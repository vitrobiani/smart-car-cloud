import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class KnownPlaces(ChronicJob):
    name = "known_places"
    interval_s = 15.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("known_places tick")


JOB = KnownPlaces()
