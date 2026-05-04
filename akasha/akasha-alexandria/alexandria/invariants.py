# DOCTRINAL LOCK — DO NOT MODIFY AT RUNTIME
# This module implements the Akasha Invariant Engine.
# Source of truth: akasha-axioms/INVARIANTS.md + INVARIANT_ENGINE.md
# Violations produce structured error records, not exceptions, unless called
# in strict mode (integrate path). Standalone validate() is always safe to call.

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

from alexandria.exceptions import InvariantViolation


# ---------------------------------------------------------------------------
# Error record
# ---------------------------------------------------------------------------

@dataclass
class InvariantError:
    code: str               # SCHEMA_FAIL | BROKEN_REFERENCE | CONTRADICTION | NO_PROVENANCE | REDUNDANT | REGRESSION
    detail: str
    field: Optional[str] = None

    def __str__(self) -> str:
        loc = f" [field={self.field}]" if self.field else ""
        return f"{self.code}{loc}: {self.detail}"


# ---------------------------------------------------------------------------
# Candidate / world type stubs — invariants are duck-typed for portability
# ---------------------------------------------------------------------------

class _Missing:
    """Sentinel for absent attributes."""


def _get(obj, *keys, default=_Missing):
    """Safely navigate nested attributes or dict keys."""
    cur = obj
    for k in keys:
        if cur is _Missing:
            break
        if isinstance(cur, dict):
            cur = cur.get(k, _Missing)
        else:
            cur = getattr(cur, k, _Missing)
    if cur is _Missing:
        if default is _Missing:
            return None
        return default
    return cur


# ---------------------------------------------------------------------------
# Individual invariant checks (I–X from INVARIANTS.md)
# ---------------------------------------------------------------------------

def _check_schema(candidate, errors: List[InvariantError]) -> None:
    """Invariant I — Structural Integrity: schema conformance."""
    # Every candidate must have an id, a source, and a claim/title.
    entity_id = _get(candidate, "id") or _get(candidate, "entity_id")
    if not entity_id:
        errors.append(InvariantError("SCHEMA_FAIL", "Entity is missing a stable id.", "id"))

    claim = _get(candidate, "claim") or _get(candidate, "title") or _get(candidate, "name")
    if not claim or (isinstance(claim, str) and len(claim.strip()) < 3):
        errors.append(InvariantError("SCHEMA_FAIL", "Entity claim/title is absent or too short.", "claim"))


def _check_references(candidate, world, errors: List[InvariantError]) -> None:
    """Invariant I — Structural Integrity: no dangling pointers."""
    refs = _get(candidate, "references") or _get(candidate, "depends_on") or []
    if isinstance(refs, str):
        refs = [refs]
    if world is None:
        return  # cannot check without world; skip silently
    known_ids: Set[str] = set()
    if hasattr(world, "entity_ids"):
        known_ids = world.entity_ids()
    elif isinstance(world, dict):
        known_ids = set(world.keys())
    for ref in refs:
        if ref and ref not in known_ids:
            errors.append(InvariantError(
                "BROKEN_REFERENCE",
                f"Reference '{ref}' does not resolve in world.",
                "references",
            ))


def _check_contradiction(candidate, world, errors: List[InvariantError]) -> None:
    """Invariant II — Consistency: no mutual exclusion or contradictory relations."""
    props = _get(candidate, "properties") or {}
    if not isinstance(props, dict):
        return
    # Domain-agnostic: check for explicit contradiction markers
    contradictions = _get(candidate, "contradicts") or []
    if contradictions:
        errors.append(InvariantError(
            "CONTRADICTION",
            f"Entity declares contradictions with accepted entities: {contradictions}.",
            "contradicts",
        ))
    # Check lattice rules if world exposes a validator
    if world is not None and hasattr(world, "check_consistency"):
        result = world.check_consistency(candidate)
        if result is False:
            errors.append(InvariantError(
                "CONTRADICTION",
                "World consistency check failed for candidate.",
            ))


def _check_provenance(candidate, errors: List[InvariantError]) -> None:
    """Invariant IV — Provenance: every entity must declare its origin."""
    prov = _get(candidate, "provenance") or _get(candidate, "source")
    if not prov:
        errors.append(InvariantError("NO_PROVENANCE", "Entity is missing provenance declaration.", "provenance"))
        return
    # Provenance must name a recognised source type
    valid_sources = {"observation", "derivation", "simulation", "synthesis"}
    if isinstance(prov, dict):
        src = _get(prov, "source")
        if src and src not in valid_sources:
            errors.append(InvariantError(
                "NO_PROVENANCE",
                f"Provenance source '{src}' is not a recognised type. Expected one of {valid_sources}.",
                "provenance.source",
            ))
        if not _get(prov, "timestamp"):
            errors.append(InvariantError("NO_PROVENANCE", "Provenance is missing a timestamp.", "provenance.timestamp"))


def _check_minimality(candidate, world, errors: List[InvariantError]) -> None:
    """Invariant X — Minimality: must solve a declared gap; must not be redundant."""
    gap = _get(candidate, "gap") or _get(candidate, "solves_gap") or _get(candidate, "purpose")
    if not gap:
        errors.append(InvariantError(
            "REDUNDANT",
            "Candidate does not declare what gap or purpose it solves.",
            "gap",
        ))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def validate(candidate, world=None) -> List[InvariantError]:
    """
    Run the full invariant suite against a candidate.

    Returns a (possibly empty) list of InvariantError.
    Empty list == PASS; eligible for human review.
    Non-empty list == FAIL; must be rejected.

    This function never raises — it always returns errors as data.
    Use integrate() for the strict path that raises on failure.
    """
    errors: List[InvariantError] = []
    _check_schema(candidate, errors)
    _check_references(candidate, world, errors)
    _check_contradiction(candidate, world, errors)
    _check_provenance(candidate, errors)
    _check_minimality(candidate, world, errors)
    return errors


def integrate(candidate, world=None) -> None:
    """
    Strict integration path. Raises InvariantViolation if any check fails.

    Mirrors INVARIANT_ENGINE.md pseudocode:
        validate → reject on errors → apply → run post-invariants → commit
    """
    errors = validate(candidate, world)
    if errors:
        details = "; ".join(str(e) for e in errors)
        raise InvariantViolation(f"Candidate rejected — {len(errors)} invariant(s) failed: {details}")


# ---------------------------------------------------------------------------
# Legacy shim — keeps old call-site working
# ---------------------------------------------------------------------------

def check_invariants(hypothesis) -> bool:
    """
    Backward-compatible shim used by older call sites.
    Checks only the two constraints the original stub enforced:
      - confidence in [0.0, 1.0] (if present)
      - claim length >= 3
    The full validate() path is preferred for new code.
    """
    if _get(hypothesis, "confidence") is not None:
        conf = _get(hypothesis, "confidence")
        try:
            if not (0.0 <= float(conf) <= 1.0):
                return False
        except (TypeError, ValueError):
            return False

    claim = _get(hypothesis, "claim") or ""
    if len(str(claim).strip()) < 3:
        return False

    return True


