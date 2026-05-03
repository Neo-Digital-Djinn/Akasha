from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from forge_stub import ForgeStub

hypothesis = {
    "target": "time_crystal",
    "gap_type": "structural_sink",
    "reason": "time_crystal receives references but does not yet propagate into adjacent structures",
    "gap_score": 0.9,
    "proposal": "Explore missing connections for 'time_crystal'",
    "suggestions": [
        "Link 'time_crystal' to adjacent domains",
        "Search for analogous structures in other fields",
        "Generate tool or model to bridge domain gap",
    ],
}

workspace_root = HERE.parents[2]
forge = ForgeStub(workspace_root=workspace_root)
plan = forge.build_proposal(hypothesis)
path = forge.save_build_plan(plan)

print(path)
print(plan)
