from sqlalchemy.orm import Session

from app.adapters.carbrain_db import Driver
from app.drivers.schemas import DriverCreate


def create_driver(session: Session, payload: DriverCreate) -> Driver:
    driver = Driver(**payload.model_dump(exclude_none=True))
    session.add(driver)
    session.commit()
    session.refresh(driver)
    return driver


def list_drivers(session: Session) -> list[Driver]:
    return list(session.query(Driver).all())


def get_driver(session: Session, driver_id: int) -> Driver | None:
    return session.get(Driver, driver_id)


def set_persona(session: Session, driver_id: int, persona: str) -> Driver | None:
    driver = session.get(Driver, driver_id)
    if driver is None:
        return None
    driver.persona = persona
    session.commit()
    session.refresh(driver)
    return driver
