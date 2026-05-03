# Design — akasha-suggestion-engine

## Role
Orchestration engine. Reads Akasha state and emits ranked next-step suggestions.

## Why it exists
The constellation is large enough to need a planner.
Without one, every branch is a forever-maybe and work stalls.
Suggestion is the practical antidote to constellation sprawl.

## Inputs
- `akasha/akasha-requests/requests/approved/*.json` — open approved requests
- Stub organ detection (same as atlas)
- Empty design docs detection

## Outputs
Ranked list of suggestions with label and summary, printed to stdout.
Ranking: high-priority requests → medium → low → stub organs → missing docs.

## Alignment
- Axiom 4 (Augmentation): helps humans know what to build next
- Axiom 8 (Iteration): keeps the discovery loop moving
- Axiom 10 (Continuity): progress should compound, not stall

## Next steps
- Score by dependency readiness (don't suggest X if X depends on unbuilt Y)
- Accept input text and surface suggestions most relevant to the input
- Emit structured JSON for programmatic consumption
