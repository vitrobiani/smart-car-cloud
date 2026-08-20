from app.events import EVENT_REGISTRY


def test_all_15_event_processors_registered() -> None:
    assert len(EVENT_REGISTRY) == 15


def test_every_processor_declares_streams_or_group() -> None:
    for proc in EVENT_REGISTRY.values():
        assert isinstance(proc.input_streams, list)
        assert proc.group
