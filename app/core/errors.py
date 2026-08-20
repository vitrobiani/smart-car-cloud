from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class SensorNotFound(Exception):
    def __init__(self, sensor_id: str) -> None:
        self.sensor_id = sensor_id


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(SensorNotFound)
    async def _sensor_not_found(_: Request, exc: SensorNotFound) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": f"unknown sensor_id: {exc.sensor_id}"},
        )
