from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    name: str = "base"
    provider_type: str = "generic"

    @abstractmethod
    def fetch(self, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    def normalize(self, raw: Any, **kwargs) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        raise NotImplementedError

    def get(self, **kwargs) -> dict[str, Any]:
        raw = self.fetch(**kwargs)
        return self.normalize(raw, **kwargs)
