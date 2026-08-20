import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class LlmFailure(EventProcessor):
    name = "llm_failure"
    input_streams = ["llm.failures"]  # emitted by llm/client.py on error

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("llm_failure handle %s %s", stream, msg_id)


PROCESSOR = LlmFailure()
