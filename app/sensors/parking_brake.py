from enum import Enum

from pydantic import BaseModel

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class EngagedSource(str, Enum):
    DRIVER = "DRIVER"
    AUTO = "AUTO"
    UNKNOWN = "UNKNOWN"


class ParkingBrakePayload(BaseModel):
    engaged: bool
    auto_apply_enabled: bool
    engaged_source: EngagedSource


SENSOR = Sensor(
    sensor_id="vehicle.parking_brake",
    payload_model=ParkingBrakePayload,
    sample_type=SampleType.ON_CHANGE,
)
