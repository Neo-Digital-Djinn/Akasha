# akasha-time-nexus

Akasha-native context engine that transforms a plain timestamp and location into a multi-axis world-state record.

## V2 goal

V2 is the first version that **wires into real adapters from `akasha-apis`** and emits records that can be stored in the **Akasha Events** format.

This repo now sits in the middle of the first living Akasha loop:

```text
akasha-apis
    ↓
akasha-time-nexus
    ↓
akasha-events
```

## What it does

Given:

- UTC timestamp
- latitude
- longitude
- event metadata

it:

1. resolves timezone context
2. fetches sunrise/sunset context
3. fetches weather context
4. derives clock/season fields
5. builds a normalized context bundle
6. can export an Akasha Event payload
7. can store enriched events in SQLite

## Early dependencies

Expected sibling / package dependency:

- `akasha-apis`

V2 uses these adapters from `akasha-apis`:

- `akasha_apis.geo.timezone_lookup.TimezoneLookupAdapter`
- `akasha_apis.astronomy.sunrise_sunset.SunriseSunsetAdapter`
- `akasha_apis.weather.open_meteo.OpenMeteoWeatherAdapter`

## Why this matters

Akasha Time Nexus is not a clock utility.

It is the first system that answers:

> What was the state of time and world when this event happened?

That means every later Akasha system can work with enriched context instead of raw timestamps.

## CLI example

```bash
python -m akasha_time_nexus.cli stamp \
  --timestamp 2026-03-30T20:00:00Z \
  --lat 38.42 \
  --lon -82.44 \
  --event-type observation \
  --title "Test anomaly" \
  --timezone America/New_York
```

To emit an Akasha Event:

```bash
python -m akasha_time_nexus.cli event \
  --timestamp 2026-03-30T20:00:00Z \
  --lat 38.42 \
  --lon -82.44 \
  --event-type observation \
  --title "Test anomaly"
```

To store in SQLite:

```bash
python -m akasha_time_nexus.cli stamp \
  --timestamp 2026-03-30T20:00:00Z \
  --lat 38.42 \
  --lon -82.44 \
  --db nexus.db
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
