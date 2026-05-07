import numpy as np
import time

from core.operator_base import Operator
from core.records import OperatorReport

class ResonanceOperator(Operator):
    reads = ["phase"]
    writes = ["phase", "signal"]

    def step(self, world, params):
        theta = world.fields["phase"]
        omega = world.fields["omega"]
        K = 0.5
        dt = 0.05
        N = len(theta)

        for i in range(N):
            coupling = sum(np.sin(theta[j] - theta[i]) for j in range(N))
            theta[i] += (omega[i] + K * coupling / N) * dt

        r = abs(sum(np.exp(1j * theta)) / N)
        world.fields["phase"] = theta
        world.fields["signal"] = float(r)

    def analyze(self, world):
        r = float(world.fields["signal"])

        return OperatorReport(
            operator="ResonanceOperator",
            role="phase",
            stability="coherent" if r > 0.7 else "disordered",
            reads=self.reads,
            writes=self.writes,
            values={"order_parameter": r},
            timestamp_ns=time.time_ns(),
        )
