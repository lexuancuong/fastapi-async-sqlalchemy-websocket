from sqlalchemy import Column, Integer, String, DateTime
from config import BaseClass
from datetime import datetime
from sqlalchemy import inspect

class User(BaseClass):
    id = Column(Integer, index=True, primary_key=True)
    username = Column(String, nullable=True)
    avatar = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
