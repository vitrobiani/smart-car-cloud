import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class GripQuality(ChronicJob):
    name = "grip_quality"
    interval_s = 2.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("grip_quality tick")


JOB = GripQuality()
