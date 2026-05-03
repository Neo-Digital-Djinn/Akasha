# Design — akasha-domain-combinator

## Role
Engine. Composes two or more domain packs into a joint workspace and emits
cross-domain structure maps, tension points, and candidate research questions.

## Inputs
- `root_path` — path to akasha_root
- `domain1 domain2 ...` (optional) — specific domains to combine; defaults to all

## Outputs
For each domain pair:
- overlap map: concept pairs sharing structural tokens, with overlap score
- tension points: structural roles (collapse, transition, equilibrium, etc.) 
  that appear in both domains but under different context
- candidate research questions derived from overlaps and tensions

## Alignment
- Axiom 2 (Discoverability): the central purpose — find structure across domains
- Axiom 4 (Augmentation): enables creation of better research directions
- Axiom 6 (Modularity): reads domain packs without coupling to their internals

## Design Notes
Overlap detection uses token-level matching against shared structural vocabulary.
Tension detection uses a fixed vocabulary of structural role markers from the Akasha Table.
Research questions are generated from the top overlaps and tensions.
All domain pairs are processed; output scales with O(n²) domain pairs.
