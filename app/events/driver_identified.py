import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class DriverIdentified(EventProcessor):
    name = "driver_identified"
    input_streams = ["identity.bluetooth"]  # produced by drivers.identity module

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("driver_identified handle %s %s", stream, msg_id)


PROCESSOR = DriverIdentified()
