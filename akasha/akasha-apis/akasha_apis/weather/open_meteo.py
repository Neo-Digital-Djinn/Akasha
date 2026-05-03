from __future__ import annotations

import requests

from akasha_apis.base_adapter import BaseAdapter


class OpenMeteoWeatherAdapter(BaseAdapter):
    name = "open-meteo"
    provider_type = "weather"

    def fetch(self, *, latitude: float, longitude: float, **kwargs):
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": ",".join([
                    "temperature_2m",
                    "relative_humidity_2m",
                    "surface_pressure",
                    "wind_speed_10m",
                    "precipitation",
                ]),
            },
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def normalize(self, raw, **kwargs) -> dict[str, object]:
        current = raw.get("current", {}) if isinstance(raw, dict) else {}
        return {
            "temperature_c": current.get("temperature_2m"),
            "humidity_pct": current.get("relative_humidity_2m"),
            "pressure_mb": current.get("surface_pressure"),
            "wind_kph": current.get("wind_speed_10m"),
            "precipitation_mm": current.get("precipitation"),
            "summary": "open-meteo current snapshot",
        }

    def metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "provider_type": self.provider_type,
            "auth_required": False,
            "status": "active",
            "description": "Open-Meteo current weather snapshot adapter",
        }
