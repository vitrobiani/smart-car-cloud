from app.delivery.channel import Notification
from app.delivery.priority import choose


def test_lowest_number_wins() -> None:
    a = Notification(trip_id="t", channel="c", message="a", priority=5)
    b = Notification(trip_id="t", channel="c", message="b", priority=1)
    assert choose([a, b]) is b


def test_empty_returns_none() -> None:
    assert choose([]) is None
