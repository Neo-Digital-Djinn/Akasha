# Architecture

Akasha Attractor is the first analysis engine in Akasha.

## Responsibility

- read persistent events from `akasha-events`
- surface grouped counts
- detect simple burst windows
- remain interpretation-free

## V2 boundary

V2 is intentionally conservative.

It does not infer causes or deep correlations.
It establishes the first real analysis loop on top of the event ledger.
