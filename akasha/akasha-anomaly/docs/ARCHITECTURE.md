# Architecture

Akasha Anomaly is intentionally small.

It performs only three responsibilities:

1. Accept human observations
2. Pass them through akasha-time-nexus
3. Emit Akasha Event records

All heavy enrichment logic lives in akasha-time-nexus.
