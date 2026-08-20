from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class PedalsPayload(BaseModel):
    accelerator_pct: float = Field(..., ge=0, le=100)
    brake_pct: float = Field(..., ge=0, le=100)
    brake_light_on: bool = False
    accelerator_available: bool = True
    brake_available: bool = True


SENSOR = Sensor(
    sensor_id="vehicle.pedals",
    payload_model=PedalsPayload,
    sample_type=SampleType.CONTINUOUS,
    rate_hz=20.0,
)
