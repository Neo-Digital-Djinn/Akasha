# Invariant System Index

This index maps the three documents that together form the Akasha invariant enforcement system.
Read them in order. Together they answer: what, how, and when.

---

## 1. INVARIANTS.md — What

The ten enforceable invariants.
Each is a hard constraint on any entity entering or modifying canon.

Sections:
- I   Structural Integrity (schema, references, unique IDs)
- II  Consistency (no contradictions)
- III Completeness Signals (non-blocking, tracked)
- IV  Provenance (source, timestamp, lineage)
- V   Immutability of Canon History (append-only, no deletion)
- VI  Determinism (same input = same output)
- VII Auditability (diffs required)
- VIII Safety Boundary (experimental ≠ canon)
- IX  Regression Protection (no accepted change breaks prior invariants)
- X   Minimality (new additions must solve a declared gap)

---

## 2. INVARIANT_ENGINE.md — How

The pseudocode pipeline that evaluates candidates against the invariants.

Stages:
```
Discovery → Candidate → VALIDATE (Invariant Engine) → Record → Human Review → Integration → Post-Audit
```

Outputs:
- PASS → eligible for human review
- FAIL → rejected with reasons (logged)
- POST-FAIL → rollback + alert

Implementation: `akasha-alexandria/alexandria/invariants.py`

---

## 3. INTEGRATION_CONTRACT.md — When

The five gates a candidate must clear before entering canon:

1. Passes invariant validation (zero errors)
2. Has complete provenance
3. Solves a declared gap
4. Produces no regression in full invariant suite
5. Is approved in human review

Failure at any gate → reject or rollback, log permanently.

---

## Implementation Map

| Document              | Location                                          | Role             |
|-----------------------|---------------------------------------------------|------------------|
| INVARIANTS.md         | akasha-axioms/INVARIANTS.md                       | Specification    |
| INVARIANT_ENGINE.md   | akasha-axioms/INVARIANT_ENGINE.md                 | Pseudocode spec  |
| INTEGRATION_CONTRACT.md | akasha-axioms/INTEGRATION_CONTRACT.md           | Admission gate   |
| invariants.py         | akasha-alexandria/alexandria/invariants.py        | Implementation   |
| pipeline.py           | akasha-requests/scripts/pipeline.py               | Wired at promote/forge |

---

## Invariant Severity

| Code              | Blocking? | Source Invariant |
|-------------------|-----------|-----------------|
| SCHEMA_FAIL       | Yes       | I               |
| BROKEN_REFERENCE  | Yes       | I               |
| CONTRADICTION     | Yes       | II              |
| NO_PROVENANCE     | Yes       | IV              |
| REDUNDANT         | Yes       | X               |
| REGRESSION        | Yes       | IX              |
