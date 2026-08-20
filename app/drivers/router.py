from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.adapters.carbrain_db import get_session
from app.drivers import service
from app.drivers.schemas import DriverCreate, DriverRead, PersonaUpdate

router = APIRouter(prefix="/drivers", tags=["drivers"])


@router.get("", response_model=list[DriverRead])
def list_drivers(session: Session = Depends(get_session)) -> list[DriverRead]:
    return [DriverRead.model_validate(d) for d in service.list_drivers(session)]


@router.post("", response_model=DriverRead, status_code=201)
def create_driver(
    payload: DriverCreate, session: Session = Depends(get_session)
) -> DriverRead:
    return DriverRead.model_validate(service.create_driver(session, payload))


@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, session: Session = Depends(get_session)) -> DriverRead:
    driver = service.get_driver(session, driver_id)
    if driver is None:
        raise HTTPException(404, "driver not found")
    return DriverRead.model_validate(driver)


@router.put("/{driver_id}/persona", response_model=DriverRead)
def set_persona(
    driver_id: int,
    payload: PersonaUpdate,
    session: Session = Depends(get_session),
) -> DriverRead:
    driver = service.set_persona(session, driver_id, payload.persona)
    if driver is None:
        raise HTTPException(404, "driver not found")
    return DriverRead.model_validate(driver)
