from urllib.parse import urlparse

BLOCKED_HOSTS = {
    # карты/агрегаторы/справочники
    "2gis.ru",
    "www.2gis.ru",
    "yandex.ru",
    "ya.ru",
    "zoon.ru",
    "www.zoon.ru",
    "prodoctorov.ru",
    "www.prodoctorov.ru",
    "docdoc.ru",
    "www.docdoc.ru",
    "sberhealth.ru",
    "www.sberhealth.ru",
    "napopravku.ru",
    "www.napopravku.ru",
    "doctu.ru",
    "www.doctu.ru",
    # соцсети/мессенджеры
    "t.me",
    "telegram.me",
    "vk.com",
    "www.vk.com",
    "instagram.com",
    "www.instagram.com",
    "ok.ru",
    "www.ok.ru",
    "youtube.com",
    "www.youtube.com",
    "gosuslugi.ru",
}

BLOCKED_DOMAINS = ["com", "org", "edu"]


def normalize_domain(url: str) -> str | None:
    url = url.strip()
    if not url:
        return None
    if "://" not in url:
        url = "https://" + url
    p = urlparse(url)
    host = (p.netloc or "").lower()
    host = host.split("@")[-1].split(":")[0]
    host = host.rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    if not host:
        return None
    if "." not in host:
        return None
    if host in BLOCKED_HOSTS:
        return None
    if host.split(".")[-1] in BLOCKED_DOMAINS:
        return None
    return host
