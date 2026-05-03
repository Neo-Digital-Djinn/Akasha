from __future__ import annotations

from akasha_apis.base_adapter import BaseAdapter


class LunarStubAdapter(BaseAdapter):
    name = "lunar-stub"
    provider_type = "astronomy"

    def fetch(self, **kwargs):
        return {}

    def normalize(self, raw, **kwargs) -> dict[str, object]:
        return {
            "moon_phase": None,
            "moon_illumination_pct": None,
        }

    def metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "provider_type": self.provider_type,
            "auth_required": False,
            "status": "stub",
            "description": "Lunar provider placeholder for v2",
        }
