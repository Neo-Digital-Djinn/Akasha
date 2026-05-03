
import json
import uuid
from datetime import datetime, timezone

def create_event(category, source, payload, location=None, confidence=None):
    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "category": category,
        "source": source,
        "payload": payload
    }

    if location:
        event["location"] = location

    if confidence:
        event["confidence"] = confidence

    return event

def save_event(event, path):
    with open(path, "w") as f:
        json.dump(event, f, indent=2)

if __name__ == "__main__":
    event = create_event(
        category="test_event",
        source="local",
        payload={"message":"Akasha event system initialized"}
    )

    save_event(event, "test_event.json")
    print("Event written:", event["event_id"])
