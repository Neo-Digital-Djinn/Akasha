# Invariant Engine (Concept Spec)

## Purpose
Evaluate all candidate and integration changes against invariants.

## Pipeline Hook

Discovery → Candidate → VALIDATE (Invariant Engine) → Record → Human Review → Integration → Post-Audit

## Pseudocode

def validate(candidate, world):
    errors = []

    if not schema_valid(candidate):
        errors.append("SCHEMA_FAIL")

    if not references_resolve(candidate, world):
        errors.append("BROKEN_REFERENCE")

    if contradicts_world(candidate, world):
        errors.append("CONTRADICTION")

    if not has_provenance(candidate):
        errors.append("NO_PROVENANCE")

    return errors


def integrate(candidate, world):
    errors = validate(candidate, world)
    if errors:
        reject(candidate, errors)
        return

    new_world = apply(candidate, world)

    if not run_invariants(new_world):
        rollback()
        raise Exception("POST_INTEGRATION_FAILURE")

    commit(new_world)

## Outputs
- PASS → eligible for human review
- FAIL → rejected with reasons
- POST-FAIL → rollback + alert

