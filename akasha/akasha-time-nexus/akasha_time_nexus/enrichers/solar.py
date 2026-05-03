from __future__ import annotations

from ..models import SolarContext


def build_solar_context(timestamp_utc: str, latitude: float, longitude: float, timezone_name: str = "UTC") -> SolarContext:
    return SolarContext(
        sunrise_local=None,
        sunset_local=None,
        is_daylight=None,
        minutes_from_sunrise=None,
        minutes_from_sunset=None,
    )
