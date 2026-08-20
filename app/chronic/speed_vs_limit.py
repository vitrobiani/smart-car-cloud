import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class SpeedVsLimit(ChronicJob):
    name = "speed_vs_limit"
    interval_s = 1.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("speed_vs_limit tick")


JOB = SpeedVsLimit()
