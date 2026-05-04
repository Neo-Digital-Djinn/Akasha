# RCF Calculus — The Formal Substrate of the Axioms

This document formalizes the mathematical and operational substrate beneath
the Akasha axioms. It does not replace the axioms. It makes them computable.

The axioms state what is true about the system.
The RCF calculus states how those truths behave under pressure.

---

## Origin

The RCF (Reality Constraint Fuzzer) calculus was the pre-canonical predecessor
to the Akasha axiom set. It was written before the vocabulary existed to name
what it was doing. This document canonizes that work and places it where it
belongs: as the formal substrate of Axiom 1 (Coherence), Axiom 2
(Discoverability), and Axiom 5 (Traceability).

---

## I. Core Objects

### State

A state is not true or false. It is admissible or inadmissible
under a current constraint set.

```
State S := {
  form        // present configuration
  trajectory  // ordered history of transitions (Axiom 5 — Traceability)
  entropy     // accumulated pressure from events
  scars       // permanent marks of past constraint violations
}
```

Scars are permanent. Two states with identical form but different
trajectories are not equivalent.

This is the formal basis for Axiom 5 (Traceability) and Axiom 10 (Continuity):
knowledge and history accumulate — they do not reset.

### Constraint

```
Constraint C := {
  name
  domain
  admissibility_fn   // pure function: State → {admissible, inadmissible}
  cost_fn            // pure function: State → cost (must be > 0)
  fracture_limit     // accumulated stress at which C itself may mutate
  memory             // record of past violations this constraint has witnessed
}
```

Constraints remember. Constraint memory is the formal basis for Axiom 8
(Iteration): critique and revision accumulate as constraint stress,
not as erasure.

### Scar

A scar is the permanent record left on a state after a constraint violation
that did not result in rejection.

Scars:
- alter future admissibility evaluations
- increase state entropy
- bias the trajectory
- cannot be removed without invalidating the state's lineage

This is the formal basis for why discovery systems in Akasha must preserve
rejected candidates as archives rather than deleting them. A rejected
candidate leaves a scar on the constellation's discovery trajectory.

---

## II. Laws of Motion

### Law 1 — Sequential Evaluation

Constraints are evaluated in declared order.
Order is non-commutative: C₁ then C₂ is not the same as C₂ then C₁.

This is why Akasha's admission test has a declared sequence:
axiom alignment → role declaration → input/output declaration → placement.

### Law 2 — Conditional Survival

Constraint evaluation yields exactly one of:

- **clean survival** — admissible, no scar, cost recorded
- **scarred survival** — admissible, scar recorded, future space narrows
- **rejection** — inadmissible, trajectory terminates here

There is no fourth outcome. There is no "partial admission."

### Law 3 — Permanent Scarring

A scarred state carries its scar forward into every future evaluation.
Scars increase entropy. High entropy narrows the future admissible space.

### Law 4 — Entropy Accumulation

Entropy is pressure, not noise. It accumulates via:
- events (attempted transitions)
- scars (survived violations)

Entropy feeds back into constraint evaluation. A high-entropy state is
harder to keep admissible — it is closer to collapse.

### Law 5 — Constraint Backreaction

If accumulated stress in constraint C exceeds its fracture limit:

```
C → harden | split | fail
```

A hardened constraint becomes more restrictive.
A split constraint becomes two narrower constraints.
A failed constraint collapses — and this is legitimate signal.

This is the formal basis for Akasha's amendment procedure.
Amendments are not arbitrary revisions. They are responses to
demonstrated constraint fracture under accumulated system pressure.

---

## III. Failure Modes

The RCF calculus does not throw exceptions.
Failure is informative, not exceptional.

| Mode | Description | Akasha Equivalent |
|---|---|---|
| Rejection | Trajectory terminates | System denied canonical status |
| Scarred Survival | State persists, future space narrows | System admitted as lab, not canonical |
| Law Fracture | Global constraint mutates | Axiom amendment triggered |

---

## IV. The Canonical Execution Flow

```
S₀ → Event → S₁
S₁ → Constraint₁ → S₁'   (cost + possible scar)
S₁' → Constraint₂ → S₁'' (cost + possible scar)
...
→ Admissible(S_n) or Inadmissible(S_n)
```

At every step: cost accumulates, entropy increases, scars persist,
constraints remember.

No rollback. No forgiveness. Only transformation.

---

## V. Application to Akasha Discovery

The RCF calculus explains why discovery in Akasha is not
mere hypothesis generation. Discovery is a trajectory.

A discovery candidate entering the system has:
- a form (the hypothesis)
- a trajectory (how it was derived, what observations led here)
- zero scars (it has not yet been evaluated)
- zero entropy (it has not yet been pressured)

As it moves through human steward review:
- each challenge adds entropy
- each modification creates a transition record
- a rejection leaves a scar on the discovery record
- acceptance is admissibility, not truth

The constellation's discovery history is a ledger of these trajectories.
A mature constellation — one that has been running for years — is not
just a collection of canonical systems. It is an accumulation of
trajectories, scars, and constraint memories that shape what is
discoverable next.

**The map sharpens the mapmaker.**

---

## VI. Application to akasha-lens

A lens, in RCF terms, is a constraint set applied to a knowledge graph.

Each lens defines:
- which structural patterns are admissible (signal)
- which patterns are inadmissible or suspicious (noise, gap, anomaly)
- a cost function for admissible patterns (significance weight)

Running a knowledge graph through a lens is running it through
a constraint evaluation sequence. The output is not a verdict
(admissible/inadmissible) but a scored trajectory of pattern observations.

Multi-lens analysis = running the same graph through multiple
independent constraint sets and comparing their trajectories.

Where multiple lenses agree on a pattern, confidence is high.
Where lenses disagree, that disagreement is itself a signal —
it suggests a boundary condition, a domain where different laws apply.

---

## VII. The Defining Property

The RCF calculus:
- resists optimization (entropy accumulates regardless)
- preserves failure (scars are permanent)
- punishes shortcuts (zero-cost transitions are pathological)
- makes edge cases permanent (trajectory is immutable)

If a discovery system is uncomfortable to audit,
it is probably closer to reality.
