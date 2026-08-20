import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.exceptions import RedisError

from app.chronic import register_all as register_chronic
from app.core.logging import configure_logging
from app.core.redis import close_redis, get_redis
from app.core.scheduler import get_scheduler, shutdown_scheduler
from app.events import start_consumers as start_event_consumers
from app.llm.client import client as llm_client
from app.orchestrator.engine import start_engine

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()

    redis_up = await _try_redis()

    scheduler = get_scheduler()
    register_chronic(scheduler)
    scheduler.start()
    log.info("scheduler: started with %d chronic jobs", len(scheduler.get_jobs()))

    event_tasks: list[asyncio.Task] = []
    orchestrator_task: asyncio.Task | None = None
    if redis_up:
        event_tasks = start_event_consumers()
        orchestrator_task = start_engine()
        log.info("event consumers: started (%d)", len(event_tasks))
    else:
        log.warning(
            "redis unavailable — event consumers + orchestrator disabled. "
            "REST endpoints will work; stream-driven features are degraded."
        )

    try:
        yield
    finally:
        if orchestrator_task is not None:
            orchestrator_task.cancel()
        for t in event_tasks:
            t.cancel()
        pending = [*event_tasks]
        if orchestrator_task is not None:
            pending.append(orchestrator_task)
        if pending:
            await asyncio.gather(*pending, return_exceptions=True)
        shutdown_scheduler()
        if redis_up:
            await close_redis()
        await llm_client.aclose()
        log.info("shutdown: complete")


async def _try_redis() -> bool:
    try:
        await get_redis().ping()
        log.info("redis: connected")
        return True
    except (RedisError, OSError) as exc:
        log.warning("redis ping failed (%s); starting in degraded mode", exc)
        return False
