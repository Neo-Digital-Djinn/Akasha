from __future__ import annotations

import argparse
import json

from akasha_attractor.analysis.summary import summary_report
from akasha_attractor.analysis.bursts import burst_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="akasha-attractor")
    sub = parser.add_subparsers(dest="command", required=True)

    summary = sub.add_parser("summary", help="Generate grouped event summary")
    summary.add_argument("--db", required=True)

    bursts = sub.add_parser("bursts", help="Detect burst windows in the ledger")
    bursts.add_argument("--db", required=True)
    bursts.add_argument("--window-hours", type=int, default=6)
    bursts.add_argument("--threshold", type=int, default=3)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "summary":
        print(json.dumps(summary_report(args.db), indent=2))
    elif args.command == "bursts":
        print(json.dumps(
            burst_report(args.db, window_hours=args.window_hours, threshold=args.threshold),
            indent=2
        ))


if __name__ == "__main__":
    main()
