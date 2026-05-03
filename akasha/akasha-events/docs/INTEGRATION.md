# Integration

## Current intended flow

human or machine observation
→ akasha-anomaly
→ akasha-time-nexus
→ akasha-events

## Example

1. `akasha-anomaly` emits an event JSON file
2. `akasha-events add --db events.db --file event.json`
3. event is persisted in the ledger
