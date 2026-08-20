import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class Geofence(EventProcessor):
    name = "geofence"
    input_streams = ["telemetry.vehicle.speed"]  # positional data source once GPS sensor lands

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("geofence handle %s %s", stream, msg_id)


PROCESSOR = Geofence()
