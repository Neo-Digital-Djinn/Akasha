import time

from core.operator_base import Operator
from core.records import OperatorReport

class OscillationOperator(Operator):
    reads = ["energy", "signal"]
    writes = ["energy"]

    def step(self, world, params):
        x = world.fields.get("x", 1.0)
        v = world.fields.get("v", 0.0)
        signal = world.fields.get("signal", 0.5)

        dt = 0.01
        omega = 1.0 + signal

        dx = v
        dv = -(omega ** 2) * x - 0.1 * v

        x += dx * dt
        v += dv * dt

        world.fields["x"] = x
        world.fields["v"] = v
        world.fields["energy"] = float(0.5 * (x*x + v*v))

    def analyze(self, world):
        energy = float(world.fields["energy"])

        return OperatorReport(
            operator="OscillationOperator",
            role="phase",
            stability="active" if energy > 0.1 else "damped",
            reads=self.reads,
            writes=self.writes,
            values={"energy": energy},
            timestamp_ns=time.time_ns(),
        )
