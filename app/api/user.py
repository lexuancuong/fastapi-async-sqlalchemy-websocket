from datetime import timedelta

from config import settings
from dependencies import get_session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from utils import authenticate_user, create_access_token

router = APIRouter()


class Token(BaseModel):
    access_token: str
    user_id: int


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), async_session=Depends(get_session)
):
    user = await authenticate_user(
        async_session, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "user_id": user.id}


@router.get("/image/{filename}", response_class=FileResponse)
def get_image(filename: str):
    image_path = f"./data/{filename}"
    # in newest version up to now, you can use image path directly
    return image_path
