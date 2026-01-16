from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def lead_keyboard(user_domain_id: str, domain: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📩 Связался", callback_data=f"contacted:{user_domain_id}:{domain}"),
                InlineKeyboardButton(text="❌ Игнорировать", callback_data=f"ignored:{user_domain_id}:{domain}"),
            ],
        ]
    )
