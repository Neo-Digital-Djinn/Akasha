# Akasha Geometry — Alignment Statement

This system is part of the Akasha ecosystem and aligns with
akasha-axioms, akasha-world, and akasha-constellation.

## Axiom Alignment

**Axiom 1 — Coherence**
The engine detects structural contradictions: lattice violations, role gaps,
and broken expectations. Contradictions are surfaced as findings, not silently ignored.

**Axiom 2 — Discoverability**
Gap pressure fields, isolated node detection, and missing link prediction
are built-in first-class operations. Gaps are signals, not voids.

**Axiom 3 — Alignment**
The engine reads akasha_table and akasha_lattice schemas directly.
All node types and relation types are constrained to declared canonical values.

**Axiom 5 — Traceability**
Every hypothesis produced by the reasoner carries a `falsifier` field.
Every suggestion declares its source signal (topological, role-structural, or compound).
No opaque outputs.

**Axiom 6 — Modularity**
The engine reads from Constellation and proposes structure.
It does not write to Constellation. It does not override placement.
Constellation remains the sole source of truth.

**Axiom 7 — Transparency**
All detection logic is implemented in inspectable Python.
No black-box scoring. All weights and rules are declared in code.

**Axiom 9 — Stewardship**
The engine flags, ranks, and exports hypotheses for human review.
It does not accept or reject hypotheses autonomously.
Final authority remains with the human steward.

**Axiom 10 — Continuity**
Hypothesis exports conform to the Akasha request schema (REQ-format JSON),
ensuring geometry findings accumulate into the broader ecosystem record
rather than being discarded after each run.

## Role Boundary

akasha-geometry is a **constraint and validation engine**.
It is not a visualization tool.
It is not a source of truth.
It proposes. It does not decide.
