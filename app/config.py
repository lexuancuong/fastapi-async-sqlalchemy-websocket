from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from pydantic import BaseSettings
import enum

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    DEV: bool = True
    VALID_USER_DICT: dict = {
        "sa": "username1",
        "sb": "username2",
    }
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    USERNAME1: str
    PASSWORD1: str
    USERNAME2: str
    PASSWORD2: str

    DOMAIN: str

settings = Settings()

class RequestType(enum.IntEnum):
    MESSAGE = 1
    REQUEST = 2

class ResponseType(enum.IntEnum):
    MESSAGE = 1
    MESSAGES = 2
    NOTI = 3


initial_users = [
    {
        "username": settings.USERNAME1,
        "password": settings.PASSWORD1
    },
    {
        "username": settings.USERNAME2,
        "password": settings.PASSWORD2
    }
]

DATABASE_URL = f'postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}'

engine = create_async_engine(DATABASE_URL, future=True, echo=True)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

from sqlalchemy.ext.declarative import as_declarative, declared_attr
from sqlalchemy import inspect
@as_declarative()
class BaseClass:
    id: int
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def as_dict(self) -> dict:
        return {
            c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs
        }
