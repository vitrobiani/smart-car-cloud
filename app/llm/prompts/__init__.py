PROMPTS: dict[str, str] = {
    "chatbot.default": "You are a friendly car assistant. Reply concisely: {q}",
    "tips.default": "Given context {context}, give one short driving tip.",
    "summary.default": "Summarize this trip in 2 sentences: {events}",
    "coaching.new": "You are a driving mentor for a new driver. Encourage: {situation}",
    "coaching.sport": "You are a race coach. Give one crisp tip: {situation}",
    "coaching.eco": "You are an eco-driving coach. Suggest one saving: {situation}",
    "coaching.experienced": "You are a co-pilot to an experienced driver: {situation}",
}


def get(name: str, **kwargs: str) -> str:
    template = PROMPTS.get(name, PROMPTS["chatbot.default"])
    return template.format(**kwargs)
