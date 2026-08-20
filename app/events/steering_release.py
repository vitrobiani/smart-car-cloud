import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class SteeringRelease(EventProcessor):
    name = "steering_release"
    input_streams = ["telemetry.rotation", "telemetry.pedals"]

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("steering_release handle %s %s", stream, msg_id)


PROCESSOR = SteeringRelease()
