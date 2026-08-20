from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.adapters.carbrain_db import get_session
from app.trips import service
from app.trips.schemas import TripRead, TripSummaryRead

router = APIRouter(prefix="/trips", tags=["trips"])


@router.get("", response_model=list[TripRead])
def list_trips(session: Session = Depends(get_session)) -> list[TripRead]:
    return [TripRead.model_validate(t) for t in service.list_trips(session)]


@router.get("/{trip_id}", response_model=TripRead)
def get_trip(trip_id: int, session: Session = Depends(get_session)) -> TripRead:
    trip = service.get_trip(session, trip_id)
    if trip is None:
        raise HTTPException(404, "trip not found")
    return TripRead.model_validate(trip)


@router.get("/{trip_id}/summary", response_model=TripSummaryRead)
def get_summary(trip_id: int, session: Session = Depends(get_session)) -> TripSummaryRead:
    trip = service.get_trip(session, trip_id)
    if trip is None:
        raise HTTPException(404, "trip not found")
    if trip.summary is None:
        raise HTTPException(404, "summary not available")
    return TripSummaryRead(trip_id=trip.id, summary=trip.summary)
