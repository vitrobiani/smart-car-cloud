from enum import Enum

from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class LaneDeparture(str, Enum):
    INACTIVE = "INACTIVE"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class LaneKeepAssist(str, Enum):
    OFF = "OFF"
    ON = "ON"
    INTERVENING = "INTERVENING"


class ForwardCollisionWarning(str, Enum):
    INACTIVE = "INACTIVE"
    WARNING = "WARNING"
    EMERGENCY_BRAKE = "EMERGENCY_BRAKE"


class AdaptiveCruiseState(str, Enum):
    OFF = "OFF"
    STANDBY = "STANDBY"
    ACTIVE = "ACTIVE"
    OVERRIDE = "OVERRIDE"


class TrafficSignType(str, Enum):
    SPEED_LIMIT = "SPEED_LIMIT"
    STOP = "STOP"
    YIELD = "YIELD"
    OTHER = "OTHER"


class TrafficSign(BaseModel):
    type: TrafficSignType
    value: int | None = None
    confidence: float = Field(..., ge=0, le=1)
    distance_m: float = Field(..., ge=0)


class AdasPayload(BaseModel):
    adas_available: bool
    front_radar_distance_m: float | None = Field(default=None, ge=0, le=200)
    rear_radar_distance_m: float | None = Field(default=None, ge=0, le=100)
    ultrasonic_front_m: list[float] = []
    ultrasonic_rear_m: list[float] = []
    lane_departure_warning: LaneDeparture = LaneDeparture.INACTIVE
    lane_keep_assist: LaneKeepAssist = LaneKeepAssist.OFF
    blind_spot_left: bool = False
    blind_spot_right: bool = False
    forward_collision_warning: ForwardCollisionWarning = ForwardCollisionWarning.INACTIVE
    adaptive_cruise_state: AdaptiveCruiseState = AdaptiveCruiseState.OFF
    adaptive_cruise_set_speed_mps: float | None = Field(default=None, ge=0, le=55)
    traffic_sign_recognition: list[TrafficSign] = []


SENSOR = Sensor(
    sensor_id="vehicle.adas",
    payload_model=AdasPayload,
    sample_type=SampleType.CONTINUOUS,
    rate_hz=10.0,
)
