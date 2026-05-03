from __future__ import annotations

from datetime import datetime, timedelta

from .ledger import connect, fetch_events


def _safe_dt(ts: str):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def burst_report(db_path: str, window_hours: int = 6, threshold: int = 3) -> dict:
    conn = connect(db_path)
    events = fetch_events(conn)

    parsed = []
    for event in events:
        dt = _safe_dt(event.get("timestamp", ""))
        if dt:
            parsed.append((dt, event))

    bursts = []
    window = timedelta(hours=window_hours)

    for i, (start_dt, start_event) in enumerate(parsed):
        bucket = [start_event]
        for j in range(i + 1, len(parsed)):
            dt, event = parsed[j]
            if dt - start_dt <= window:
                bucket.append(event)
            else:
                break

        if len(bucket) >= threshold:
            bursts.append({
                "start": start_dt.isoformat(),
                "window_hours": window_hours,
                "count": len(bucket),
                "event_ids": [e["event_id"] for e in bucket],
                "categories": sorted(set(e.get("category", "unknown") for e in bucket)),
                "sources": sorted(set(e.get("source", "unknown") for e in bucket)),
            })

    # Deduplicate overlapping windows by event_ids tuple
    deduped = []
    seen = set()
    for burst in bursts:
        key = tuple(burst["event_ids"])
        if key not in seen:
            seen.add(key)
            deduped.append(burst)

    return {
        "window_hours": window_hours,
        "threshold": threshold,
        "burst_count": len(deduped),
        "bursts": deduped,
    }
