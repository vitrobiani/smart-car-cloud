import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class Obstacle(EventProcessor):
    name = "obstacle"
    input_streams = ["telemetry.env.surroundings", "telemetry.vehicle.adas"]

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("obstacle handle %s %s", stream, msg_id)


PROCESSOR = Obstacle()
