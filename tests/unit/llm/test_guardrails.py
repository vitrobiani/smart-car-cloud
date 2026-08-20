from app.llm.guardrails import MAX_LEN, validate


def test_trims_whitespace() -> None:
    assert validate("  hi  ") == "hi"


def test_truncates_long_output() -> None:
    long = "x" * (MAX_LEN + 100)
    assert len(validate(long)) <= MAX_LEN + 1
