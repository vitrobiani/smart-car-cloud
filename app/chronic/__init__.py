from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.chronic import (
    alertness,
    comfort_temp,
    distraction,
    eco_score,
    energy_range,
    fatigue_trend,
    following_distance,
    grip_quality,
    known_places,
    speed_check,
    speed_vs_limit,
)
from app.chronic.base import ChronicContext, ChronicJob

_MODULES = [
    speed_check,
    alertness,
    grip_quality,
    following_distance,
    speed_vs_limit,
    energy_range,
    distraction,
    fatigue_trend,
    eco_score,
    comfort_temp,
    known_places,
]

CHRONIC_REGISTRY: dict[str, ChronicJob] = {m.JOB.name: m.JOB for m in _MODULES}


def register_all(scheduler: AsyncIOScheduler) -> None:
    ctx = ChronicContext()
    for job in CHRONIC_REGISTRY.values():
        scheduler.add_job(
            job.run,
            "interval",
            seconds=job.interval_s,
            id=job.name,
            replace_existing=True,
            kwargs={"ctx": ctx},
        )
