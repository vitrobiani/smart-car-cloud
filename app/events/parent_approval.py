import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class ParentApproval(EventProcessor):
    name = "parent_approval"
    input_streams = ["delivery.approval"]  # emitted by delivery/approval.py

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("parent_approval handle %s %s", stream, msg_id)


PROCESSOR = ParentApproval()
