from app.delivery.channel import Notification


def choose(candidates: list[Notification]) -> Notification | None:
    """Pick the highest-priority notification (lowest number wins)."""
    if not candidates:
        return None
    return min(candidates, key=lambda n: n.priority)
