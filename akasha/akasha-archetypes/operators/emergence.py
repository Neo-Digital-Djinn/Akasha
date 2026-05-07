import numpy as np
import time

from core.operator_base import Operator
from core.records import OperatorReport

class EmergenceOperator(Operator):
    reads = ["field"]
    writes = ["field", "energy"]

    def step(self, world, params):
        field = world.fields["field"]
        n = field.shape[0]
        new = np.zeros_like(field)

        for r in range(n):
            for c in range(n):
                s = np.sum(field[max(0,r-1):r+2, max(0,c-1):c+2]) - field[r,c]
                if field[r,c] == 1 and s in [2,3]:
                    new[r,c] = 1
                elif field[r,c] == 0 and s == 3:
                    new[r,c] = 1

        world.fields["field"] = new
        world.fields["energy"] = float(np.mean(new))

    def analyze(self, world):
        density = float(world.fields["energy"])
        role = "attractor" if density > 0.5 else "phase"

        return OperatorReport(
            operator="EmergenceOperator",
            role=role,
            stability="dynamic",
            reads=self.reads,
            writes=self.writes,
            values={"density": density},
            timestamp_ns=time.time_ns(),
        )
