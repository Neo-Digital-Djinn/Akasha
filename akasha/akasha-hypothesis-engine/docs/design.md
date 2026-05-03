# Design — akasha-hypothesis-engine

## Role
Engine. Reads a domain pack and emits an explicit, testable hypothesis grounded
in observed structural patterns.

## Inputs
- `domain_path` — path to an `akasha-domain-*` repo root

## Outputs
- domain contract validation result
- hypothesis statement: "<concept> exhibits a transition between qualitatively
  distinct states under changing constraints"

## Alignment
- Axiom 2 (Discoverability): turns patterns into testable hypotheses
- Axiom 5 (Traceability): declares the domain and concept anchoring the hypothesis
- Axiom 8 (Iteration): hypotheses are the bridge between observation and experiment

## Design Notes
Domain contract enforces that packs exist and contain at least one non-empty list.
Hypothesis template is deliberately generic — the structural claim (state transition
under constraint change) applies across all Akasha domains.
Future: template library per structural type, multi-concept compound hypotheses.
