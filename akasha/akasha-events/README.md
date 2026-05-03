# akasha-events

Akasha Events is the canonical **event schema and persistent ledger layer** for the Akasha ecosystem.

Everything that happens in Akasha — human observations, API data, sensor readings,
and future discovery outputs — is represented as an **Event**.

## Position in the Akasha stack

```text
akasha-anomaly
    ↓
akasha-time-nexus
    ↓
akasha-events
    ↓
akasha-attractor
```

## V2 goal

V2 turns `akasha-events` from a schema-only seed into a **working event ledger**.

It now includes:

- canonical event schema
- SQLite storage
- event insert helpers
- simple event query helpers
- CLI for add/list/recent

## Why it matters

Without a durable event ledger, Akasha has no memory.

Akasha Events is the first persistent place where:

- enriched observations
- machine observations
- external observations

can accumulate in a common structure and later be queried for patterns.

## Example event

```json
{
  "event_id": "uuid",
  "timestamp": "2026-03-30T20:00:00Z",
  "location": "38.42,-82.44",
  "category": "observation",
  "source": "human",
  "payload": {
    "title": "strange lights",
    "notes": "three flashes near tree line"
  },
  "confidence": 0.72
}
```

## Engine Role

TODO: fill this section.

## Why it exists

TODO: fill this section.

## Inputs

TODO: fill this section.

## Memory / Registry

TODO: fill this section.

## Relation Model

TODO: fill this section.

## Evaluator

TODO: fill this section.

## Outputs

TODO: fill this section.

## Position in Constellation

TODO: fill this section.

## Next Steps

TODO: fill this section.
