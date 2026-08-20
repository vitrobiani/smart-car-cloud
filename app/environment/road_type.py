"""Road-type classification interface. Real impl calls OSM / Overpass."""
from enum import Enum

from pydantic import BaseModel


class RoadClass(str, Enum):
    URBAN = "URBAN"
    RURAL = "RURAL"
    HIGHWAY = "HIGHWAY"
    SCHOOL_ZONE = "SCHOOL_ZONE"
    UNKNOWN = "UNKNOWN"


class RoadType(BaseModel):
    road_class: RoadClass


async def classify(lat: float, lon: float) -> RoadType:
    raise NotImplementedError("road-type provider not integrated")
