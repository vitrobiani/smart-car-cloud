from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class OdometerPayload(BaseModel):
    total_km: float = Field(..., ge=0)
    trip_km: float = Field(..., ge=0)
    session_delta_km: float = Field(..., ge=0)


SENSOR = Sensor(
    sensor_id="vehicle.odometer",
    payload_model=OdometerPayload,
    sample_type=SampleType.CONTINUOUS,
    rate_hz=0.2,
)
