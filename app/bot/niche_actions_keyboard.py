from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def niche_actions_keyboard(niche: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🚀 Запустить", callback_data=f"run:{niche}"),
                InlineKeyboardButton(text="✏️ Изменить", callback_data=f"edit:{niche}"),
            ],
            [
                InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete{niche}"),
            ],
        ]
    )
