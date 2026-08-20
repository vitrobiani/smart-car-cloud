import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class HarshAccel(EventProcessor):
    name = "harsh_accel"
    input_streams = ["telemetry.accelerometer", "telemetry.pedals"]

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("harsh_accel handle %s %s", stream, msg_id)


PROCESSOR = HarshAccel()
