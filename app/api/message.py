# For FastAPI Services
from fastapi import APIRouter
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# For DB
import db.crud as crud
from config import engine, async_session, sessionmaker
from dependencies import get_session

# For configuration
from config import settings, SignalType

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

    async def send_personal_message(self, data: list, websocket: WebSocket):
        data = json.dumps(data, default=DatetimeEncoder),
        await websocket.send_json(data)

    async def broadcast(self,message: Dict):
        message = json.dumps(message, default=DatetimeEncoder),
        for connection in self.active_connections_dict:
            await self.active_connections_dict[connection].send_json(message)

manager = ConnectionManager()

@router.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
            data = json.loads(str(data))
            if data.get('signal_type') == SignalType.MESSAGE:
                text = data.get('text')
                message_db = await crud.create_message(
                    db_session=async_db_connection,
                    user_id=user_id,
                    text=text
                )
                json_data = message_db.as_dict()
                # await manager.send_personal_message(data, websocket)
                await manager.broadcast(message=json_data)
            else:
                message_id = int(data.get('id'))
                quantity = int(data.get('quantity'))
                messages_db = await crud.get_all_messages(
                    db_session=async_db_connection,
                    greaterid=message_id,
                    quantity=quantity
                )
                json_data = []
                for cell in messages_db:
                    json_data.append(cell.as_dict())
                await manager.send_personal_message(
                    data=json_data,
                    websocket=websocket
                )
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        await manager.broadcast(f"{user_id} left the chat")
