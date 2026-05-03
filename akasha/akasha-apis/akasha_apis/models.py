from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ProviderMetadata:
    name: str
    provider_type: str
    auth_required: bool
    status: str
    description: str
