from __future__ import annotations

from datetime import datetime

from ..models import SolarContext, WeatherContext


def get_timezone_name(latitude: float, longitude: float) -> str:
    try:
        from akasha_apis.geo.timezone_lookup import TimezoneLookupAdapter
        payload = TimezoneLookupAdapter().get(latitude=latitude, longitude=longitude)
        return payload.get("timezone_name") or "UTC"
    except Exception:
        return "UTC"


def get_solar_context(timestamp_utc: str, latitude: float, longitude: float, timezone_name: str) -> SolarContext:
    try:
        from akasha_apis.astronomy.sunrise_sunset import SunriseSunsetAdapter
        date = datetime.fromisoformat(timestamp_utc.replace("Z", "+00:00")).date().isoformat()
        payload = SunriseSunsetAdapter().get(
            latitude=latitude,
            longitude=longitude,
            date=date,
            timestamp_utc=timestamp_utc,
            timezone_name=timezone_name,
        )
        return SolarContext(**payload)
    except Exception:
        return SolarContext()


def get_weather_context(timestamp_utc: str, latitude: float, longitude: float) -> WeatherContext:
    try:
        from akasha_apis.weather.open_meteo import OpenMeteoWeatherAdapter
        payload = OpenMeteoWeatherAdapter().get(latitude=latitude, longitude=longitude, timestamp_utc=timestamp_utc)
        return WeatherContext(**payload)
    except Exception:
        return WeatherContext()
