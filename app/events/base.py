from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EventContext:
    trip_id: str | None = None


class EventProcessor(ABC):
    """Consumes one or more telemetry streams and emits derived events."""

    name: str
    input_streams: list[str]
    group: str = "events"

    @abstractmethod
    async def handle(
        self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext
    ) -> None: ...
