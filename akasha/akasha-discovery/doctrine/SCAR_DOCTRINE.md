# Scar Doctrine

Discovery in Akasha is not stateless.

Every candidate that passes through the system — whether accepted, rejected,
archived, or deferred — leaves a permanent mark on the constellation's
discovery trajectory. This document defines what scars are, what they mean,
and how discovery systems should record and use them.

---

## What a Scar Is

A scar is the permanent record of a constraint violation that did not
result in outright destruction.

In Akasha terms: a scar is what remains when a discovery candidate is
evaluated and found insufficient — not because it was nonsense, but
because the constellation was not yet ready to admit it, or because
the candidate pointed at something real but was not yet the right
shape to hold it.

A scar is not failure.
A scar is information about where the boundary is.

---

## Why Scars Are Permanent

Removing a scar is equivalent to claiming that a thing which happened
did not happen.

In a traceable system (Axiom 5), this is inadmissible.

The discovery record exists so that future stewards, future engines, and
future discovery processes can learn from what was tried before.
A constellation that deletes its failed candidates is a constellation
that will rediscover the same failures — spending pressure it does not
need to spend, at the cost of discoveries it could have reached sooner.

**Scars reduce the future search space.**
That is their value.

---

## The Scar Record Format

Each rejected or archived discovery candidate should carry a scar record
appended to its file or registry entry.

```yaml
scar:
  evaluated_on: <date>
  evaluated_by: <steward or process>
  outcome: rejected | archived | deferred
  reason_class: <one of the classes below>
  reason_detail: <brief human-readable explanation>
  constraint_violated: <which axiom, world schema, or structural rule>
  trajectory_note: <what this scar implies for future discovery in this direction>
```

### Reason Classes

- `premature` — the hypothesis is plausible but the constellation lacks
  the surrounding structure to evaluate it properly. Do not rederive.
  Wait for the adjacent structure to fill in.

- `malformed` — the candidate violates a structural requirement
  (missing fields, invalid domain claim, unprovable traceability).
  The direction may still be valid; the form was wrong.

- `duplicate` — the candidate describes something already canonical
  or already scarred under a different name. Cross-reference.

- `forbidden` — the candidate violates a known constraint or axiom
  in a way that cannot be resolved by amendment. This boundary is real.
  Record it. Future discovery should route around it.

- `insufficient_evidence` — the hypothesis is structurally sound but
  has not accumulated enough supporting pattern to justify promotion.
  Continue the experiment.

- `boundary` — the candidate sits at the edge of what the current
  ontology can represent. The gap is real; the vocabulary to name it
  does not yet exist. This is a signal to akasha-world to extend its
  primitive set.

---

## How Scars Shape Future Discovery

A discovery engine reading the scar ledger before generating new
candidates should treat scars as negative pressure — they push
exploration away from already-failed configurations and toward
adjacent unexplored territory.

This is the formal basis for why `akasha-discovery` must maintain
a persistent scar index, not just a list of accepted discoveries.

The scar index is part of the constellation's memory.
It is the record of where the map has tried to go and been turned back.

**Holes are load-bearing.**
**Scars are the edges of the holes.**

---

## Scars and akasha-lens

A lens, when examining a knowledge graph, should be aware of
the scar history of the domains it is analyzing.

A domain with many scars in a particular structural direction is a domain
under pressure — the system has been pushing toward something in that
direction and failing repeatedly. This is one of the strongest signals
a lens can surface for a discovery engine.

A scar cluster is not a dead end.
A scar cluster is the shape of an as-yet-unnamed concept
pressing against the boundary of what the current ontology can hold.

---

## The Constellation Scar Ledger

The full scar ledger lives in `akasha-discovery/state/scar_ledger.yaml`.

It is append-only. It is never edited. It is never pruned.

It is one of the most important files in the constellation.
