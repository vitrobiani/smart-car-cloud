from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Notification:
    trip_id: str
    channel: str
    message: str
    priority: int = 5


class Channel(ABC):
    name: str

    @abstractmethod
    async def send(self, notification: Notification) -> None: ...


class DashboardChannel(Channel):
    name = "dashboard"

    def __init__(self) -> None:
        self._queues: dict[str, list[Notification]] = {}

    async def send(self, notification: Notification) -> None:
        self._queues.setdefault(notification.trip_id, []).append(notification)

    def drain(self, trip_id: str) -> list[Notification]:
        return self._queues.pop(trip_id, [])


class TtsChannel(Channel):
    """Phase 2: prints TTS strings to logs."""

    name = "tts"

    async def send(self, notification: Notification) -> None:
        import logging

        logging.getLogger(__name__).info("TTS[%s]: %s", notification.trip_id, notification.message)


dashboard = DashboardChannel()
tts = TtsChannel()
