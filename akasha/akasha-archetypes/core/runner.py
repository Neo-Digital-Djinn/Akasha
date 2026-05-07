import time
from core.records import StepRecord

class Runner:
    def __init__(self, operators):
        self.operators = operators

    def run(self, world, steps=10):
        log = []

        for step in range(steps):
            before = world.hash()
            reports = []

            for op in self.operators:
                op.step(world, {})
                report = op.analyze(world)
                report.timestamp_ns = time.time_ns()
                reports.append(report)

            after = world.hash()

            record = StepRecord(
                step=step,
                world_hash_before=before,
                world_hash_after=after,
                reports=reports,
                snapshot=world.snapshot(),
            )

            world.t += 1
            log.append(record)

        return log
