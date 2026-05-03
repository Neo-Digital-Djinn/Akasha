"""
akasha-anomaly pipeline mode
Called by the orchestrator with a free-text input string.
Stamps it as an observation event, writes to SQLite, emits the event path.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from akasha_time_nexus import stamp_event
from akasha_time_nexus.exporters import to_akasha_event
from akasha_time_nexus.storage.sqlite import connect, init_db, insert_enriched_event


# Default coordinates — can be overridden by AKASHA_LAT / AKASHA_LON env vars
import os

DEFAULT_LAT = float(os.environ.get("AKASHA_LAT", "0.0"))
DEFAULT_LON = float(os.environ.get("AKASHA_LON", "0.0"))
DEFAULT_TZ  = os.environ.get("AKASHA_TZ", "UTC")


def run(title: str, event_dir: Path) -> None:
    ts = datetime.now(timezone.utc).isoformat()

    enriched = stamp_event(
        timestamp_utc=ts,
        latitude=DEFAULT_LAT,
        longitude=DEFAULT_LON,
        event_type="observation",
        title=title,
        notes="",
        source="pipeline",
        metadata={},
    )

    # Write to SQLite ledger
    db_path = event_dir / "ledger.db"
    conn = connect(db_path)
    init_db(conn)
    insert_enriched_event(conn, enriched)
    conn.close()

    # Also emit a JSON sidecar for downstream tools
    event = to_akasha_event(enriched)
    json_path = event_dir / f"{event['event_id']}.json"
    json_path.write_text(json.dumps(event, indent=2))

    season = enriched.context.clock.season
    hour   = enriched.context.clock.hour_local
    tz     = enriched.context.clock.timezone_name
    print(f"[anomaly] observation stamped — season={season}, hour={hour}, tz={tz}")
    print(f"[anomaly] event written → {json_path.name}")
    print(f"[anomaly] ledger → {db_path}")


def main() -> None:
    if len(sys.argv) < 2:
        print("[anomaly] usage: python -m akasha_anomaly.cli.pipeline \"<title>\" [event_dir]")
        sys.exit(1)

    title     = sys.argv[1]
    event_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("events")
    event_dir.mkdir(parents=True, exist_ok=True)

    run(title, event_dir)


if __name__ == "__main__":
    main()
