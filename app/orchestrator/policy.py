def prompt_for(persona: str | None, use: str) -> str:
    """Return the prompt template name for (persona, use). LLM layer resolves it."""
    return f"{(persona or 'new').lower()}.{use}"
