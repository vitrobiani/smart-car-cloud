import asyncio
import json
import logging
from pathlib import Path
from typing import Any

import httpx

log = logging.getLogger(__name__)

LIBRARY = Path(__file__).parent / "library"

_running: dict[str, asyncio.Task] = {}


def list_scenarios() -> list[str]:
    return sorted(p.stem for p in LIBRARY.glob("*.json"))


def load(name: str) -> dict[str, Any]:
    path = LIBRARY / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(name)
    return json.loads(path.read_text())


async def _play(name: str, base_url: str) -> None:
    scenario = load(name)
    async with httpx.AsyncClient(base_url=base_url, timeout=5.0) as client:
        for frame in scenario["frames"]:
            await asyncio.sleep(frame["delay_ms"] / 1000)
            env = frame["envelope"]
            try:
                await client.post(f"/ingest/{env['sensor_id']}", json=env)
            except Exception:
                log.exception("scenario %s: ingest failed", name)


def start(name: str, base_url: str = "http://localhost:8000") -> None:
    if name in _running and not _running[name].done():
        return
    _running[name] = asyncio.create_task(_play(name, base_url), name=f"scenario:{name}")


def stop(name: str) -> bool:
    task = _running.pop(name, None)
    if task is None:
        return False
    task.cancel()
    return True
