# Akasha World Invariants (Enforceable)

These invariants are executable constraints. Violation = automatic rejection or rollback.

## I — Structural Integrity
- All entities MUST conform to schema.
- All references MUST resolve (no dangling pointers).
- All IDs MUST be unique and stable.

## II — Consistency
- No entity may contain mutually exclusive properties.
- No relation may contradict another accepted relation.
- Canon MUST remain logically satisfiable.

## III — Completeness Signals (Non-blocking but tracked)
- Symmetry groups SHOULD be closed.
- Taxonomies SHOULD not have orphan nodes.
- Known pattern classes SHOULD be filled or explicitly marked incomplete.

## IV — Provenance
- Every entity MUST include provenance:
  - source: observation | derivation | simulation | synthesis
  - timestamp
  - lineage (parent or origin reference)

## V — Immutability of Canon History
- Canon entries are append-only.
- Edits create new versions; old versions persist.
- Deletion is forbidden; only deprecation allowed.

## VI — Determinism
- Same input + same world state MUST produce identical outputs.
- Non-deterministic processes MUST be isolated and labeled.

## VII — Auditability
- Every change MUST produce a diff.
- Diffs MUST be human-readable and machine-parseable.

## VIII — Safety Boundary
- Experimental artifacts MUST NOT enter canon.
- Clear separation: /world (canon) vs /candidates (non-canon)

## IX — Regression Protection
- No accepted change may break existing invariants.
- Full invariant suite MUST run post-integration.

## X — Minimality
- New additions MUST solve a specific gap.
- Redundant entities are rejected unless justified.

