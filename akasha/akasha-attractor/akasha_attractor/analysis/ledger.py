from __future__ import annotations

import json
import sqlite3
from pathlib import Path


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def fetch_events(conn: sqlite3.Connection) -> list[dict]:
    """
    Reads from the akasha-time-nexus SQLite schema.
    Joins events + event_context to produce a flat dict per event.
    Maps timestamp_utc → timestamp so downstream analysis is schema-agnostic.
    """
    rows = conn.execute(
        """
        SELECT
            e.event_id,
            e.timestamp_utc   AS timestamp,
            e.event_type      AS category,
            e.source,
            e.title,
            e.notes,
            ec.season,
            ec.hour_local,
            ec.day_of_week,
            ec.moon_phase,
            ec.temperature_c,
            ec.weather_summary
        FROM events e
        LEFT JOIN event_context ec ON ec.event_id = e.event_id
        ORDER BY e.timestamp_utc ASC
        """
    ).fetchall()

    out = []
    for row in rows:
        item = dict(row)
        # Build a context sub-dict so summary_report can read clock.season
        item["payload"] = {
            "context": {
                "clock": {
                    "season":     item.pop("season", None),
                    "hour_local": item.pop("hour_local", None),
                    "day_of_week":item.pop("day_of_week", None),
                },
                "lunar": {
                    "moon_phase": item.pop("moon_phase", None),
                },
                "weather": {
                    "temperature_c":  item.pop("temperature_c", None),
                    "weather_summary":item.pop("weather_summary", None),
                },
            }
        }
        out.append(item)
    return out
