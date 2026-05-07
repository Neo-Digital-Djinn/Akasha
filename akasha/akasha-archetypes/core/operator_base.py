from abc import ABC, abstractmethod
from typing import Dict, Any
from core.records import OperatorReport

class Operator(ABC):
    reads = []
    writes = []

    @abstractmethod
    def step(self, world, params: Dict[str, Any]):
        pass

    @abstractmethod
    def analyze(self, world) -> OperatorReport:
        pass

    def describe(self):
        return {
            "operator": self.__class__.__name__,
            "reads": self.reads,
            "writes": self.writes,
        }
