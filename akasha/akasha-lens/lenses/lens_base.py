"""
akasha-lens — Base Lens Implementation

Reconciles two lens models:
  - Stone model: projection (raw input → domain-typed state)
  - Akasha model: analysis (knowledge graph → pattern candidates)

Both are valid. Both are lenses. They operate in opposite directions
along the discovery pipeline.

This module provides the base classes for both modes.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class LensMode(Enum):
    PROJECTION = "projection"   # Stone model: structures incoming signal
    ANALYSIS = "analysis"       # Akasha model: reads structure for patterns
    BOTH = "both"


@dataclass
class PatternObservation:
    """
    A structural pattern detected by an analysis lens.
    Not a claim of truth — a claim of structural interest.
    """
    pattern_type: str           # gap | anomaly | analogy | forbidden | candidate
    domain: str
    description: str
    confidence: float           # 0.0 - 1.0
    structural_basis: str       # what in the graph suggested this
    trajectory_note: str = ""   # how this was derived (Axiom 5 — Traceability)


@dataclass
class ProjectionResult:
    """
    A domain-typed state produced by a projection lens.
    Carries provenance of the source observation.
    """
    domain: str
    typed_state: Dict[str, Any]
    source_observation: Dict[str, Any]
    constraints_applied: List[str] = field(default_factory=list)
    admissible: bool = True
    violations: List[str] = field(default_factory=list)


class BaseLens(ABC):
    """
    Base class for all Akasha lenses.

    Subclass and implement the modes you support.
    At minimum, declare your manifest properties.
    """

    # Subclasses must declare these
    name: str = "base"
    domain: str = "general"
    perspective: str = "base perspective"
    mode: LensMode = LensMode.ANALYSIS
    constraint_basis: str = ""

    def project(self, observation: Dict[str, Any]) -> ProjectionResult:
        """
        Mode A: Project unstructured input into domain-typed state.
        Stone model. Override to implement.
        """
        raise NotImplementedError(
            f"Lens '{self.name}' does not implement projection mode."
        )

    def analyze(self, graph: Dict[str, Any]) -> List[PatternObservation]:
        """
        Mode B: Analyze a knowledge graph for patterns, gaps, anomalies.
        Akasha model. Override to implement.
        """
        raise NotImplementedError(
            f"Lens '{self.name}' does not implement analysis mode."
        )

    def __call__(self, input_data: Dict[str, Any]) -> Any:
        """
        Callable interface. Routes to project or analyze based on
        input shape and declared mode.
        """
        if self.mode == LensMode.PROJECTION:
            return self.project(input_data)
        elif self.mode == LensMode.ANALYSIS:
            return self.analyze(input_data)
        else:
            # BOTH: infer from input shape
            if "nodes" in input_data or "edges" in input_data:
                return self.analyze(input_data)
            else:
                return self.project(input_data)

    def manifest(self) -> Dict[str, Any]:
        """Return the lens manifest as a dict."""
        return {
            "name": self.name,
            "domain": self.domain,
            "perspective": self.perspective,
            "mode": self.mode.value,
            "constraint_basis": self.constraint_basis,
        }


class AnalysisLens(BaseLens):
    """
    Convenience base for pure analysis lenses (Mode B).
    """
    mode: LensMode = LensMode.ANALYSIS

    @abstractmethod
    def analyze(self, graph: Dict[str, Any]) -> List[PatternObservation]:
        ...


class ProjectionLens(BaseLens):
    """
    Convenience base for pure projection lenses (Mode A).
    Inherits from Stone's lens pattern.
    """
    mode: LensMode = LensMode.PROJECTION

    @abstractmethod
    def project(self, observation: Dict[str, Any]) -> ProjectionResult:
        ...


class MultiLens:
    """
    Runs multiple lenses over the same input and compares results.

    Agreement between lenses increases candidate confidence.
    Disagreement signals a boundary condition — potentially more
    interesting than agreement.
    """

    def __init__(self, lenses: List[BaseLens]):
        self.lenses = lenses

    def analyze(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run all analysis-mode lenses and return convergence report.
        """
        results: Dict[str, List[PatternObservation]] = {}

        for lens in self.lenses:
            if lens.mode in (LensMode.ANALYSIS, LensMode.BOTH):
                results[lens.name] = lens.analyze(graph)

        return self._convergence_report(results)

    def _convergence_report(
        self,
        results: Dict[str, List[PatternObservation]]
    ) -> Dict[str, Any]:
        """
        Compare results across lenses.
        High agreement = strong candidate signal.
        Disagreement = boundary condition signal.
        """
        all_patterns: List[PatternObservation] = []
        for observations in results.values():
            all_patterns.extend(observations)

        # Group by description similarity (simplified — real impl uses structural sig)
        pattern_counts: Dict[str, int] = {}
        for p in all_patterns:
            key = f"{p.pattern_type}:{p.domain}:{p.description[:40]}"
            pattern_counts[key] = pattern_counts.get(key, 0) + 1

        n_lenses = len(results)
        strong_signals = [k for k, v in pattern_counts.items() if v >= n_lenses * 0.5]
        boundary_signals = [k for k, v in pattern_counts.items() if v == 1]

        return {
            "lenses_run": list(results.keys()),
            "total_observations": len(all_patterns),
            "strong_signals": strong_signals,
            "boundary_conditions": boundary_signals,
            "raw_results": results,
        }
