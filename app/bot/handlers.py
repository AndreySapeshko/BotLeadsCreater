import logging

from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot.contacted_keyboard import contacted_keyboard
from app.bot.lead_keyboard import lead_keyboard
from app.bot.niche_actions_keyboard import niche_actions_keyboard
from app.bot.niches_keyboard import niches_keyboard
from app.db.crud import (
    get_or_create_user,
    get_user_by_telegram_id,
)
from app.db.session import AsyncSessionLocal
from app.repositories.query_repo import query_repo
from app.repositories.user_domain_repo import user_domain_repo

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message):
    logger.info(f"ENTER start_cmd from: {message.from_user.id}")
    print("ENTER start_cmd")
    telegram_id = message.from_user.id
    username = message.from_user.username

    user = await get_or_create_user(telegram_id=telegram_id, username=username)

    if user:
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

    await message.answer("Ошибка при регистрации, обратитесь к разработчику.")
    return user


@router.message(Command("niches"))
async def niches_cmd(message: Message, state: FSMContext):
    logger.info(f"ENTER niches_cmd from: {message.from_user.id}")
    print(f"ENTER niches_cmd from: {message.from_user.id}")
    user = await get_user_by_telegram_id(message.from_user.id)
    niches = await query_repo.list_business_types(user.id)

    if not niches:
        await message.answer("У тебя пока нет ниш. Напиши название новой ниши:")
        await state.set_state("waiting_new_niche")
        return

    await message.answer("Выбери нишу:", reply_markup=niches_keyboard(niches))


@router.callback_query(F.data.startswith("niche:"))
async def select_niche(cb: CallbackQuery, state):
    logger.info(f"ENTER callback select_niche from: {cb.from_user.id}")
    print(f"ENTER callback select_niche from: {cb.from_user.id}")
    niche = cb.data.split(":")[1]
    await state.update_data(niche=niche)

    user = await get_user_by_telegram_id(cb.from_user.id)
    queries = await query_repo.list_queries_by_type(user.id, niche)

    text = f"Ниша: {niche}\n поисковые запросы:\n"
    for query in queries:
        text += f"  - {query}\n"

    await cb.message.answer(text, reply_markup=niche_actions_keyboard(niche))
    await cb.answer()


@router.message(StateFilter("waiting_new_niche"))
async def create_niche(message, state):
    logger.info(f"ENTER create_niche from: {message.from_user.id}")
    print(f"ENTER create_niche from: {message.from_user.id}")
    niche = message.text.strip().lower()

    await state.update_data(business_type=niche)

    await message.answer(
        f"Ниша '{niche}' создана.\n"
        "Теперь введи первый поисковый запрос.\n"
        "Например: стоматология записаться\n"
        "Можно ввести несколько запросов через запятую."
    )
    await state.set_state("waiting_new_query")


@router.message(StateFilter("waiting_new_query"))
async def add_queries(message, state):
    logger.info(f"ENTER add_queries from: {message.from_user.id}")
    print(f"ENTER add_queries from: {message.from_user.id}")
    data = await state.get_data()
    niche = data["business_type"]
    phrases = message.text.split(",")

    user = await get_user_by_telegram_id(message.from_user.id)
    await query_repo.add_queries_from_list(user.id, niche, phrases)

    await message.answer(
        f"Запрос добавлен в нишу {niche}.\n" "Можешь изменить, удалить или 🚀 Запустить поиск.",
        reply_markup=niche_actions_keyboard(niche),
    )

    await state.clear()


@router.callback_query(F.data.startswith("edit:"))
async def edit_niche(cb: CallbackQuery, state: FSMContext):
    print(f"ENTER callback edit_niche from: {cb.from_user.id}")
    niche = cb.data.split(":")[1]
    await state.update_data(business_type=niche)

    await cb.message.answer(
        "Для удаления запроса перед ним укажите знак минус.\n"
        "Что бы добавить запрос введите слово или фразу.\n"
        "Можно указать несколько запросов через запятую.\n"
        "Пример удалить: -удаляемый_запрос_1, -удаляемый_запрос_2\n"
        "Пример добавить: новый запрос_1, новый запрос 2"
    )
    await state.set_state("waiting_edit_queries")


@router.message(StateFilter("waiting_edit_queries"))
async def edit_queries_to_niche(message, state):
    logger.info(f"ENTER edit_queries_to_niche from: {message.from_user.id}")
    print(f"ENTER edit_queries_to_niche from: {message.from_user.id}")
    data = await state.get_data()
    niche = data["business_type"]
    phrases = message.text.split(",")

    removed_phrases = []
    added_phrases = []
    for phrase in phrases:
        phrase = phrase.strip()
        if phrase[0] == "-":
            removed_phrases.append(phrase[1:].strip())
        else:
            added_phrases.append(phrase)

    user = await get_user_by_telegram_id(message.from_user.id)

    if added_phrases:
        await query_repo.add_queries_from_list(user.id, niche, added_phrases)
        text = "Добавлены поисковые запросы:\n"
        for phrase in added_phrases:
            text += f"  - {phrase}\n"
        await message.answer(text)

    if removed_phrases:
        non_existent_phrases = await query_repo.delete_queries(user.id, niche, removed_phrases)
        if non_existent_phrases:
            text = "Таких запросов нет:\n"
            for phrase in non_existent_phrases:
                text += f"  - {phrase}\n"
            await message.answer(text)
        else:
            text = "Удалены запросы:\n"
            for phrase in removed_phrases:
                text += f"  - {phrase}\n"
            await message.answer(text)

    await message.answer(
        f"Изменены запросы в нише {niche}.\n" "Можешь изменить, удалить или 🚀 Запустить поиск.",
        reply_markup=niche_actions_keyboard(niche),
    )

    await state.clear()


@router.callback_query(F.data.startswith("delete:"))
async def delete_niche(cb: CallbackQuery):
    print(f"ENTER callback delete_niche from: {cb.from_user.id}")
    niche = cb.data.split(":")[1]

    user = await get_user_by_telegram_id(cb.from_user.id)
    is_successfully = await query_repo.delete_niche(user.id, niche)

    if is_successfully:
        await cb.message.answer(f"Ниша {niche} удалена.")
    else:
        await cb.message.answer(f"Ниша {niche} не найдена.")
    await cb.answer()


@router.callback_query(F.data.startswith("run:"))
async def run_niche(cb: CallbackQuery):
    print(f"ENTER callback RUN_niche from: {cb.from_user.id}")
    niche = cb.data.split(":")[1]
    await cb.answer("⏳ Обрабатываю...", show_alert=False)
    from app.bot.bot import pipeline

    user = await get_user_by_telegram_id(cb.from_user.id)
    async with AsyncSessionLocal() as session:
        result = await pipeline.run(session=session, user_id=user.id, business_type=niche)

    await cb.message.answer(
        f"Ниша {niche}\n"
        f"Сайтов найдено: {result['found_domains']}\n"
        f"Новых: {result['new_domains']}\n"
        f"Лидов: {result['leads']}\n\n"
        "Команда: /leads"
    )


@router.message(Command("leads"))
async def leads_cmd(message: Message):
    logger.info(f"ENTER leads_cmd from: {message.from_user.id}")
    print(f"ENTER niches_cmd from: {message.from_user.id}")
    user = await get_user_by_telegram_id(message.from_user.id)

    async with AsyncSessionLocal() as session:
        leads = await user_domain_repo.get_leads_by_user(session, user.id)

    if leads:
        for lead in leads:
            domain = lead.get("domain")
            user_domain_id = lead.get("user_domain_id")
            text = f"Найден lead:\n  - {domain}\n"
            await message.answer(text, reply_markup=lead_keyboard(user_domain_id, domain))
    else:
        await message.answer("leads не найдены.")


@router.callback_query(F.data.startswith("contacted:"))
async def contacted_domain(cb: CallbackQuery):
    print(f"ENTER callback contacted_domain from: {cb.from_user.id}")
    status, user_domain_id, domain = cb.data.split(":")

    async with AsyncSessionLocal() as session:
        is_successfully = await user_domain_repo.set_status(session, int(user_domain_id), status)
        if is_successfully:
            await cb.message.answer(f"Lead {domain} изменен статус на {status}")
        else:
            await cb.message.answer(f"Не удалось изменить статус.\nLead {domain} или статус {status} не найден.")
    await cb.answer()


@router.callback_query(F.data.startswith("ignored:"))
async def ignored_domain(cb: CallbackQuery):
    print(f"ENTER callback ignored_domain from: {cb.from_user.id}")
    status, user_domain_id, domain = cb.data.split(":")

    async with AsyncSessionLocal() as session:
        is_successfully = await user_domain_repo.set_status(session, int(user_domain_id), status)
        if is_successfully:
            await cb.message.answer(f"Lead {domain} изменен статус на {status}")
        else:
            await cb.message.answer(f"Не удалось изменить статус.\nLead {domain} или статус {status} не найден.")
    await cb.answer()


@router.message(Command("contact"))
async def contact_cmd(message: Message):
    logger.info(f"ENTER contact_cmd from: {message.from_user.id}")
    print(f"ENTER contact_cmd from: {message.from_user.id}")
    user = await get_user_by_telegram_id(message.from_user.id)

    async with AsyncSessionLocal() as session:
        leads = await user_domain_repo.get_contacted_leads_by_user(session, user.id)

    if leads:
        for lead in leads:
            domain = lead.get("domain")
            user_domain_id = lead.get("user_domain_id")
            text = f"Предложение отправлено lead:\n  - {domain}\n"
            await message.answer(text, reply_markup=contacted_keyboard(user_domain_id, domain))
    else:
        await message.answer("leads не найдены.")
