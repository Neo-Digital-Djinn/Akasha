from __future__ import annotations

from akasha_apis.astronomy.sunrise_sunset import SunriseSunsetAdapter
from akasha_apis.astronomy.lunar_stub import LunarStubAdapter
from akasha_apis.weather.open_meteo import OpenMeteoWeatherAdapter
from akasha_apis.geo.timezone_lookup import TimezoneLookupAdapter


def list_registered_adapters() -> list[dict]:
    adapters = [
        SunriseSunsetAdapter(),
        LunarStubAdapter(),
        OpenMeteoWeatherAdapter(),
        TimezoneLookupAdapter(),
    ]
    return [adapter.metadata() for adapter in adapters]
