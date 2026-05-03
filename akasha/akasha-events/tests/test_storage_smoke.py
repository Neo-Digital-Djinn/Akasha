from pathlib import Path

from akasha_events.storage.sqlite import connect, init_db, insert_event, recent_events


def test_storage_roundtrip(tmp_path: Path):
    db = tmp_path / "events.db"
    conn = connect(db)
    init_db(conn)
    insert_event(conn, {
        "event_id": "test-1",
        "timestamp": "2026-03-30T20:00:00Z",
        "location": "0,0",
        "category": "test",
        "source": "unit",
        "payload": {"hello": "world"},
        "confidence": 1.0,
    })
    rows = recent_events(conn, limit=1)
    assert len(rows) == 1
