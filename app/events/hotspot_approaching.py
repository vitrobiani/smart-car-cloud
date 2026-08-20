import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class HotspotApproaching(EventProcessor):
    name = "hotspot_approaching"
    input_streams = ["telemetry.vehicle.speed"]  # location proxy for now

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("hotspot_approaching handle %s %s", stream, msg_id)


PROCESSOR = HotspotApproaching()
