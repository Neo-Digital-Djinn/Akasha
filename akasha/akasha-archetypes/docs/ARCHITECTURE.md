# Architecture

The canonical substrate is now centered on WorldState and StepRecord.

All operators:
- declare reads/writes
- emit provenance
- avoid hidden state
- operate deterministically under a fixed seed

Runner owns orchestration and replay logging.
