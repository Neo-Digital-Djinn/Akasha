from __future__ import annotations

import json
import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()


def insert_event(conn: sqlite3.Connection, event: dict) -> int:
    cur = conn.execute(
        '''
        INSERT INTO events (
            event_id, timestamp, location, category, source, payload_json, confidence
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            event["event_id"],
            event["timestamp"],
            event.get("location"),
            event["category"],
            event["source"],
            json.dumps(event["payload"]),
            event.get("confidence"),
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def list_events(conn: sqlite3.Connection, limit: int = 50) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM events ORDER BY timestamp ASC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]


def recent_events(conn: sqlite3.Connection, limit: int = 10) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM events ORDER BY timestamp DESC LIMIT ?",
        (limit,),
    ).fetchall()
    return [dict(r) for r in rows]
