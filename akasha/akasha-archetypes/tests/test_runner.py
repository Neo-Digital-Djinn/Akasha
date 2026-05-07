import numpy as np

from world.world_state import WorldState
from core.runner import Runner
from operators.emergence import EmergenceOperator
from operators.resonance import ResonanceOperator
from operators.feedback import FeedbackOperator
from operators.oscillation import OscillationOperator

def test_pipeline_runs():
    world = WorldState(
        seed=42,
        fields={
            "field": np.random.randint(0, 2, (8,8)),
            "phase": np.random.rand(5),
            "omega": np.random.rand(5),
            "signal": 0.5,
            "energy": 0.0,
        },
    )

    runner = Runner([
        FeedbackOperator(),
        ResonanceOperator(),
        OscillationOperator(),
        EmergenceOperator(),
    ])

    log = runner.run(world, steps=3)

    assert len(log) == 3
