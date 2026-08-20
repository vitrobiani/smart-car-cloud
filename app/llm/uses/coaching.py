from app.llm import prompts
from app.llm.client import client
from app.llm.guardrails import validate

# persona strings — carbrain.drivers.persona is free text.
# Keep in sync with the values the drivers-persona classifier writes.
_PROMPT_BY_PERSONA: dict[str, str] = {
    "NEW": "coaching.new",
    "SPORT": "coaching.sport",
    "ECO": "coaching.eco",
    "EXPERIENCED": "coaching.experienced",
}


async def coach(persona: str | None, situation: str) -> str:
    key = _PROMPT_BY_PERSONA.get((persona or "NEW").upper(), "coaching.new")
    prompt = prompts.get(key, situation=situation)
    raw = await client.complete(prompt)
    return validate(raw)
