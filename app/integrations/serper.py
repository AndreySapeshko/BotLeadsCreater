import httpx


class SerperClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def search(self, q: str, num: int = 10) -> list[dict]:
        url = "https://google.serper.dev/search"
        headers = {"X-API-KEY": self.api_key}
        payload = {"q": q, "num": num}

        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()

        organic = data.get("organic") or []
        return organic
