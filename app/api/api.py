from fastapi import APIRouter
from . import message, user
api_router = APIRouter()
api_router.include_router(user.router, tags=["user"])

api_router.include_router(message.router, prefix="/message", tags=["message"])
