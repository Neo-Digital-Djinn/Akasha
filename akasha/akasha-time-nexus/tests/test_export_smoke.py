from akasha_time_nexus.nexus import stamp_event
from akasha_time_nexus.exporters import to_akasha_event


def test_event_export_has_core_fields():
    enriched = stamp_event(
        timestamp_utc="2026-03-30T20:00:00Z",
        latitude=38.42,
        longitude=-82.44,
        event_type="observation",
        title="Smoke test",
    )
    event = to_akasha_event(enriched)
    assert "event_id" in event
    assert "timestamp" in event
    assert "payload" in event
