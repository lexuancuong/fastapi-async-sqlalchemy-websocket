from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

# For DB
import db.crud as crud
from db.config import engine, Base, async_session, sessionmaker, settings

# For parsing json
import datetime
import json
def DatetimeEncoder(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    # create db tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

class ConnectionManager:
    def __init__(self):
        self.active_connections_dict: Dict = {}
        self.valid_user = settings.VALID_USER_DICT

    def get_valid_username(self, token):
        if token in self.valid_user:
            return self.valid_user.get(token)
        return None

    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections_dict[username] = websocket

    def disconnect(self, username: str):
        del self.active_connections_dict[username]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self,message: Dict):
        message = json.dumps(message, default=DatetimeEncoder),
        for connection in self.active_connections_dict:
            await self.active_connections_dict[connection].send_json(message)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


import logging
@app.websocket("/ws/")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None),
):
    logging.debug(token)
    print(token)
    token = websocket.query_params['token']
    username = manager.get_valid_username(token)
    if username is None:
        raise HTTPException(status_code=404, detail="User not found.")
    await manager.connect(websocket, username)
    async_db_connection = async_session()
    try:
        while True:
            data = await websocket.receive_text()
            message_db = await crud.create_message(
                db_session=async_db_connection,
                username=username,
                message=data
            )
            json_data = message_db.as_dict()
            # await manager.send_personal_message(data, websocket)
            await manager.broadcast(message=json_data)
    except WebSocketDisconnect:
        manager.disconnect(username)
        await manager.broadcast(f"{username} left the chat")
