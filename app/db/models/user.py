from config import BaseClass
from sqlalchemy import Column, Integer, String


class User(BaseClass):
    id = Column(Integer, index=True, primary_key=True)
    username = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
