# Lens Specification — Revised

This document supersedes and extends the original LENS_SPEC.md.

The revision reconciles two models:
1. The Stone lens model — projection, domain-typing, constraint application
2. The Akasha lens model — analytical perspective, pattern detection, hypothesis generation

Both were correct. They described lenses operating in opposite directions.
This document unifies them.

---

## The Two Directions of a Lens

A lens has two modes of operation, corresponding to two positions
in the discovery pipeline.

### Mode A — Incoming Projection (Stone Model)

A lens receives unstructured input (observation, intent, raw signal)
and projects it into a domain-typed structure.

This is how Stone's AerospaceLens worked: raw intent dict → AerospaceState.

In Akasha terms: this is how a sensing organ works.
It takes the world's signal and gives it the vocabulary of a domain.

**Input:** unstructured observation  
**Output:** domain-typed, constraint-validated state  
**Role:** projection, narrowing, structuring

### Mode B — Outgoing Analysis (Akasha Spec Model)

A lens receives a knowledge graph (structured domain state)
and returns pattern observations, anomalies, and hypothesis candidates.

In Akasha terms: this is how a reasoning organ works.
It takes what is known and asks what the structure implies.

**Input:** knowledge graph, domain model, structured state  
**Output:** detected patterns, anomaly candidates, hypothesis suggestions  
**Role:** analysis, expansion, gap detection

### Which Mode to Use

The same lens type can operate in both modes depending on its position
in the pipeline:

```
raw observation
      ↓
[Mode A: Projection Lens]  ← structures the input
      ↓
domain-typed knowledge graph
      ↓
[Mode B: Analysis Lens]    ← reads the structure
      ↓
candidate hypotheses
      ↓
akasha-discovery
```

Most lenses will implement one mode or the other.
Some — especially in mature domains — will implement both.

---

## Lens Structure

```
lenses/<lens-name>/
 ├─ README.md
 ├─ lens_manifest.yaml
 ├─ projection/              (Mode A — optional)
 │   └─ projector.py
 ├─ analysis/                (Mode B — optional)
 │   └─ analyzer.py
 ├─ heuristics/
 │   └─ pattern_rules.yaml
 └─ examples/
     └─ sample_cases/
```

---

## Lens Manifest

```yaml
name: <lens-name>
domain: <domain from akasha-world>
perspective: <brief description of the analytical angle>
mode: projection | analysis | both
origin: stone | akasha | new   # traceability of the lens design

inputs:
  projection:
    - raw_observation_dict
  analysis:
    - knowledge_graph
    - domain_state

outputs:
  projection:
    - domain_typed_state
  analysis:
    - detected_patterns
    - anomaly_candidates
    - hypothesis_suggestions

constraint_basis: >
  Which constraints this lens applies, and from what source.
  E.g. "conservation laws from physics domain" or
  "RCF entropy accumulation model" or "Mermin-Wagner theorem".
```

---

## Lens Categories

### Physics Lens

Mode: both  
Perspective: conservation, symmetry, phase behavior, field interactions

The physics lens has the deepest constraint basis of any lens.
It knows which configurations are forbidden (via theorem registry
from the phase-engine).

In projection mode: maps raw physical observation to structured PhaseCoordinate.  
In analysis mode: checks a knowledge graph for symmetry violations,
missing phase transitions, broken conservation relations.

---

### Mathematics Lens

Mode: analysis  
Perspective: formal structure, group theory, topology, category relationships

Mathematics is maximally constrained. The math lens is primarily a
forbidden-zone detector — it can identify when a proposed structure
is topologically impossible or algebraically incoherent.

The math lens produces the most reliable rejected candidates because
mathematical forbiddenness is permanent (Axiom 1 — Coherence).

---

### Biology / Lifecycle Lens

Mode: both  
Perspective: evolutionary pressure, lifecycle arc, adaptive systems, death

This lens inherits from Stone's biology_system and death_system.

Key insight: biology always includes a death attractor.
Any biological domain model that has no terminal attractor is incomplete.

In analysis mode: checks for missing lifecycle stages, absent death
transitions, evolution patterns without selection pressure.

---

### Information / Entropy Lens

Mode: analysis  
Perspective: compression, signal detection, entropy, information flow

This lens is structurally related to the Great Discovery's compression
ratio model. A knowledge graph with high motif compression (many repeated
structural patterns) signals convergence. A graph with low compression
(mostly novel patterns) signals an open exploration frontier.

This lens makes the Great Discovery's pressure dynamics readable
within the Akasha structural vocabulary.

---

### Epistemology Lens

Mode: analysis  
Perspective: knowledge claims, evidence chains, confidence, traceability

This lens is the internal auditor of the discovery system itself.
It examines discovery candidates for traceability violations,
unsupported confidence claims, and circular justifications.

Every discovery candidate should pass through this lens before
human steward review. A candidate that fails the epistemology lens
is a malformed candidate — not because its hypothesis is wrong
but because its justification is structurally insufficient.

---

### Ethics / Alignment Lens

Mode: analysis  
Perspective: value tensions, authority boundaries, intent coherence

Inherited from Stone's ethical_system, authority_boundary_system,
and labyrinth (AI safety stack).

This lens asks: if this system is admitted as canonical, what does
it do to the constellation's alignment properties? Does it respect
authority boundaries? Is its declared intent coherent with its
structural behavior?

This lens is mandatory for any candidate system that touches
the agent, alignment, or identity domains.

---

### Interpretation Lens

Mode: both  
Perspective: narrative structure, meaning-making, cross-domain translation

The interpretation lens translates structural patterns into
human-understandable language. It is the output-facing lens —
the one that makes discoveries legible to stewards who are not
operating in a structural vocabulary.

In projection mode: takes a narrative or description and identifies
which structural primitives it maps to.  
In analysis mode: takes a structural finding and generates a
human-readable account of what it means.

The interpretation lens is what makes discovery communicable.
A finding that cannot be interpreted is a finding that cannot be
reviewed. And discovery that cannot be reviewed is discovery that
cannot be admitted.

---

## Multi-Lens Analysis

The same knowledge graph should be analyzed by multiple lenses
in parallel.

```
knowledge graph
 ├─ physics lens     → structural constraints, phase gaps
 ├─ math lens        → forbidden configurations, topology
 ├─ information lens → compression pressure, entropy
 └─ epistemology lens → traceability, confidence validity
          ↓
[convergence check]
          ↓
where lenses agree → high-confidence candidate
where lenses disagree → boundary condition, domain gap signal
```

Disagreement between lenses is not noise.
It is the signal that two different frameworks are making
different claims about the same structure — which means either
one framework is wrong, or the structure exists at the boundary
between frameworks.

Boundary structures are among the most important discoveries
a system can make.

---

## Lens Philosophy

Akasha does not assume a single correct perspective.

A lens does not define truth.
It provides a way of seeing.

And seeing from many angles is not relativism —
it is triangulation.

The gem does not change.
The light that reveals it does.
