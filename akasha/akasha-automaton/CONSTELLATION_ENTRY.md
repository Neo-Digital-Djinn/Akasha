# Constellation Entry — akasha-automaton

This file contains the registry patch to formally admit `akasha-automaton`
into the Akasha Constellation.

## Patch: akasha-constellation/registry.yaml

Add the following entry under the `repos:` key:

```yaml
  akasha-automaton:
    role: engine
    layer: simulation
    description: >
      Emergent-systems simulation and observation engine. Eight cellular automaton
      engines (Conway's Life, Reaction-Diffusion, Lenia, Brian's Brain, WireWorld,
      Langton's Ant, Cyclic CA, SmoothLife), nine render modes, genetic rule
      evolution, multi-universe forking, time-travel history scrubbing, AI pattern
      analysis, Pattern DNA metrics, and a living README grid updated by GitHub
      Actions. Produces grid snapshots, Wolfram classifications, evolved rule sets,
      and Akasha-compatible emergence event payloads for akasha-events ingestion.
    depends_on:
      - akasha-events
      - akasha-axioms
    inputs:
      - rule_definitions
      - initial_grid_states
      - rle_pattern_strings
      - simulation_parameters
    outputs:
      - grid_state_snapshots
      - pattern_dna_metrics
      - wolfram_class_classifications
      - evolved_rule_sets
      - emergence_event_payloads
      - ai_pattern_analyses
    canonical_status: canonical
    maturity: stable
    source_lineage: Cellular_Automation_Explorer (ULTRAVERSE v10 / v8)
```

## Admission Checklist

- [x] Axiom alignment documented in `docs/AKASHA_ALIGNMENT.md`
- [x] `repo-manifest.yaml` complete with all required fields
- [x] Role declared: `engine`
- [x] Layer declared: `simulation`
- [x] Inputs declared
- [x] Outputs declared
- [x] Dependencies declared
- [x] Canonical status: `canonical`
- [x] Human steward declared
- [x] Alignment statement present
- [x] Admission test passed (see `docs/AKASHA_ALIGNMENT.md`)

## System Organ Type

`akasha-automaton` is a **system organ** — a canonical, active member of the
Akasha constellation with declared role, layer, interfaces, and alignment.

It is not a lab, not an experiment, not a stub.
It is a working emergent-systems simulation instrument, fully integrated.

## Constellation Relationship Notes

`akasha-automaton` and `akasha-capital` are **sibling analysis organs** in
the constellation. Both occupy the observation/analysis band — one observing
capital flow dynamics, one observing emergent computational dynamics. Both
emit Akasha-compatible event payloads to `akasha-events`. Both are augmentation
instruments that expand human observational capacity without replacing human judgment.
