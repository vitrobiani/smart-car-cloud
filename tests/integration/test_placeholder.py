import pytest


@pytest.mark.skip(reason="needs Postgres+Redis via docker-compose")
def test_ingest_end_to_end() -> None:
    """Placeholder: bring up compose, POST /ingest/vehicle.speed, assert row + stream."""
    ...
