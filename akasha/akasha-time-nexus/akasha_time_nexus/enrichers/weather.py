from __future__ import annotations

from ..models import WeatherContext


def build_weather_context(timestamp_utc: str, latitude: float, longitude: float) -> WeatherContext:
    return WeatherContext(
        temperature_c=None,
        humidity_pct=None,
        pressure_mb=None,
        wind_kph=None,
        precipitation_mm=None,
        summary=None,
    )
