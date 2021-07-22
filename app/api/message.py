# For FastAPI Services
from fastapi import APIRouter
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, Request, Depends
from starlette.websockets import WebSocketState
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


# For DB
import db.crud as crud
from config import engine, async_session, sessionmaker
from dependencies import get_session

# For configuration
from config import settings, RequestType, ResponseType

from utils import get_current_user

# For parsing json
import json

# For datetime and parser
import datetime
def DatetimeEncoder(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()

# Print system logs
import logging

router = APIRouter()

templates = Jinja2Templates(directory="templates")

class ConnectionManager:
    def __init__(self):
        self.active_connections_dict: Dict = {}
        self.valid_user = settings.VALID_USER_DICT

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections_dict[user_id] = websocket

    def disconnect(self, user_id: str):
        del self.active_connections_dict[user_id]

    async def send_personal_message(self, data: dict, websocket: WebSocket):
        #  logging.error(data)
        data = json.dumps(data, default=DatetimeEncoder)
        await websocket.send_json(data)

    async def broadcast(self,message: Dict):
        message = json.dumps(message, default=DatetimeEncoder)
        for connection in self.active_connections_dict:
            tmp_websocket = self.active_connections_dict[connection]
            if tmp_websocket.application_state == WebSocketState.CONNECTED \
                    and tmp_websocket.client_state == WebSocketState.CONNECTED:
                await self.active_connections_dict[connection].send_json(message)
            else:
                del self.active_connections_dict[connection]

manager = ConnectionManager()

@router.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "domain": settings.DOMAIN}
    )

@router.websocket("/ws/")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None),
):
    token = websocket.query_params['token']
    async_db_connection = async_session()
    user = await get_current_user(
        async_session=async_db_connection,
        token=token
    )
    user_id = user.id
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                data = json.loads(str(data))
                #  logging.error(data)
                if data.get('request_type') == RequestType.MESSAGE:
                    text = data.get('text')
                    message_db = await crud.create_message(
                        db_session=async_db_connection,
                        user_id=user_id,
                        text=text
                    )
                    json_message_db = message_db.as_dict()
                    json_message_db['avatar'] = user.avatar
                    message = {
                        'response_type': ResponseType.MESSAGE,
                        'data': json_message_db
                    }
                    #  message = json.dumps(message, default=DatetimeEncoder)
                    #  logging.debug(message)
                    # await manager.send_personal_message(data, websocket)
                    await manager.broadcast(message=message)
                else:
                    message_id = 1000000
                    if data.get('id'):
                        message_id = int(data.get('id'))
                    quantity = int(data.get('quantity'))
                    messages_db = await crud.get_all_messages(
                        db_session=async_db_connection,
                        greaterid=message_id,
                        quantity=quantity
                    )
                    list_data = []
                    for cell in messages_db:
                        tmp = cell.as_dict()
                        tmp['avatar'] = user.avatar
                        list_data.append(tmp)

                    data = {
                        'response_type': ResponseType.MESSAGES,
                        'data': list_data
                    }
                    await manager.send_personal_message(
                        data=data,
                        websocket=websocket
                    )
            except:
                pass

    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(f"{user_id} left the chat")
