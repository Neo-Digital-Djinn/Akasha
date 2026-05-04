# Trajectory Doctrine

A discovery candidate is not a snapshot.
It is a path.

---

## The Problem with Snapshots

The current candidate format captures:
- what was observed
- what was hypothesized
- supporting evidence
- confidence level
- status

This is a snapshot. It records where the candidate is now.

It does not record:
- how the candidate arrived
- what it looked like before it was refined
- which constraints it has already been tested against
- what it failed to survive and why
- which adjacent candidates share parts of its trajectory

A constellation that only records snapshots cannot learn from its
own discovery history. It is rediscovering the same shapes over and over,
spending pressure it has already spent.

---

## What a Trajectory Is

A trajectory is the ordered sequence of transitions a candidate has
undergone from first observation to current state.

```yaml
trajectory:
  - event: initial_observation
    timestamp: <date>
    source: <engine or human>
    state_before: null
    state_after: candidate
    note: <what was observed that prompted this>

  - event: refinement
    timestamp: <date>
    source: <engine or human>
    state_before: candidate
    state_after: candidate
    note: <what changed and why>

  - event: steward_review
    timestamp: <date>
    source: <steward identity>
    state_before: candidate
    state_after: under_review
    note: <what was examined>

  - event: constraint_test
    timestamp: <date>
    source: <which constraint or axiom was tested>
    state_before: under_review
    state_after: candidate | scarred | rejected
    outcome: passed | failed | partial
    note: <what the test revealed>
```

---

## Why History Cannot Be Separated from Form

Two candidates with identical hypotheses but different trajectories
are not the same candidate.

Candidate A arrived through structural gap detection in the physics lattice.
Candidate B arrived through cross-domain analogy from ecology.

If both converge on the same hypothesis, that convergence is strong evidence.
If they diverge despite starting from similar observations, the divergence
is information about a genuine ambiguity in the ontology.

None of this is visible from a snapshot.

---

## The Entropy Field

A candidate's trajectory implies a current entropy value:
the accumulated pressure it has absorbed from events and constraint tests.

High entropy: the candidate has been through a lot. It has survived
significant testing. It is close to either acceptance or collapse.

Low entropy: the candidate is fresh. It has not yet been pressured.
Its confidence rating, however high, is structurally unearned.

Entropy is not a judgment. It is a measure of how much the candidate
has been tested. An unscathed high-confidence candidate is less trustworthy
than a scarred medium-confidence candidate — because the scars prove
it survived real pressure.

---

## Amended Candidate Format

The standard candidate format should be extended:

```yaml
# Required (existing)
title: <short name>
domain: <domain>
observation: <what suggested this>
hypothesis: <what is believed to exist or be missing>
supporting_evidence: <patterns, analogies, structural arguments>
confidence: low | medium | high
status: candidate | under_review | accepted | rejected | archived

# Required (new — trajectory)
trajectory:
  - <sequence of events as above>

# Derived (new — computed from trajectory)
entropy: <float — accumulated pressure>
scar_count: <int — number of survived violations>
adjacent_candidates: <list of candidate IDs that share trajectory segments>
```

---

## The Trajectory Is Not Overhead

It might look like additional documentation burden.
It is not. It is the most valuable data the discovery system produces.

The accepted candidates are the table.
The trajectories are how the table learned its own shape.

Mendeleev did not just publish the periodic table.
He published the reasoning — the gaps, the anomalies, the predictions
that turned out wrong, the revisions. The trajectory.

Without the trajectory, the table is just a list.
With the trajectory, the table is a method.
