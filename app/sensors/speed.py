from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class SpeedPayload(BaseModel):
    speed_mps: float = Field(..., ge=-30, le=90)
    speed_kmh: float


SENSOR = Sensor(
    sensor_id="vehicle.speed",
    payload_model=SpeedPayload,
    sample_type=SampleType.CONTINUOUS,
    rate_hz=10.0,
)
