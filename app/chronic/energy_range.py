import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class EnergyRange(ChronicJob):
    name = "energy_range"
    interval_s = 30.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("energy_range tick")


JOB = EnergyRange()
