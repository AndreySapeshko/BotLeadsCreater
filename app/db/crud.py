from sqlalchemy import select

from app.db.models import User
from app.db.session import AsyncSessionLocal


async def get_or_create_user(telegram_id: int, username: str | None) -> User:
    async with AsyncSessionLocal() as session:
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
        await session.commit()

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        user = (await session.scalars(stmt)).one_or_none()

    return user


async def get_user_by_telegram_id(telegram_id: int):
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.telegram_id == telegram_id)
        return (await session.scalars(stmt)).one_or_none()
