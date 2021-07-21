from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from sqlalchemy import inspect
from config import BaseClass
from db.models.user import User
from sqlalchemy.orm import relationship
from db.utils import get_current_time

class Message(BaseClass):
    id = Column(Integer, index=True, primary_key=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),default=get_current_time())
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(
        User,
        uselist=False,
        primaryjoin='Message.user_id == User.id',
    )
