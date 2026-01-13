import re

CHAT_MARKERS = ["jivo", "chatra", "livechat", "bitrix", "callback", "carrotquest", "amo", "amocrm"]


def extract_signals(domain: str, html: str) -> dict:
    h = html.lower()

    has_form = "<form" in h
    has_telegram = bool(re.search(r"t\.me/|telegram", h))
    has_chat = any(m in h for m in CHAT_MARKERS)

    has_booking_words = any(w in h for w in ["онлайн-запись", "онлайн запись", "записаться", "appointment", "book"])

    return {
        "domain": domain,
        "has_form": has_form,
        "has_telegram": has_telegram,
        "has_chat": has_chat,
        "has_booking_words": has_booking_words,
    }
