import json
import hashlib
import random
from dataclasses import dataclass, field
from typing import Dict, Any

import numpy as np

@dataclass
class WorldState:
    seed: int = 42
    t: int = 0
    fields: Dict[str, Any] = field(default_factory=dict)
    meta: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        random.seed(self.seed)
        np.random.seed(self.seed)

    def snapshot(self):
        out = {}
        for k, v in self.fields.items():
            if hasattr(v, "tolist"):
                out[k] = v.tolist()
            else:
                out[k] = v
        return out

    def hash(self):
        payload = json.dumps(self.snapshot(), sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

    def clone(self):
        return WorldState(
            seed=self.seed,
            t=self.t,
            fields=dict(self.fields),
            meta=dict(self.meta),
        )
