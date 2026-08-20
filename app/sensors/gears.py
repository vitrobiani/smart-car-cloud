from enum import Enum

from pydantic import BaseModel

from app.core.envelope import SampleType
from app.sensors.base import Sensor


class Gear(str, Enum):
    P = "P"
    R = "R"
    N = "N"
    D = "D"
    S = "S"
    M = "M"
    G1 = "1"
    G2 = "2"
    G3 = "3"
    G4 = "4"
    G5 = "5"
    G6 = "6"
    G7 = "7"
    G8 = "8"


class GearsPayload(BaseModel):
    gear_selected: Gear
    gear_engaged: Gear
    is_shift: bool = False
    previous_gear: Gear | None = None


SENSOR = Sensor(
    sensor_id="vehicle.gears",
    payload_model=GearsPayload,
    sample_type=SampleType.ON_CHANGE,
)
