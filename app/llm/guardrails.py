MAX_LEN = 400


def validate(text: str) -> str:
    """Enforce length + basic tone guardrails. Return the sanitized text."""
    text = text.strip()
    if len(text) > MAX_LEN:
        text = text[:MAX_LEN].rstrip() + "…"
    return text
