"""Bluetooth beacon → driver_id resolution.

Not integrated: the carbrain `drivers` table doesn't currently carry a
bluetooth MAC column. Needs a schema addition from smart_car_project
before this can be wired up.
"""
from sqlalchemy.orm import Session


def resolve_by_mac(session: Session, mac: str) -> int | None:
    raise NotImplementedError(
        "drivers table has no bluetooth_mac column — coordinate with smart_car_project"
    )
