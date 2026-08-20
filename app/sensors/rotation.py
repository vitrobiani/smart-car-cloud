from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class RotationPayload(BaseModel):
    qx: float = Field(..., ge=-1, le=1)
    qy: float = Field(..., ge=-1, le=1)
    qz: float = Field(..., ge=-1, le=1)
    qw: float = Field(..., ge=-1, le=1)
    heading_deg: float = Field(..., ge=0, le=360)
    pitch_deg: float = Field(..., ge=-90, le=90)
    roll_deg: float = Field(..., ge=-180, le=180)
    gyro_x: float = Field(..., ge=-10, le=10)
    gyro_y: float = Field(..., ge=-10, le=10)
    gyro_z: float = Field(..., ge=-10, le=10)


SENSOR = Sensor(
    sensor_id="vehicle.rotation",
    payload_model=RotationPayload,
    sample_type=SampleType.CONTINUOUS,
    rate_hz=50.0,
)
