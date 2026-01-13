import asyncio

import httpx

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; AgentLeadsBot/1.0)"}
MAX_BYTES = 500_000
TIMEOUT = 15


class HtmlFetcher:
    def __init__(self, concurrency: int = 10):
        self.sem = asyncio.Semaphore(concurrency)

    async def fetch(self, url: str) -> str:
        async with self.sem:
            async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS, follow_redirects=True) as client:
                r = await client.get(url)
                r.raise_for_status()
                return r.content[:MAX_BYTES].decode("utf-8", errors="ignore")
