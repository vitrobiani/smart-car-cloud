from app.llm import prompts
from app.llm.client import client
from app.llm.guardrails import validate


async def generate(context_desc: str) -> str:
    prompt = prompts.get("tips.default", context=context_desc)
    raw = await client.complete(prompt)
    return validate(raw)
