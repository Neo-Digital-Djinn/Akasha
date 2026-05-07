from enum import Enum

class StructuralRole(str, Enum):
    PHASE = "phase"
    TRANSITION = "transition"
    CONSTRAINT = "constraint"
    INSTABILITY = "instability"
    EQUILIBRIUM = "equilibrium"
    ATTRACTOR = "attractor"

class StabilityVerdict(str, Enum):
    STABLE = "stable"
    COHERENT = "coherent"
    DYNAMIC = "dynamic"
    DISORDERED = "disordered"
    UNSTABLE = "unstable"
    ADAPTIVE = "adaptive"
    DAMPED = "damped"
    ACTIVE = "active"
