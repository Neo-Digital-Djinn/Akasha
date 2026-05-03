# Architecture

V2 is the first repo pass where Akasha Time Nexus consumes real adapters from `akasha-apis`.

## Flow

raw event
→ timezone adapter
→ solar adapter
→ weather adapter
→ context bundle
→ Akasha Event export or SQLite storage

## Current boundary

V2 keeps lunar/tide/geomagnetic context conservative.
The important milestone is the living loop, not maximal provider count.
