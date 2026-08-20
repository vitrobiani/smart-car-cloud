import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class SpeedThreshold(EventProcessor):
    name = "speed_threshold"
    input_streams = ["telemetry.vehicle.speed"]

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("speed_threshold handle %s %s", stream, msg_id)


PROCESSOR = SpeedThreshold()
