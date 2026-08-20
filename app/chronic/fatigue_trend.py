import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class FatigueTrend(ChronicJob):
    name = "fatigue_trend"
    interval_s = 30.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("fatigue_trend tick")


JOB = FatigueTrend()
