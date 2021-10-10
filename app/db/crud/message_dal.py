from typing import List

from db.models.message import Message
from db.utils import get_current_time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def create_message(db_session: AsyncSession, user_id: int, text: str):
    new_message = Message(user_id=user_id, text=text, created_at=get_current_time())
    db_session.add(new_message)
    await db_session.commit()
    await db_session.flush()
    return new_message


async def get_all_messages(
    db_session: AsyncSession,
    greaterid: int,
    quantity: int,
) -> List[Message]:
    result = await db_session.execute(
        select(Message).where(Message.id < greaterid).order_by(Message.id.desc())
    )
    return result.scalars().all()[:quantity]
