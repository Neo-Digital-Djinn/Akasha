# Design — akasha-analogy-engine

## Role
Engine. Generates structurally grounded analogies from a domain pack.

## Inputs
- `domain_path` — path to an `akasha-domain-*` repo root containing `packs/*.yaml`
- `seed` (optional) — free-text input from the pipeline; anchors the analogy concept

## Outputs
Printed to stdout:
- anchor concept (domain structure most relevant to seed)
- structural label (the Akasha Table primitive being exemplified)
- analogy statement in natural language

## Alignment
- Axiom 2 (Discoverability): selects the concept most resonant with the input
- Axiom 5 (Traceability): declares structural type of each analogy
- Axiom 7 (Transparency): output is human-readable and inspectable

## Design Notes
Concept selection uses token overlap between seed and domain concept names.
Template selection is seeded by concept+input for deterministic replay.
Templates are grounded in Akasha Table structural primitives (attractor, threshold,
resonance, emergence, coupling, constraint, gradient, hysteresis, symmetry-breaking).
