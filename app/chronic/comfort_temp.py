import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class ComfortTemp(ChronicJob):
    name = "comfort_temp"
    interval_s = 60.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("comfort_temp tick")


JOB = ComfortTemp()
