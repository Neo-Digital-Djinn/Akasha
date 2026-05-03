from __future__ import annotations

import uuid

from ..models import EnrichedEvent


def to_akasha_event(enriched: EnrichedEvent, confidence: float | None = None) -> dict:
    event = enriched.event
    context = enriched.context.to_dict()

    payload = {
        "title": event.title,
        "notes": event.notes,
        "event_type": event.event_type,
        "metadata": event.metadata,
        "context": context,
    }

    out = {
        "event_id": str(uuid.uuid4()),
        "timestamp": event.timestamp_utc,
        "location": f"{event.latitude},{event.longitude}",
        "category": event.event_type,
        "source": event.source,
        "payload": payload,
    }

    if confidence is not None:
        out["confidence"] = confidence

    return out
