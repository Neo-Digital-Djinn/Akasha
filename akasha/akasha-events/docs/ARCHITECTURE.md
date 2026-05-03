# Architecture

Akasha Events is the memory layer.

## Responsibility

- define the canonical event shape
- store events durably
- expose simple query access
- remain interpretation-free

## V2 boundary

V2 keeps storage deliberately simple:

- SQLite
- insert
- list
- recent

This is enough to support the first living Akasha loop and the first pattern engine work in `akasha-attractor`.
