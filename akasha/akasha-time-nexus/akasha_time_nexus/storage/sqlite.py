from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from ..models import EnrichedEvent

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(schema)
    conn.commit()


def insert_enriched_event(conn: sqlite3.Connection, enriched: EnrichedEvent) -> int:
    event = enriched.event
    ctx = enriched.context

    cur = conn.execute(
        '''
        INSERT INTO events (
            timestamp_utc, latitude, longitude, event_type, title, notes, source, metadata_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            event.timestamp_utc,
            event.latitude,
            event.longitude,
            event.event_type,
            event.title,
            event.notes,
            event.source,
            json.dumps(event.metadata),
        ),
    )
    event_id = int(cur.lastrowid)

    conn.execute(
        '''
        INSERT INTO event_context (
            event_id,
            utc, local, timezone_name, day_of_week, day_of_year, season, hour_local, is_weekend,
            sunrise_local, sunset_local, is_daylight, minutes_from_sunrise, minutes_from_sunset,
            moon_phase, moon_illumination_pct,
            temperature_c, humidity_pct, pressure_mb, wind_kph, precipitation_mm, weather_summary,
            extra_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        (
            event_id,
            ctx.clock.utc,
            ctx.clock.local,
            ctx.clock.timezone_name,
            ctx.clock.day_of_week,
            ctx.clock.day_of_year,
            ctx.clock.season,
            ctx.clock.hour_local,
            1 if ctx.clock.is_weekend else 0,
            ctx.solar.sunrise_local,
            ctx.solar.sunset_local,
            None if ctx.solar.is_daylight is None else int(ctx.solar.is_daylight),
            ctx.solar.minutes_from_sunrise,
            ctx.solar.minutes_from_sunset,
            ctx.lunar.moon_phase,
            ctx.lunar.moon_illumination_pct,
            ctx.weather.temperature_c,
            ctx.weather.humidity_pct,
            ctx.weather.pressure_mb,
            ctx.weather.wind_kph,
            ctx.weather.precipitation_mm,
            ctx.weather.summary,
            json.dumps(ctx.extra),
        ),
    )
    conn.commit()
    return event_id
