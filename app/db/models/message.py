from sqlalchemy import Column, Integer, String, DateTime
from db.config import Base
from datetime import datetime, timezone
from sqlalchemy import inspect
#from sqlalchemy.ext.declarative import as_declarative, declared_attr

#@as_declarative()
class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True),default=datetime.now())

    def as_dict(self) -> dict:
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs}
