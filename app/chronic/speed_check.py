import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class SpeedCheck(ChronicJob):
    name = "speed_check"
    interval_s = 1.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("speed_check tick")


JOB = SpeedCheck()
