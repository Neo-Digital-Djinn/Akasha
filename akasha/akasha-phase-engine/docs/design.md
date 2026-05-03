# Design — akasha-phase-engine

## Role
Engine. Estimates the current phase state of a domain's knowledge landscape.
Models: seed → formation → expansion → complexity → criticality → renewal.

## Inputs
- `domain_path` — path to an `akasha-domain-*` repo root containing `packs/*.yaml`

## Outputs
- pack count and concept count
- current phase estimate
- likely next phase
- entropy score (proxy for conceptual complexity, 0–100)
- stability score (inverse proxy, bounded away from 0)
- sample concept

## Alignment
- Axiom 2 (Discoverability): phase position suggests what kind of work is needed
- Axiom 5 (Traceability): all values derived from observable pack contents
- Axiom 8 (Iteration): phase model is recursive by design

## Design Notes
Phase scoring is heuristic: concept count drives phase index, entropy proxies
for conceptual density. These are declared as heuristics, not measurements.
Future: per-pack phase estimation, cross-domain phase comparison, phase-aware
suggestion weighting.
