from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class HypothesisBranch:
    branch_id: str
    source_path: str
    transform_name: str
    transform_params: dict[str, Any]
    output_text: str
    score: dict[str, Any]

    def to_dict(self) -> dict:
        return asdict(self)
