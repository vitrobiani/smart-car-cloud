import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class EnergyLow(EventProcessor):
    name = "energy_low"
    input_streams = ["telemetry.vehicle.energy"]

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("energy_low handle %s %s", stream, msg_id)


PROCESSOR = EnergyLow()
