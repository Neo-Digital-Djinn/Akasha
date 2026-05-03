# Design — akasha-edge-generator

## Role
Discovery engine. Generates candidate structural edges between concepts across
Akasha domain packs.

## Why it exists
Akasha can read existing domain packs and reason within them (via akasha-analogy-engine).
But the missing move is *proposing new links between them*. The edge generator is
the first organ that can suggest structure that does not yet exist in the packs.

## Inputs
- All available `akasha-domain-*/packs/*.yaml` files (structures + examples)
- Optional seed concept (free-text input, used to bias which pairs are surfaced)
- Optional count `n` (default 5 edges)

## Outputs
For each edge:
```
source: {domain, structure}
relation: <Akasha Table relation class>
target: {domain, structure}
confidence: float (0–1)
rationale: one-sentence justification
provenance: string identifying the generator + method
```

## Method
1. Load all domain packs, collect structure lists per domain
2. Build cross-domain pair candidates
3. If a seed concept is given, rank pairs by token overlap with seed
4. Sample N pairs, assign relation class + confidence via domain affinity table
5. Sort by confidence descending, emit

## Relation classes used
From AKASHA_TABLE.md: couples_to, transitions_to, resonates_with, constrains,
emerges_from, tends_toward, signals, propagates_through.

## Alignment
- Axiom 2 (Discoverability): gaps are signals — this engine turns missing edges into candidates
- Axiom 5 (Traceability): every edge declares provenance and rationale
- Axiom 6 (Modularity): pure input/output, no side effects

## Known limitations
- Confidence is currently heuristic (domain affinity table + jitter), not empirically derived
- Relation assignment is sampled, not reasoned — a future version should use structural matching
- Pairs are sampled from a candidate list, not exhaustively ranked

## Next steps
- Feed output into akasha-hypothesis-engine (REQ-010)
- Validate edges against akasha-world lattice schema
- Replace affinity heuristic with structural similarity scoring
