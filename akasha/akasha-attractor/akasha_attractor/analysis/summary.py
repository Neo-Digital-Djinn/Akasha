from __future__ import annotations

from collections import Counter
from datetime import datetime

from .ledger import connect, fetch_events


def _safe_dt(ts: str):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def summary_report(db_path: str) -> dict:
    conn = connect(db_path)
    events = fetch_events(conn)

    by_category = Counter()
    by_source = Counter()
    by_day = Counter()
    by_hour = Counter()
    by_season = Counter()

    for event in events:
        by_category[event.get("category") or "unknown"] += 1
        by_source[event.get("source") or "unknown"] += 1

        dt = _safe_dt(event.get("timestamp", ""))
        if dt:
            by_day[dt.date().isoformat()] += 1
            by_hour[str(dt.hour).zfill(2)] += 1

        payload = event.get("payload") or {}
        context = payload.get("context") or {}
        clock = context.get("clock") or {}
        season = clock.get("season")
        if season:
            by_season[season] += 1

    return {
        "event_count": len(events),
        "by_category": dict(by_category.most_common()),
        "by_source": dict(by_source.most_common()),
        "by_day": dict(by_day.most_common()),
        "by_hour": dict(by_hour.most_common()),
        "by_season": dict(by_season.most_common()),
    }
