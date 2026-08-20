from app.llm import prompts
from app.llm.client import client
from app.llm.guardrails import validate


async def summarize(events_desc: str) -> str:
    prompt = prompts.get("summary.default", events=events_desc)
    raw = await client.complete(prompt)
    return validate(raw)
