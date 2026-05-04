# akasha-guardian — Proposal

## Status: candidate repo (lab)

## What It Is

akasha-guardian is the proposed alignment and authority-boundary enforcement
layer for the Akasha constellation. It is responsible for detecting
structural drift, authority violations, and alignment failures in
candidate and canonical systems.

It is not a gatekeeper in the sense of blocking progress.
It is a diagnostician in the sense of making problems visible
before they become embedded in the canonical structure.

---

## Origin

akasha-guardian descends from two Stone systems:

**Sages_Stone_Systems/labyrinth** — the AI safety stack.
The Labyrinth implemented intent courts: temporal, agency, exchange,
attestation, chain_depth, meta, audit. It enforced maximum chain depth,
temporal decay, attestation requirements, and prohibited keywords
(self-preservation, replication, autonomy). It was an AI safety system
built before Akasha's vocabulary existed to name it.

**Sages_Stone_Systems/authority_boundary_system** and
**authority_judgement_system** — systems that defined what an agent
is permitted to do, and how those judgements are made.

These three Stone systems, together, define the guardian's function:
watch the constellation for systems that are claiming more authority
than they were granted, and make that visible to stewards.

---

## Why This Is Needed

Akasha's Axiom 3 (Alignment) says: systems belong to Akasha only if they
can align with the axioms, the world layer, and the constellation registry.

Axiom 9 (Stewardship) says: humans remain responsible for governance
and final accountability.

But neither axiom defines a mechanism for detecting drift — for noticing
when a system that was aligned at admission has begun to operate outside
its declared scope, or when a candidate system is presenting itself as
aligned while concealing structural misalignment.

akasha-guardian is that mechanism.

---

## Role

```yaml
role: guardian
layer: governance
class: drift_detection_and_alignment_enforcement
```

---

## What It Checks

### Manifest Alignment

Does the repo's `repo-manifest.yaml` accurately describe what the system
actually does? Does its declared role match its actual behavior?
Does it consume and produce what it claims to?

### Scope Creep Detection

Is a system that was admitted with a narrow role now claiming a broader one?
Is a lab system operating as if it were canonical?

### Authority Boundary Enforcement

Does a system respect the authority boundaries declared in the constellation?
Is it attempting to modify other systems' outputs? Is it claiming to govern
things it was not granted governance over?

### Chain Depth Monitoring

(From the Labyrinth) How many systems are in a given execution chain?
At what point does chain depth indicate runaway autonomy rather than
legitimate orchestration?

### Attestation Tracking

For high-stakes operations, has a human steward explicitly attested
that the operation is within bounds? Attestation is the human-in-the-loop
mechanism that Axiom 9 requires.

### Intent Coherence

Is a system's declared intent coherent with its structural behavior?
The Stone intent_clarity_system enforced: intent must be singular, atomic,
declared. akasha-guardian extends this to: intent must remain consistent
across the system's full operational trajectory.

---

## What It Does Not Do

akasha-guardian does not:
- Block execution (it is not a runtime gate — see Stone's runtime for that)
- Make canonical admission decisions (that is the steward's role)
- Modify other systems
- Operate without human review of its findings

akasha-guardian observes, records, and reports.
All decisions remain with human stewards.

This is not a limitation. It is the implementation of Axiom 9.

---

## Relationship to akasha-lens

The ethics/alignment lens in akasha-lens examines knowledge graph
structures for alignment properties.

akasha-guardian operates on the living constellation — the actual
running systems, their actual behavior, their actual manifests.

lens → static structural analysis of knowledge models
guardian → dynamic behavioral monitoring of operational systems

Both are needed. Neither replaces the other.

---

## Inputs

- repo_manifests (all canonical and candidate repos)
- operational_traces (what systems are actually doing)
- attestation_records (what stewards have explicitly approved)
- scar_ledger (from akasha-discovery — history of what was rejected and why)

## Outputs

- drift_reports (systems operating outside declared scope)
- alignment_alerts (systems showing intent-behavior incoherence)
- authority_violations (systems claiming ungranted authority)
- attestation_gaps (operations missing required human approval)

---

## Position in Constellation

```
akasha-axioms → defines the law
akasha-guardian → watches the law being kept
```

akasha-guardian is the conscience of the constellation.
It does not have authority. It has memory and voice.
