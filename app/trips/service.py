from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.adapters.carbrain_db import Trip


def start_trip(session: Session, driver_id: int) -> Trip:
    trip = Trip(driver_id=driver_id, start_time=datetime.now(timezone.utc))
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip


def end_trip(session: Session, trip_id: int) -> Trip | None:
    trip = session.get(Trip, trip_id)
    if trip is None:
        return None
    trip.end_time = datetime.now(timezone.utc)
    session.commit()
    session.refresh(trip)
    return trip


def list_trips(session: Session) -> list[Trip]:
    return list(session.query(Trip).all())


def get_trip(session: Session, trip_id: int) -> Trip | None:
    return session.get(Trip, trip_id)
