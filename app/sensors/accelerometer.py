from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class AccelerometerPayload(BaseModel):
    ax: float = Field(..., ge=-20, le=20)
    ay: float = Field(..., ge=-20, le=20)
    az: float = Field(..., ge=-20, le=20)
    linear_ax: float = Field(..., ge=-20, le=20)
    linear_ay: float = Field(..., ge=-20, le=20)
    linear_az: float = Field(..., ge=-20, le=20)
    magnitude: float = Field(..., ge=0, le=30)


SENSOR = Sensor(
    sensor_id="vehicle.accelerometer",
    payload_model=AccelerometerPayload,
    sample_type=SampleType.CONTINUOUS,
    rate_hz=50.0,
)
