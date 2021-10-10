from config import BaseClass
from db.models.user import User
from db.utils import get_current_time
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Message(BaseClass):
    id = Column(Integer, index=True, primary_key=True)
    text = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=get_current_time())
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(
        User,
        uselist=False,
        primaryjoin="Message.user_id == User.id",
    )
