CREATE TABLE IF NOT EXISTS events (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_utc TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    event_type TEXT NOT NULL,
    title TEXT NOT NULL DEFAULT '',
    notes TEXT NOT NULL DEFAULT '',
    source TEXT NOT NULL DEFAULT 'manual',
    metadata_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS event_context (
    context_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id INTEGER NOT NULL REFERENCES events(event_id) ON DELETE CASCADE,

    utc TEXT NOT NULL,
    local TEXT NOT NULL,
    timezone_name TEXT NOT NULL,
    day_of_week TEXT NOT NULL,
    day_of_year INTEGER NOT NULL,
    season TEXT NOT NULL,
    hour_local INTEGER NOT NULL,
    is_weekend INTEGER NOT NULL,

    sunrise_local TEXT,
    sunset_local TEXT,
    is_daylight INTEGER,
    minutes_from_sunrise INTEGER,
    minutes_from_sunset INTEGER,

    moon_phase TEXT,
    moon_illumination_pct REAL,

    temperature_c REAL,
    humidity_pct REAL,
    pressure_mb REAL,
    wind_kph REAL,
    precipitation_mm REAL,
    weather_summary TEXT,

    extra_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp_utc);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
