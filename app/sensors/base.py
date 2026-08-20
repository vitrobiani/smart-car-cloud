from dataclasses import dataclass

from pydantic import BaseModel

from app.core.envelope import SampleType


@dataclass(frozen=True)
class Sensor:
    """One entry per sensor type. Registered in SENSOR_REGISTRY by sensor_id."""

    sensor_id: str
    payload_model: type[BaseModel]
    sample_type: SampleType
    rate_hz: float | None = None  # None for ON_CHANGE / EVENT
