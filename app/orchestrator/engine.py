import asyncio
import logging

from app.core.bus import DERIVED_EVENTS_STREAM, read_stream
from app.orchestrator.context import build_snapshot
from app.orchestrator.rules import RULES
from app.orchestrator.throttle import Throttle

log = logging.getLogger(__name__)


class Engine:
    def __init__(self) -> None:
        self.throttle = Throttle()

    async def run(self) -> None:
        streams = {DERIVED_EVENTS_STREAM: ">"}
        try:
            async for stream, msg_id, fields in read_stream(streams, "orchestrator", "engine"):
                await self._handle(fields)
        except asyncio.CancelledError:
            log.info("orchestrator engine cancelled")
            raise

    async def _handle(self, fields: dict[str, str]) -> None:
        event_type = fields.get("type", "")
        trip_id = fields.get("trip_id", "")
        snapshot = await build_snapshot(trip_id)
        for rule in RULES:
            result = rule(snapshot, {"type": event_type, **fields})
            if result is None:
                continue
            key = f"{event_type}:{result.action}"
            if not self.throttle.allow(key):
                continue
            log.info("orchestrator: %s -> %s (%s)", event_type, result.action, result.message)
            # TODO: publish to delivery layer


ENGINE = Engine()


def start_engine() -> asyncio.Task:
    return asyncio.create_task(ENGINE.run(), name="orchestrator")
