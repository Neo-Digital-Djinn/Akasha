"""
akasha-attractor pipeline adapter.
Wraps the summary report with human-readable [attractor] labels.
"""
from __future__ import annotations

import sys
import json

from akasha_attractor.analysis.summary import summary_report


def run(db_path: str) -> None:
    report = summary_report(db_path)

    count = report.get("event_count", 0)
    by_day = report.get("by_day", {})
    by_season = report.get("by_season", {})
    by_hour = report.get("by_hour", {})
    by_source = report.get("by_source", {})

    # Most active day
    top_day = max(by_day, key=lambda d: by_day[d]) if by_day else "—"
    top_hour = max(by_hour, key=lambda h: by_hour[h]) if by_hour else "—"
    top_season = max(by_season, key=lambda s: by_season[s]) if by_season else "—"

    print(f"[attractor] event_count:  {count}")
    print(f"[attractor] top day:      {top_day} ({by_day.get(top_day, 0)} events)")
    print(f"[attractor] peak hour:    {top_hour}:00 UTC")
    print(f"[attractor] season:       {top_season}")
    print(f"[attractor] sources:      {', '.join(by_source.keys()) or '—'}")

    days = sorted(by_day.keys())
    if len(days) > 1:
        span = f"{days[0]} → {days[-1]}"
    elif days:
        span = days[0]
    else:
        span = "no data"
    print(f"[attractor] date span:    {span}")


def main() -> None:
    if len(sys.argv) < 2:
        print("[attractor] ERROR: db path required", file=sys.stderr)
        sys.exit(1)
    run(sys.argv[1])


if __name__ == "__main__":
    main()
