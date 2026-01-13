import json

from app.llm.prompts import LLM_PROMPT


class LLMStage:
    def __init__(self, llm_client):
        self.llm = llm_client

    async def enrich(self, signals_list: list[dict]) -> list[dict]:
        enriched = []

        for s in signals_list:
            payload = json.dumps(s, ensure_ascii=False)

            prompt = LLM_PROMPT.format(signals=payload)

            messages = [
                {"role": "system", "content": "You are a B2B automation consultant."},
                {"role": "user", "content": prompt},
            ]

            try:
                resp = await self.llm.analyze(messages)
            except Exception:
                continue

            # resp уже JSON
            s["problem"] = resp.get("problem")
            s["opportunity"] = resp.get("opportunity")
            s["pitch"] = resp.get("pitch")

            enriched.append(s)

        return enriched
