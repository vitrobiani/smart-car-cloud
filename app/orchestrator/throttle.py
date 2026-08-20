import time


class Throttle:
    """Non-nanny cooldown: suppress repeat notifications of the same key within cooldown_s."""

    def __init__(self, cooldown_s: float = 30.0) -> None:
        self.cooldown_s = cooldown_s
        self._last: dict[str, float] = {}

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        last = self._last.get(key, 0.0)
        if now - last < self.cooldown_s:
            return False
        self._last[key] = now
        return True
