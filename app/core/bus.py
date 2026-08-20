from collections.abc import AsyncIterator
from typing import Any

from app.core.envelope import SensorEnvelope
from app.core.redis import get_redis


def sensor_stream(sensor_id: str) -> str:
    return f"telemetry.{sensor_id}"


DERIVED_EVENTS_STREAM = "events.derived"


async def publish_envelope(envelope: SensorEnvelope) -> str:
    """Publish a validated sensor envelope to its per-sensor stream. Returns the stream id."""
    r = get_redis()
    return await r.xadd(
        sensor_stream(envelope.sensor_id),
        {"json": envelope.model_dump_json()},
    )


async def publish_derived_event(event_type: str, payload: dict[str, Any]) -> str:
    r = get_redis()
    return await r.xadd(
        DERIVED_EVENTS_STREAM,
        {"type": event_type, "payload": _json(payload)},
    )


async def read_stream(
    streams: dict[str, str],
    group: str,
    consumer: str,
    block_ms: int = 5000,
    count: int = 32,
) -> AsyncIterator[tuple[str, str, dict[str, str]]]:
    """Yield (stream, message_id, fields) from a consumer group. Creates the group if missing."""
    r = get_redis()
    for stream in streams:
        try:
            await r.xgroup_create(stream, group, id="$", mkstream=True)
        except Exception:
            # BUSYGROUP: already exists — expected on restart
            pass

    while True:
        resp = await r.xreadgroup(group, consumer, streams, count=count, block=block_ms)
        if not resp:
            continue
        for stream, entries in resp:
            for msg_id, fields in entries:
                yield stream, msg_id, fields


def _json(payload: dict[str, Any]) -> str:
    import json

    return json.dumps(payload, default=str)
