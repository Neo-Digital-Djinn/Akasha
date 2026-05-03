import uuid

def generate_directives(summary: dict, bursts: dict) -> dict:
    directives = []

    if summary.get("event_count", 0) < 25:
        directives.append({
            "directive_id": str(uuid.uuid4()),
            "directive_type": "observation_focus",
            "priority": 0.9,
            "reason": "Ledger sparse — increase disciplined observation."
        })

    if bursts.get("burst_count", 0) > 0:
        directives.append({
            "directive_id": str(uuid.uuid4()),
            "directive_type": "provider_search",
            "priority": 0.8,
            "reason": "Burst windows detected — search for more environmental providers."
        })

    directives.sort(key=lambda d: d["priority"], reverse=True)

    return {
        "directive_count": len(directives),
        "directives": directives
    }
