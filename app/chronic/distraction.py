import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class Distraction(ChronicJob):
    name = "distraction"
    interval_s = 5.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("distraction tick")


JOB = Distraction()
