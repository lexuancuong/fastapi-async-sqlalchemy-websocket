from db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def create_user(
    db_session: AsyncSession, username: str, hased_password: str, avatar: str
):
    new_user = User(username=username, hashed_password=hased_password, avatar=avatar)
    db_session.add(new_user)
    await db_session.commit()
    await db_session.flush()
    return new_user


async def get_user_by_username(db_session: AsyncSession, username: str) -> User:
    result = await db_session.execute(select(User).where(User.username == username))
    return result.scalars().first()
