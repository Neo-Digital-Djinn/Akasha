from pathlib import Path
import sqlite3
import json

from akasha_attractor.analysis.summary import summary_report


def test_summary_report(tmp_path: Path):
    db = tmp_path / "events.db"
    conn = sqlite3.connect(str(db))
    conn.execute(
        '''
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL UNIQUE,
            timestamp TEXT NOT NULL,
            location TEXT,
            category TEXT NOT NULL,
            source TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            confidence REAL
        )
        '''
    )
    conn.execute(
        '''
        INSERT INTO events (event_id, timestamp, location, category, source, payload_json, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            "evt-1",
            "2026-03-30T20:00:00Z",
            "0,0",
            "observation",
            "human",
            json.dumps({"title": "test"}),
            1.0,
        ),
    )
    conn.commit()

    report = summary_report(str(db))
    assert report["event_count"] == 1
    assert report["by_category"]["observation"] == 1
