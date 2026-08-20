import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class AlertnessDrop(EventProcessor):
    name = "alertness_drop"
    input_streams = ["events.derived"]  # reacts to alertness score from chronic

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("alertness_drop handle %s %s", stream, msg_id)


PROCESSOR = AlertnessDrop()
