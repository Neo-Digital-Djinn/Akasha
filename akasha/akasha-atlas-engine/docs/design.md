# Design — akasha-atlas-engine

## Role
Discovery infrastructure. Maps the Akasha knowledge space from live artifacts.

## Why it exists
As Akasha grows, repos, domains, and engines accumulate. Without a cartographer,
the constellation becomes unnavigable. Atlas is that cartographer.
It does not infer or reason — it reads, counts, and reports.

## Inputs
- `akasha/*/repo-manifest.yaml` — all repo declarations
- `akasha/akasha-domain-*/packs/*.yaml` — domain knowledge packs
- `akasha/*/src/main.py` — source files (stub detection)

## Outputs
- Count of mapped repos
- Per-domain structure counts
- List of stub organs (growth frontiers)
- Printed map to stdout

## Alignment
- Axiom 2 (Discoverability): surfaces gaps as growth frontiers
- Axiom 5 (Traceability): reads only declared manifests and packs
- Axiom 7 (Transparency): human-readable output, nothing hidden

## Next steps
- Emit structured JSON map for consumption by akasha-constellation
- Add dependency graph traversal from manifest depends_on fields
- Detect orphan repos (no manifest, no backlinks)
