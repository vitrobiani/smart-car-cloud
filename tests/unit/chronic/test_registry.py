from app.chronic import CHRONIC_REGISTRY


def test_all_11_chronic_jobs_registered() -> None:
    assert len(CHRONIC_REGISTRY) == 11


def test_every_job_has_positive_interval() -> None:
    for job in CHRONIC_REGISTRY.values():
        assert job.interval_s > 0
