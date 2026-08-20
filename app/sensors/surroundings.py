from enum import Enum

from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class ObjectType(str, Enum):
    CAR = "CAR"
    TRUCK = "TRUCK"
    MOTORCYCLE = "MOTORCYCLE"
    PEDESTRIAN = "PEDESTRIAN"
    CYCLIST = "CYCLIST"
    ANIMAL = "ANIMAL"
    UNKNOWN = "UNKNOWN"


class LaneRelative(str, Enum):
    SAME = "SAME"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UNKNOWN = "UNKNOWN"


class Vec2(BaseModel):
    x: float
    y: float


class Vec2Velocity(BaseModel):
    vx: float
    vy: float


class SurroundingObject(BaseModel):
    object_id: int
    type: ObjectType
    relative_position_m: Vec2
    relative_velocity_mps: Vec2Velocity
    distance_m: float = Field(..., ge=0, le=200)
    bearing_deg: float = Field(..., ge=-180, le=180)
    lane_relative: LaneRelative
    time_to_collision_s: float | None = None
    confidence: float = Field(..., ge=0, le=1)


class SurroundingsPayload(BaseModel):
    objects: list[SurroundingObject] = []
    following_distance_m: float | None = None
    following_time_s: float | None = None


SENSOR = Sensor(
    sensor_id="env.surroundings",
    payload_model=SurroundingsPayload,
    sample_type=SampleType.CONTINUOUS,
    rate_hz=5.0,
)
