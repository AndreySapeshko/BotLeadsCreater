from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def niches_keyboard(niches: list[str]) -> InlineKeyboardMarkup:
    inline_keyboard = []
    for niche in niches:
        inline_keyboard.append(
            [
                InlineKeyboardButton(text=f"{niche}", callback_data=f"niche:{niche}"),
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard)
