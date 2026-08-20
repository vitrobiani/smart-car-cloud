import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class EcoScore(ChronicJob):
    name = "eco_score"
    interval_s = 10.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("eco_score tick")


JOB = EcoScore()
