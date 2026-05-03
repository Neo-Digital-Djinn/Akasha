from __future__ import annotations

from akasha_apis.base_adapter import BaseAdapter


class TimezoneLookupAdapter(BaseAdapter):
    name = "timezone-lookup"
    provider_type = "geo"

    def fetch(self, *, latitude: float, longitude: float, **kwargs):
        # V2 conservative placeholder. Replace with real timezone provider later.
        return {
            "latitude": latitude,
            "longitude": longitude,
        }

    def normalize(self, raw, **kwargs) -> dict[str, object]:
        return {
            "timezone_name": "UTC",
        }

    def metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "provider_type": self.provider_type,
            "auth_required": False,
            "status": "stub",
            "description": "Timezone lookup placeholder adapter",
        }
