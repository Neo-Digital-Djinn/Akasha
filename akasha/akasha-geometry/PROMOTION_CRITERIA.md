# Promotion Criteria

Current status: `experimental`

## To reach `prototype`

- [ ] Integration test against a real Constellation graph (not synthetic test data)
- [ ] Reasoner hypotheses reviewed and validated by a human steward
- [ ] At least one GEO-HYP accepted and acted on by akasha-forge or akasha-requests
- [ ] `repo-manifest.yaml` reviewed and approved

## To reach `canonical`

- [ ] All prototype criteria met
- [ ] Zero lattice violations in engine's own structural model
- [ ] Deterministic output confirmed across repeated runs on same graph
- [ ] Dependency on akasha-constellation formalized with a declared adapter
- [ ] Amendment to akasha-world REPO_CLASSES.md to add `geometry-engine` as a recognized class
- [ ] Alignment statement reviewed and countersigned by steward

## Admission Test (per akasha-axioms SYSTEM_REQUIREMENTS)

1. Does it align with the axioms? → Yes (see ALIGNMENT.md)
2. Does it have a declared role? → Yes (constraint + validation engine)
3. Does it declare inputs and outputs? → Yes (see repo-manifest.yaml)
4. Can it be placed in the constellation? → Yes (depends_on declared)
5. Can its purpose be explained clearly? → Yes (see GEOMETRY.md and README)
