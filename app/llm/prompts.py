LLM_PROMPT = """
You analyze a clinic website based on technical signals.

Your task:
1. Infer what problem this clinic likely has with handling client requests.
2. Propose a realistic automation opportunity.
3. Write a short first-contact message (pitch) that sounds helpful, not salesy.

Rules:
- Do not invent facts.
- Use only the provided signals.
- Keep pitch under 500 characters.
- Tone: professional, friendly, non-pushy.
- Output only valid JSON.

Return exactly:
{
  "problem": "...",
  "opportunity": "...",
  "pitch": "..."
}
"""
