from typing import List, Optional
from sqlalchemy import update
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.message import Message

async def create_message(db_session: AsyncSession, username: str, message: str):
    new_message = Message(username=username,message=message)
    db_session.add(new_message)
    await db_session.commit()
    await db_session.flush()
    return new_message

async def get_all_messages(db_session: AsyncSession) -> List[Message]:
    q = await db_session.execute(select(Message).order_by(Message.id))
    return q.scalars().all()

