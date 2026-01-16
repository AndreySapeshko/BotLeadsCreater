from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def contacted_keyboard(user_domain_id: str, domain: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="❌ Игнорировать", callback_data=f"ignored:{user_domain_id}:{domain}"),
            ],
        ]
    )
