import time

from app.orchestrator.throttle import Throttle


def test_throttle_blocks_repeats_within_cooldown() -> None:
    t = Throttle(cooldown_s=60.0)
    assert t.allow("x") is True
    assert t.allow("x") is False


def test_throttle_allows_after_cooldown() -> None:
    t = Throttle(cooldown_s=0.01)
    assert t.allow("x") is True
    time.sleep(0.02)
    assert t.allow("x") is True
