# Akasha World

The canonical knowledge registry of the Akasha ecosystem.

Akasha World defines how knowledge is structured, named, and organized across the system. It acts as the shared map of what is known, hypothesized, and discovered.

While the axioms define the rules of the system, the world repository defines the structure of knowledge itself.

---

## Purpose

Akasha World provides:

• a registry of domains and entities  
• naming conventions for knowledge structures  
• schemas describing Akasha repositories  
• the canonical map of the system's knowledge landscape  

---

## Role in the Akasha Ecosystem

akasha-axioms → governs rules  
akasha-world → defines knowledge  
akasha-discovery → explores unknowns  

Akasha World represents the current model of reality understood by the system.

---

## Core Documents

CHARTER.md  
Defines the role and purpose of the knowledge registry.

NAMING.md  
Standardized naming conventions used across Akasha repositories.

repo-manifest.schema.json  
Machine-readable schema describing Akasha repository manifests.

---

## Relationship to Other Repositories

akasha-axioms — governing principles  
akasha-discovery — discovery engine that proposes knowledge candidates  
akasha-constellation — ecosystem map tracking all repositories

---

## Knowledge States

Knowledge within Akasha may exist in several states:

canonical — accepted knowledge  
candidate — proposed discovery  
archived — historical or rejected knowledge  

Human review remains the final authority for promoting candidate knowledge to canonical status.

---

## Engine Role

akasha-world is the **ontology and schema layer** — it is not a running engine.  
It provides the structural definitions that all other engines reference.

## Why it exists

Without a shared definition of what knowledge looks like, each engine would invent  
its own vocabulary. akasha-world provides a single source of truth for:

- domain taxonomy (what subjects Akasha reasons about)  
- lattice grammar (the structural roles entities can occupy)  
- repository manifest schema (what a declared Akasha repo must contain)  
- naming conventions (so repos stay recognisable and composable)

## Inputs

- Amendment proposals from akasha-axioms  
- Discovery candidates promoted from akasha-discovery  
- New domain pack requests from domain-* repos  

## Memory / Registry

- `schema/akasha_lattice.yaml` — structural grammar (phases, stability axes, constraints)  
- `schema/akasha_table.yaml` — node and relation types  
- `domains/` — declared domain lattices (e.g. STONE_DOMAIN_LATTICE.yaml)  
- `candidates/` — promoted candidates awaiting full canonical admission  
- `schemas/repo-manifest.schema.json` — machine-readable manifest schema  

## Relation Model

akasha-world sits at the base of the knowledge stack:

```
akasha-axioms (law)
      │
akasha-world (structure)
      │
akasha-discovery (exploration) ←→ akasha-constellation (map)
      │
all domain engines
```

## Evaluator

There is no runtime evaluator in this repo.  
Structural correctness is enforced by akasha-alexandria's invariant engine,  
which reads the schemas declared here to validate candidates.

## Outputs

- Schema files consumed by all engines  
- Domain lattices consumed by akasha-phase-engine, akasha-analogy-engine, etc.  
- Naming conventions referenced by akasha-forge when generating new repos  

## Position in Constellation

Role: `registry`  
Layer: `knowledge`  
Canonical status: `canonical`  

## Next Steps

- Add `domains/` entries for physics, neuroscience, economics, music (specs exist in domain-* repos)  
- Expand `NAMING.md` to cover the `akasha-*` prefix convention used by all current repos  
- Wire `schemas/repo-manifest.schema.json` into the akasha-gatekeeper validation path  

This repository participates in the Akasha ecosystem and is described by repo-manifest.yaml.
