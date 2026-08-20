from enum import Enum

from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class NightModeSource(str, Enum):
    VHAL = "VHAL"
    UI_MODE_MANAGER = "UI_MODE_MANAGER"
    LIGHT_SENSOR_INFERRED = "LIGHT_SENSOR_INFERRED"
    UNAVAILABLE = "UNAVAILABLE"


class SunState(str, Enum):
    DAY = "DAY"
    TWILIGHT = "TWILIGHT"
    NIGHT = "NIGHT"


class LightingPayload(BaseModel):
    night_mode: bool
    night_mode_source: NightModeSource
    ambient_light_lux: float = Field(..., ge=0, le=40_000)
    light_sensor_available: bool
    sun_state: SunState


SENSOR = Sensor(
    sensor_id="env.lighting",
    payload_model=LightingPayload,
    sample_type=SampleType.CONTINUOUS,
    rate_hz=1.0,
)
