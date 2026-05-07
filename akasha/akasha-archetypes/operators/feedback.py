import random
import time

from core.operator_base import Operator
from core.records import OperatorReport

class FeedbackOperator(Operator):
    reads = ["signal"]
    writes = ["signal"]

    def step(self, world, params):
        signal = world.fields.get("signal", 0.5)
        noise = (random.random() - 0.5) * 0.01
        world.fields["signal"] = max(0.0, min(1.0, signal + noise))

    def analyze(self, world):
        signal = float(world.fields["signal"])

        return OperatorReport(
            operator="FeedbackOperator",
            role="equilibrium" if abs(signal - 0.5) < 0.1 else "transition",
            stability="adaptive",
            reads=self.reads,
            writes=self.writes,
            values={"signal": signal},
            timestamp_ns=time.time_ns(),
        )
