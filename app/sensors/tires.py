from pydantic import BaseModel, Field

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class TiresPayload(BaseModel):
    front_left_kpa: float = Field(..., ge=0, le=500)
    front_right_kpa: float = Field(..., ge=0, le=500)
    rear_left_kpa: float = Field(..., ge=0, le=500)
    rear_right_kpa: float = Field(..., ge=0, le=500)
    min_kpa: float = Field(..., ge=0, le=500)
    low_pressure_alert: bool = False
    critical_pressure_alert: bool = False
    recommended_kpa: float = Field(..., gt=0)


SENSOR = Sensor(
    sensor_id="vehicle.tires",
    payload_model=TiresPayload,
    sample_type=SampleType.ON_CHANGE,
)
