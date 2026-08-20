import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class HarshBrake(EventProcessor):
    name = "harsh_brake"
    input_streams = ["telemetry.accelerometer", "telemetry.pedals"]

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("harsh_brake handle %s %s", stream, msg_id)


PROCESSOR = HarshBrake()
