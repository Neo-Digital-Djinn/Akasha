"""
Capital Suite v3 — signals.py
DivergenceDetector: spots mismatches between sub-indicators that often
precede regime transitions.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from core.config import (
    DIVERGENCE_FUNDING_FLIP_THRESHOLD,
    DIVERGENCE_DOM_SPIKE_THRESHOLD,
    DIVERGENCE_VOL_DROP_WHILE_INFLOW,
)


@dataclass
class Divergence:
    kind: str          # 'FUNDING_FLIP' | 'DOM_SPIKE' | 'VOL_COMPRESSION' | 'SCORE_INVERSION'
    severity: float    # 0-1
    description: str

    def display(self) -> str:
        bar = "█" * int(self.severity * 10) + "░" * (10 - int(self.severity * 10))
        return f"  [{self.kind:<20}]  {bar}  {self.severity:.2f}  {self.description}"


class DivergenceDetector:
    """
    Compares flow sub-components to surface structural inconsistencies.

    Divergences don't predict direction — they flag when the regime signal
    is internally contradicted, warranting reduced confidence weighting.
    """

    def __init__(self):
        self._prev_dom: Optional[float] = None
        self._prev_score: Optional[float] = None

    def evaluate(
        self,
        score: float,
        inflow: float,
        outflow: float,
        funding: float,
        vol: float,
        dom: float,
    ) -> List[Divergence]:
        found: List[Divergence] = []

        # 1. Funding flip — funding disagrees strongly with net flow direction
        net_flow = inflow - outflow
        if abs(funding - net_flow) > DIVERGENCE_FUNDING_FLIP_THRESHOLD * 2:
            sev = min(1.0, abs(funding - net_flow) / 2.0)
            found.append(Divergence(
                kind="FUNDING_FLIP",
                severity=round(sev, 3),
                description=f"funding={funding:+.2f} vs net_flow={net_flow:+.2f}",
            ))

        # 2. Dom spike — sudden BTC dominance jump (rotation signal)
        if self._prev_dom is not None:
            delta = abs(dom - self._prev_dom)
            if delta >= DIVERGENCE_DOM_SPIKE_THRESHOLD:
                sev = min(1.0, delta / 15.0)
                found.append(Divergence(
                    kind="DOM_SPIKE",
                    severity=round(sev, 3),
                    description=f"dom Δ={delta:+.2f}% ({self._prev_dom:.1f}→{dom:.1f})",
                ))

        # 3. Vol compression during inflow — inflow without vol = weak conviction
        if score > 0.2 and vol < DIVERGENCE_VOL_DROP_WHILE_INFLOW:
            sev = round((0.2 - vol) / 0.2, 3)
            found.append(Divergence(
                kind="VOL_COMPRESSION",
                severity=min(1.0, sev),
                description=f"score={score:+.3f} but vol={vol:.3f} (low conviction inflow)",
            ))

        # 4. Score inversion — score flipped sign vs previous tick
        if self._prev_score is not None:
            if self._prev_score > 0.2 and score < -0.2:
                found.append(Divergence(
                    kind="SCORE_INVERSION",
                    severity=round(min(1.0, abs(score - self._prev_score)), 3),
                    description=f"score flipped {self._prev_score:+.3f}→{score:+.3f}",
                ))
            elif self._prev_score < -0.2 and score > 0.2:
                found.append(Divergence(
                    kind="SCORE_INVERSION",
                    severity=round(min(1.0, abs(score - self._prev_score)), 3),
                    description=f"score flipped {self._prev_score:+.3f}→{score:+.3f}",
                ))

        self._prev_dom   = dom
        self._prev_score = score
        return found
