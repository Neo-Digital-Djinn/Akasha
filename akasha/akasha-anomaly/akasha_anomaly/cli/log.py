from __future__ import annotations

import argparse
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from akasha_time_nexus import stamp_event
from akasha_time_nexus.exporters import to_akasha_event


def build_parser():
    p = argparse.ArgumentParser()
    p.add_argument("--title", required=True)
    p.add_argument("--notes", default="")
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--timestamp", default="")
    p.add_argument("--source", default="human")
    p.add_argument("--out", default="events")
    return p


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.timestamp:
        ts = args.timestamp
    else:
        ts = datetime.now(timezone.utc).isoformat()

    enriched = stamp_event(
        timestamp_utc=ts,
        latitude=args.lat,
        longitude=args.lon,
        event_type="observation",
        title=args.title,
        notes=args.notes,
        source=args.source,
        metadata={},
    )

    event = to_akasha_event(enriched)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    event_id = event["event_id"]
    path = out_dir / f"{event_id}.json"

    path.write_text(json.dumps(event, indent=2))

    print("Event stored:", path)
