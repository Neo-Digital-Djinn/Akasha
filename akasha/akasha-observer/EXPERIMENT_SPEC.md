# Akasha Experiment Specification

Experiments define how discovery engines analyze knowledge structures.

Each experiment must include:

• input knowledge structure  
• discovery engine  
• lenses applied  
• evaluation criteria  
• output record format

---

## Experiment Flow

```
knowledge graph
      ↓
discovery engine
      ↓
lens analysis
      ↓
pattern detection
      ↓
hypothesis candidate
      ↓
experiment record
```

---

## Example Experiment

```yaml
experiment: phase_structure_scan

input:
  knowledge_graph: phase_behavior_domain

engine:
  discovery_engine: constraint_analysis

lenses:
  - physics_lens
  - geometry_lens
  - information_lens

outputs:
  - anomaly_candidates
  - structural_patterns
  - hypothesis_suggestions
```

---

## Experiment Philosophy

Experiments do not prove truth.

They reveal patterns worthy of further investigation.

Human stewards interpret results and guide future discovery.
