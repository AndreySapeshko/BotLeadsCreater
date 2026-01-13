import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.db.crud import (
    get_or_create_user,
)
from app.db.session import AsyncSessionLocal

logger = logging.getLogger("bot")

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message):
    print("ENTER start_cmd")
    telegram_id = message.from_user.id
    username = message.from_user.username

    async with AsyncSessionLocal() as session:
        user = await get_or_create_user(
            session=session,
            telegram_id=telegram_id,
            username=username,
        )
        await session.commit()

    await message.answer(
        f"👋 Привет!\n\n"
        f"Ты успешно зарегистрирован.\n"
        f"Твой ID: {user.telegram_id}\n"
        f"Имя: {user.username}\n"
        "AgentResearcher готов. 🚀\n"
        "Пришли задачу для исследования."
    )
