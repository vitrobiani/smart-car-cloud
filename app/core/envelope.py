from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SensorStatus(str, Enum):
    OK = "OK"
    UNAVAILABLE = "UNAVAILABLE"
    ERROR = "ERROR"
    PERMISSION_DENIED = "PERMISSION_DENIED"


class SampleType(str, Enum):
    CONTINUOUS = "CONTINUOUS"
    ON_CHANGE = "ON_CHANGE"
    EVENT = "EVENT"


class SensorEnvelope(BaseModel):
    """Shared envelope for every sensor frame — see docs/sensor_specification.md."""

    sensor_id: str
    ts_ms: int = Field(..., description="Unix time in milliseconds")
    trip_id: UUID
    driver_id: UUID
    status: SensorStatus = SensorStatus.OK
    available: bool = True
    payload: dict[str, Any]
