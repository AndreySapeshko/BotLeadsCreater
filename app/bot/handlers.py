import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message

from app.bot.bot import query_repo
from app.bot.niche_actions_keyboard import niche_actions_keyboard
from app.bot.niches_keyboard import niches_keyboard
from app.db.crud import (
    get_or_create_user,
    get_user_by_telegram_id,
)
from app.db.session import get_session

logger = logging.getLogger("bot")

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message):
    print("ENTER start_cmd")
    telegram_id = message.from_user.id
    username = message.from_user.username

    async with get_session() as session:
        user = await get_or_create_user(session=session, telegram_id=telegram_id, username=username)
        await session.commit()

    await message.answer(
        "👋 Привет!\n\n"
        "Я нахожу бизнесы которым нужна автоматизация.\n"
        "Откройте список ниш /niches.\n"
        "В нише выбрать изменить или запустить или удалить.\n"
        "По кнопке запустить начнется поиск. 🚀\n"
        "Изменить значит добавить или удалить запрос из ниши.\n"
        "Кнопка удалить нишу со всеми запросами."
    )
    return user.id


@router.message(Command("niches"))
async def niches_cmd(message: Message, state: FSMContext):
    async with get_session() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        niches = await query_repo.list_business_types(user.id)

    if not niches:
        await message.answer("У тебя пока нет ниш. Напиши название новой ниши:")
        await state.set_state("waiting_niche_name")
        return

    await message.answer("Выбери нишу:", reply_markup=niches_keyboard(niches))


@router.callback_query(F.data.startswith("niche:"))
async def select_niche(cb: CallbackQuery, state):
    niche = cb.data.split(":")[1]
    await state.update_data(niche=niche)

    async with get_session() as session:
        user = await get_user_by_telegram_id(session, cb.from_user.id)
        queries = await query_repo.list_queries_by_type(user.id, niche)
        await session.commit()

    text = f"Ниша: {niche}\n поисковые запросы:\n"
    for query in queries:
        text += f"  - {query}\n"

    await cb.message.answer(text, reply_markup=niche_actions_keyboard(niche))


@router.message(State("waiting_new_niche"))
async def create_niche(message, state):
    niche = message.text.strip().lower()

    await state.update_data(business_type=niche)

    await message.answer(
        f"Ниша '{niche}' создана.\n"
        "Теперь введи первый поисковый запрос.\n"
        "Например: стоматология записаться\n"
        "Можно ввести несколько запросов через запятую."
    )
    await state.set_state("waiting_new_query")


@router.message(State("waiting_new_query"))
async def add_first_query(message, state):
    data = await state.get_data()
    niche = data["business_type"]
    phrases = message.text.split(",")

    async with get_session() as session:
        user = await get_user_by_telegram_id(session, message.from_user.id)
        await query_repo.add_queries_from_list(user.id, niche, phrases)
        await session.commit()

    await message.answer(
        f"Запрос добавлен в нишу {niche}.\n" "Можешь добавить ещё запрос или нажать 🚀 Запустить.",
        reply_markup=niche_actions_keyboard(niche),
    )

    await state.clear()
