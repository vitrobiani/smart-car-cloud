from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ChronicContext:
    """Passed to every chronic job. Extend with DB/Redis handles as jobs need them."""

    trip_id: str | None = None


class ChronicJob(ABC):
    """Periodic processor. Scheduler calls `run(ctx)` every `interval_s` seconds."""

    name: str
    interval_s: float

    @abstractmethod
    async def run(self, ctx: ChronicContext) -> None: ...
