from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from config import settings, engine, BaseClass, initial_users
from api.api import api_router
from db.crud import create_user
from utils import get_password_hash

app = FastAPI()

# Use Alembic for production
@app.on_event("startup")
async def startup():
    # create db tables
    if settings.DEV:
        async with engine.begin() as conn:
            await conn.run_sync(BaseClass.metadata.drop_all)
            await conn.run_sync(BaseClass.metadata.create_all)
        from config import async_session
        async with async_session() as session:
            for element in initial_users:
                await create_user(
                    db_session=session,
                    username=element.get('username'),
                    hased_password=get_password_hash(element.get('password'))
                )

# Less security! Dont use this for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=['Content-Disposition'],
)

app.include_router(api_router)

