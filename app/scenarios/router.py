from fastapi import APIRouter, HTTPException

from app.scenarios import runner

router = APIRouter(prefix="/scenarios", tags=["scenarios"])


@router.get("")
def list_scenarios() -> list[str]:
    return runner.list_scenarios()


@router.post("/{name}/start")
def start(name: str) -> dict[str, str]:
    try:
        runner.load(name)
    except FileNotFoundError:
        raise HTTPException(404, f"scenario {name} not found")
    runner.start(name)
    return {"name": name, "status": "started"}


@router.post("/{name}/stop")
def stop(name: str) -> dict[str, str]:
    ok = runner.stop(name)
    return {"name": name, "status": "stopped" if ok else "not_running"}
