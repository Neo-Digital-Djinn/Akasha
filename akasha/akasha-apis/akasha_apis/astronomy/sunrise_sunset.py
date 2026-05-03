from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import requests

from akasha_apis.base_adapter import BaseAdapter


class SunriseSunsetAdapter(BaseAdapter):
    name = "sunrise-sunset"
    provider_type = "astronomy"

    def fetch(self, *, latitude: float, longitude: float, date: str, **kwargs):
        response = requests.get(
            "https://api.sunrise-sunset.org/json",
            params={
                "lat": latitude,
                "lng": longitude,
                "date": date,
                "formatted": 0,
            },
            timeout=20,
        )
        response.raise_for_status()
        return response.json()

    def normalize(
        self,
        raw,
        *,
        timestamp_utc: str | None = None,
        timezone_name: str = "UTC",
        **kwargs,
    ) -> dict[str, object]:
        results = raw.get("results", {}) if isinstance(raw, dict) else {}
        tz = ZoneInfo(timezone_name)

        sunrise_utc = results.get("sunrise")
        sunset_utc = results.get("sunset")

        sunrise_local = None
        sunset_local = None
        is_daylight = None
        minutes_from_sunrise = None
        minutes_from_sunset = None

        if sunrise_utc:
            sunrise_dt = datetime.fromisoformat(sunrise_utc.replace("Z", "+00:00")).astimezone(tz)
            sunrise_local = sunrise_dt.isoformat()
        else:
            sunrise_dt = None

        if sunset_utc:
            sunset_dt = datetime.fromisoformat(sunset_utc.replace("Z", "+00:00")).astimezone(tz)
            sunset_local = sunset_dt.isoformat()
        else:
            sunset_dt = None

        if timestamp_utc:
            event_dt = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00")).astimezone(UTC).astimezone(tz)
            if sunrise_dt and sunset_dt:
                is_daylight = sunrise_dt <= event_dt <= sunset_dt
                minutes_from_sunrise = int((event_dt - sunrise_dt).total_seconds() // 60)
                minutes_from_sunset = int((event_dt - sunset_dt).total_seconds() // 60)

        return {
            "sunrise_local": sunrise_local,
            "sunset_local": sunset_local,
            "is_daylight": is_daylight,
            "minutes_from_sunrise": minutes_from_sunrise,
            "minutes_from_sunset": minutes_from_sunset,
        }

    def metadata(self) -> dict[str, object]:
        return {
            "name": self.name,
            "provider_type": self.provider_type,
            "auth_required": False,
            "status": "active",
            "description": "Sunrise and sunset context adapter",
        }
