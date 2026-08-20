import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class Alertness(ChronicJob):
    name = "alertness"
    interval_s = 5.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("alertness tick")


JOB = Alertness()
