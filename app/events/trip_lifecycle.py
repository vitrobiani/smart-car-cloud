import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class TripLifecycle(EventProcessor):
    name = "trip_lifecycle"
    input_streams = ["telemetry.vehicle.gears", "telemetry.vehicle.parking_brake"]

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("trip_lifecycle handle %s %s", stream, msg_id)


PROCESSOR = TripLifecycle()
