from abc import ABC, abstractmethod


class BaseLLMClient(ABC):
    client_id: str
    prompt: str

    @abstractmethod
    async def analyze(self, messages: list[dict]) -> dict:
        raise NotImplementedError
