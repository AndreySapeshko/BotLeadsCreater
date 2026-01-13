from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
) -> User:
    stmt = select(User).where(User.telegram_id == telegram_id)
    user = (await session.scalars(stmt)).one_or_none()

    if user:
        # обновляем username, если изменился
        if user.username != username:
            user.username = username
        return user

    # создаём нового пользователя
    user = User(
        telegram_id=telegram_id,
        username=username,
    )
    session.add(user)
    await session.flush()

    return user


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int):
    stmt = select(User).where(User.telegram_id == telegram_id)
    return (await session.scalars(stmt)).one_or_none()
