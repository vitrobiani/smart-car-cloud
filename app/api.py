from fastapi import FastAPI

from app.core.errors import register_exception_handlers
from app.delivery.router import router as delivery_router
from app.drivers.router import router as drivers_router
from app.environment.router import router as environment_router
from app.lifespan import lifespan
from app.llm.router import router as llm_router
from app.orchestrator.router import router as orchestrator_router
from app.scenarios.router import router as scenarios_router
from app.sensors.router import router as sensors_router
from app.trips.router import router as trips_router

app = FastAPI(
    title="Car Brain",
    summary="Cloud interface for Volkswagen's Car Brain challenge – Phase 2 prototype.",
    version="0.1",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.include_router(sensors_router)
app.include_router(drivers_router)
app.include_router(trips_router)
app.include_router(environment_router)
app.include_router(orchestrator_router)
app.include_router(llm_router)
app.include_router(delivery_router)
app.include_router(scenarios_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
