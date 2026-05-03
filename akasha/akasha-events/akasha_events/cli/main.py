from __future__ import annotations

import argparse
import json
from pathlib import Path

from akasha_events.storage.sqlite import connect, init_db, insert_event, list_events, recent_events


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="akasha-events")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Insert an event JSON file into the ledger")
    add.add_argument("--db", required=True)
    add.add_argument("--file", required=True)

    lst = sub.add_parser("list", help="List events")
    lst.add_argument("--db", required=True)
    lst.add_argument("--limit", type=int, default=50)

    recent = sub.add_parser("recent", help="Show recent events")
    recent.add_argument("--db", required=True)
    recent.add_argument("--limit", type=int, default=10)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    conn = connect(Path(args.db))
    init_db(conn)

    if args.command == "add":
        event = json.loads(Path(args.file).read_text(encoding="utf-8"))
        row_id = insert_event(conn, event)
        print(f"stored_row_id={row_id}")

    elif args.command == "list":
        print(json.dumps(list_events(conn, limit=args.limit), indent=2))

    elif args.command == "recent":
        print(json.dumps(recent_events(conn, limit=args.limit), indent=2))

if __name__ == "__main__":
    main()
