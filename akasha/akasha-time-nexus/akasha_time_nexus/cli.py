from __future__ import annotations

import argparse
import json
from pathlib import Path

from .exporters import to_akasha_event
from .nexus import stamp_event
from .storage.sqlite import connect, init_db, insert_enriched_event


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="akasha-time-nexus")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ("stamp", "event"):
        cmd = sub.add_parser(name)
        cmd.add_argument("--timestamp", required=True, help="UTC timestamp, e.g. 2026-03-30T20:00:00Z")
        cmd.add_argument("--lat", type=float, required=True)
        cmd.add_argument("--lon", type=float, required=True)
        cmd.add_argument("--event-type", default="observation")
        cmd.add_argument("--title", default="")
        cmd.add_argument("--notes", default="")
        cmd.add_argument("--source", default="manual")
        cmd.add_argument("--db", default="", help="Optional SQLite database path")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    enriched = stamp_event(
        timestamp_utc=args.timestamp,
        latitude=args.lat,
        longitude=args.lon,
        event_type=args.event_type,
        title=args.title,
        notes=args.notes,
        source=args.source,
        metadata={},
    )

    if args.command == "stamp":
        print(json.dumps(enriched.to_dict(), indent=2))
        if args.db:
            conn = connect(Path(args.db))
            init_db(conn)
            event_id = insert_enriched_event(conn, enriched)
            print(f"stored_event_id={event_id}")
    elif args.command == "event":
        event_payload = to_akasha_event(enriched)
        print(json.dumps(event_payload, indent=2))

if __name__ == "__main__":
    main()
