import logging

from app.events.base import EventContext, EventProcessor

log = logging.getLogger(__name__)


class WeatherChange(EventProcessor):
    name = "weather_change"
    input_streams = ["environment.weather"]

    async def handle(self, stream: str, msg_id: str, fields: dict[str, str], ctx: EventContext) -> None:
        log.debug("weather_change handle %s %s", stream, msg_id)


PROCESSOR = WeatherChange()
