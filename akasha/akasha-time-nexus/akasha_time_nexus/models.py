from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class EventInput:
    timestamp_utc: str
    latitude: float
    longitude: float
    event_type: str = "observation"
    title: str = ""
    notes: str = ""
    source: str = "manual"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ClockContext:
    utc: str
    local: str
    timezone_name: str
    day_of_week: str
    day_of_year: int
    season: str
    hour_local: int
    is_weekend: bool


@dataclass(slots=True)
class SolarContext:
    sunrise_local: str | None = None
    sunset_local: str | None = None
    is_daylight: bool | None = None
    minutes_from_sunrise: int | None = None
    minutes_from_sunset: int | None = None


@dataclass(slots=True)
class LunarContext:
    moon_phase: str | None = None
    moon_illumination_pct: float | None = None


@dataclass(slots=True)
class WeatherContext:
    temperature_c: float | None = None
    humidity_pct: float | None = None
    pressure_mb: float | None = None
    wind_kph: float | None = None
    precipitation_mm: float | None = None
    summary: str | None = None


@dataclass(slots=True)
class ContextBundle:
    clock: ClockContext
    solar: SolarContext
    lunar: LunarContext
    weather: WeatherContext
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "clock": asdict(self.clock),
            "solar": asdict(self.solar),
            "lunar": asdict(self.lunar),
            "weather": asdict(self.weather),
            "extra": self.extra,
        }


@dataclass(slots=True)
class EnrichedEvent:
    event: EventInput
    context: ContextBundle

    def to_dict(self) -> dict[str, Any]:
        return {
            "event": asdict(self.event),
            "context": self.context.to_dict(),
        }
