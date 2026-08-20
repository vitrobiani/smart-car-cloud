from app.llm import prompts
from app.llm.client import client
from app.llm.guardrails import validate


async def reply(question: str) -> str:
    prompt = prompts.get("chatbot.default", q=question)
    raw = await client.complete(prompt)
    return validate(raw)
