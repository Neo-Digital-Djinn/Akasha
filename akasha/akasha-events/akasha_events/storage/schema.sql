CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE,
    timestamp TEXT NOT NULL,
    location TEXT,
    category TEXT NOT NULL,
    source TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    confidence REAL
);

CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_category ON events(category);
CREATE INDEX IF NOT EXISTS idx_events_source ON events(source);
