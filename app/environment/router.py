from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.environment import road_type, speed_limits, weather

router = APIRouter(prefix="/environment", tags=["environment"])


class EnvironmentRead(BaseModel):
    weather: weather.Weather
    road_type: road_type.RoadType
    speed_limit: speed_limits.SpeedLimit
    geofences: list[str]


@router.get(
    "/{lat}/{lon}",
    response_model=EnvironmentRead,
    responses={501: {"description": "Environment providers not integrated"}},
)
async def snapshot(lat: float, lon: float) -> EnvironmentRead:
    raise HTTPException(
        status_code=501,
        detail="environment providers (weather/road/speed-limits/geofence) not integrated",
    )
