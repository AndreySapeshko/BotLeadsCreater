from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def niches_keyboard(niches: list[str]) -> InlineKeyboardMarkup:
    inline_keyboard = []
    for niche in niches:
        if len(niche) > 30:
            niche = niche[:30]
        inline_keyboard.append(
            [
                InlineKeyboardButton(text=f"{niche}", callback_data=f"niche:{niche}"),
            ]
        )
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
