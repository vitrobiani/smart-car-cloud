from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from app.adapters.carbrain_db import Telemetry, get_session
from app.core.bus import publish_envelope
from app.core.envelope import SensorEnvelope
from app.core.errors import SensorNotFound
from app.sensors import SENSOR_REGISTRY, get_sensor

router = APIRouter(tags=["sensors"])


class SensorInfo(BaseModel):
    sensor_id: str
    sample_type: str
    rate_hz: float | None


class IngestResponse(BaseModel):
    stream_id: str


class BatchIngestResponse(BaseModel):
    accepted: int
    stream_ids: list[str]


@router.get("/sensors", response_model=list[SensorInfo])
def list_sensors() -> list[SensorInfo]:
    return [
        SensorInfo(
            sensor_id=s.sensor_id,
            sample_type=s.sample_type.value,
            rate_hz=s.rate_hz,
        )
        for s in SENSOR_REGISTRY.values()
    ]


@router.post(
    "/ingest/{sensor_id}",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=IngestResponse,
)
async def ingest(
    sensor_id: str,
    envelope: SensorEnvelope,
    session: Session = Depends(get_session),
) -> IngestResponse:
    stream_id = await _ingest_one(sensor_id, envelope, session)
    await run_in_threadpool(session.commit)
    return IngestResponse(stream_id=stream_id)


@router.post(
    "/ingest/batch",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=BatchIngestResponse,
)
async def ingest_batch(
    envelopes: list[SensorEnvelope],
    session: Session = Depends(get_session),
) -> BatchIngestResponse:
    ids: list[str] = []
    for env in envelopes:
        ids.append(await _ingest_one(env.sensor_id, env, session))
    await run_in_threadpool(session.commit)
    return BatchIngestResponse(accepted=len(ids), stream_ids=ids)


async def _ingest_one(
    sensor_id: str, envelope: SensorEnvelope, session: Session
) -> str:
    sensor = get_sensor(sensor_id)
    if sensor is None:
        raise SensorNotFound(sensor_id)
    if envelope.sensor_id != sensor_id:
        envelope = envelope.model_copy(update={"sensor_id": sensor_id})
    _validate_payload(sensor.payload_model, envelope.payload)
    # envelope.trip_id is UUID; carbrain.telemetry.trip_id is Integer. int(UUID)
    # overflows a 32-bit column, so we write NULL until smart_car_project widens
    # the column (or we switch the envelope to int trip ids).
    session.add(
        Telemetry(
            trip_id=None,
            timestamp=datetime.fromtimestamp(envelope.ts_ms / 1000, tz=timezone.utc),
            sensor_type=envelope.sensor_id,
            sensor_data=envelope.payload,
        )
    )
    return await publish_envelope(envelope)


def _validate_payload(model: type[BaseModel], payload: dict[str, Any]) -> None:
    try:
        model.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors())
