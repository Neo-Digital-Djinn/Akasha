# Akasha Discovery

The discovery engine of the Akasha ecosystem.

This repository explores unknown structures by examining the knowledge defined in **akasha-world** and identifying potential gaps, patterns, and unexplained relationships.

Discovery proposes hypotheses, not truth.

All proposed discoveries must be reviewed by human stewards before integration into the canonical knowledge registry.

---

## Purpose

Akasha Discovery is designed to:

• detect structural gaps in knowledge  
• generate discovery candidates  
• explore hypothesis spaces  
• record experiments and analyses  

---

## Role in the Akasha Ecosystem

akasha-axioms → governing principles  
akasha-world → canonical knowledge registry  
akasha-discovery → discovery engine  
akasha-constellation → ecosystem map  

Discovery operates between **knowledge** and **understanding**.

---

## Discovery Flow

akasha-world → discovery analysis  
↓  
candidate hypothesis generated  
↓  
human review and validation  
↓  
accepted knowledge added to akasha-world  

Discovery **never writes directly to canonical knowledge**.

Human stewardship is required for all accepted discoveries.

---

## Repository Structure

candidates/  
Proposed discoveries awaiting evaluation.

experiments/  
Experiments and analyses used to test hypotheses.

DISCOVERY_PROCESS.md  
The structured method used by discovery tools.

CANDIDATE_FORMAT.md  
Standard format used to record discovery candidates.

---

## Relationship to Other Repositories

akasha-axioms — defines the governing principles of the system  
akasha-world — contains the canonical model of knowledge  
akasha-constellation — maps the ecosystem and its repositories  

Akasha Discovery is the exploratory layer of the Akasha system.

---

## Engine Role

akasha-discovery is the **gap detection and hypothesis generation engine**.  
It scans the structural lattice defined in akasha-world and surfaces  
coordinates that are theoretically reachable but not yet named or inhabited.

## Why it exists

The canonical registry (akasha-world) only contains what is already known.  
Without an active discovery process, the system would never grow.  
akasha-discovery is the mechanism by which Akasha finds its own blind spots.

## Inputs

- `akasha-world` lattice and domain schemas — defines the space to search  
- `akasha-world/candidates/` — promoted candidates to cross-reference  
- External observations from akasha-anomaly (time-stamped events)  
- Structural analogies from akasha-analogy-engine  
- Cross-domain tensions surfaced by akasha-domain-combinator  

## Memory / Registry

- `candidates/` — proposed discovery candidates (markdown, one per gap)  
- `state/system_state.json` — current system state snapshot  
- `build_outputs/runs/` — timestamped run outputs and proposals  
- `doctrine/` — trajectory, scar, and great-discovery alignment docs  
- `schema/akasha_anatomy.yaml` — expected organ families in a healthy constellation  
- `schema/proposal_contract.yaml` — what a valid candidate proposal must contain  

## Relation Model

Discovery sits between sensing and memory in the system anatomy:

```
sensing (akasha-anomaly, akasha-apis)
      │
akasha-discovery (gap detection, hypothesis generation)
      │
memory (akasha-world, akasha-events)
      │
governance (akasha-gatekeeper, akasha-validation, akasha-axioms invariant engine)
```

## Evaluator

Candidates are evaluated by:

1. `engine/curiosity_engine.py` — scores structural gaps by novelty and bridgeability  
2. `engine/architectural_gap_detector.py` — detects missing system organs  
3. `engine/bridge_detector.py` — finds cross-domain structural matches  
4. Human review (mandatory before any candidate enters canon)  
5. akasha-alexandria invariant engine (automated schema + provenance checks)  

## Outputs

- `candidates/` markdown files — human-readable gap proposals  
- `build_outputs/runs/<timestamp>/candidate_proposals.json` — machine-readable  
- `build_outputs/runs/<timestamp>/summary.json` — run-level statistics  

## Position in Constellation

Role: `engine`  
Layer: `discovery`  
Canonical status: `canonical`  

## Next Steps

- Wire `schema/proposal_contract.yaml` into `run_discovery.py` so all output candidates  
  are validated at generation time  
- Connect akasha-discovery to akasha-gatekeeper so candidates are formally gated  
  before entering `akasha-world/candidates/`  
- Add `engine/organogenesis.py` output directly to `akasha-forge` for auto-scaffolding  
  of detected missing organs  

This repository participates in the Akasha ecosystem and is described by repo-manifest.yaml.
