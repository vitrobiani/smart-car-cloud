import asyncio
import logging

from app.core.bus import read_stream
from app.events import (
    alertness_drop,
    driver_identified,
    energy_low,
    geofence,
    harsh_accel,
    harsh_brake,
    hotspot_approaching,
    lane_change,
    llm_failure,
    obstacle,
    parent_approval,
    speed_threshold,
    steering_release,
    trip_lifecycle,
    weather_change,
)
from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)

_MODULES = [
    steering_release,
    harsh_brake,
    harsh_accel,
    lane_change,
    obstacle,
    speed_threshold,
    geofence,
    trip_lifecycle,
    driver_identified,
    alertness_drop,
    weather_change,
    energy_low,
    hotspot_approaching,
    parent_approval,
    llm_failure,
]

EVENT_REGISTRY: dict[str, EventProcessor] = {m.PROCESSOR.name: m.PROCESSOR for m in _MODULES}


async def _run_processor(proc: EventProcessor) -> None:
    ctx = EventContext()
    streams = {s: ">" for s in proc.input_streams}
    if not streams:
        return
    try:
        async for stream, msg_id, fields in read_stream(streams, proc.group, proc.name):
            try:
                await proc.handle(stream, msg_id, fields, ctx)
            except Exception:
                log.exception("event processor %s failed on %s", proc.name, msg_id)
    except asyncio.CancelledError:
        log.info("event processor %s cancelled", proc.name)
        raise


def start_consumers() -> list[asyncio.Task]:
    """Spawn one background task per processor. Return the task handles so lifespan can cancel."""
    return [asyncio.create_task(_run_processor(p), name=f"event:{p.name}") for p in EVENT_REGISTRY.values()]
