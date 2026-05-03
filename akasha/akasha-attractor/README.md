# akasha-attractor

Akasha Attractor is the first **pattern and clustering engine** in the Akasha ecosystem.

It reads the persistent event ledger from `akasha-events` and surfaces simple, disciplined patterns.

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

V2 is intentionally modest.

It does not attempt to explain reality. It does not infer causes.
It performs first-order pattern work:

- count events by category
- count events by source
- count events by day
- count events by hour
- count events by season (when present in payload context)
- detect simple burst windows

## Why it exists

Akasha needs a first discovery loop that is real, honest, and useful.

Attractor begins that loop by answering questions like:

- what categories are most common?
- which sources dominate?
- when do events cluster?
- are there bursts of activity in short time windows?

## Discipline

Attractor is not an oracle.

Its job is:

- read
- count
- group
- compare
- surface

Interpretation belongs later, after signal is real.

## Example usage

```bash
python -m akasha_attractor.cli.main summary --db events.db
```

```bash
python -m akasha_attractor.cli.main bursts --db events.db --window-hours 6 --threshold 3
```

## Engine Role

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
