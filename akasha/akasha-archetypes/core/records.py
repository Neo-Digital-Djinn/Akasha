from dataclasses import dataclass, field
from typing import Dict, Any, List

@dataclass
class OperatorReport:
    operator: str
    role: str
    stability: str
    reads: List[str]
    writes: List[str]
    values: Dict[str, float]
    timestamp_ns: int

@dataclass
class StepRecord:
    step: int
    world_hash_before: str
    world_hash_after: str
    reports: List[OperatorReport] = field(default_factory=list)
    snapshot: Dict[str, Any] = field(default_factory=dict)
