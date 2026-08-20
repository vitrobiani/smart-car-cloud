import logging

from app.chronic.base import ChronicContext, ChronicJob

log = logging.getLogger(__name__)


class FollowingDistance(ChronicJob):
    name = "following_distance"
    interval_s = 1.0

    async def run(self, ctx: ChronicContext) -> None:
        log.debug("following_distance tick")


JOB = FollowingDistance()
