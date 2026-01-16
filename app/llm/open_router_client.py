import asyncio
import json
import time

import openai
from openai import AsyncOpenAI

from app.config import OPEN_ROUTER_KEY, OPEN_ROUTER_URL
from app.llm.base_client import BaseLLMClient

client = AsyncOpenAI(api_key=OPEN_ROUTER_KEY, base_url=OPEN_ROUTER_URL)


class OpenRouterLLMClient(BaseLLMClient):
    client_id = "open_router"

    def __init__(
        self,
        client: AsyncOpenAI,
        models: list[str] = ["mistralai/mistral-small-3.1-24b-instruct:free", "deepseek/deepseek-r1-0528:free"],
        min_interval: float = 31.0,
        retries_per_model: int = 2,
    ):
        self.client = client
        self.models = models
        self.model = ""
        self.min_interval = min_interval
        self._last_call = 0
        self._lock = asyncio.Lock()
        self.retries_per_model = retries_per_model

    async def _throttled(self):
        async with self._lock:
            now = time.time()
            delta = now - self._last_call

            if delta < self.min_interval:
                await asyncio.sleep(self.min_interval - delta)

            self._last_call = time.time()

    async def analyze(self, messages: list[dict]) -> dict:
        for model in self.models:
            self.model = model
            for attempt in range(self.retries_per_model):
                await self._throttled()
                try:
                    resp = await self.client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=150,
                        temperature=0,
                        response_format={"type": "json_object"},
                    )

                    return json.loads(resp.choices[0].message.content)

                except openai.RateLimitError:
                    await asyncio.sleep(31)
                    break

                except Exception:
                    break

                except json.JSONDecodeError:
                    # модель ответила, но формат битый — пробуем ещё раз
                    continue

        raise RuntimeError("All models failed")


def get_open_router_client() -> OpenRouterLLMClient:
    return OpenRouterLLMClient(client)
