import json
import logging

from app.llm.prompts import LLM_PROMPT

logger = logging.getLogger(__name__)


class LLMStage:
    def __init__(self, llm_client):
        self.llm = llm_client

    async def enrich(self, signals_list: list[dict]) -> list[dict]:
        enriched = []

        for s in signals_list:
            payload = json.dumps(s, ensure_ascii=False, indent=2)

            prompt = f"{LLM_PROMPT}\n\nInput JSON:\n{payload}"

            messages = [
                {"role": "system", "content": "You are a B2B automation consultant."},
                {"role": "user", "content": prompt},
            ]

            try:
                resp = await self.llm.analyze(messages)
            except Exception as e:
                logger.info(f"Exception in llm.analyse: {e}")
                resp = None

            # resp уже JSON
            if resp:
                s["problem"] = resp.get("problem")
                s["opportunity"] = resp.get("opportunity")
                s["pitch"] = resp.get("pitch")

            enriched.append(s)

        return enriched
