# esce/plugins/hmac_plugin.py — HMAC-SHA256 transform plugin
# SECRET should be overridden via config in production contexts.

import hmac as _hmac
import hashlib
from .base import PluginBase

SECRET = b"esce-secret"  # TODO: inject via config / env in production


class HMACPlugin(PluginBase):
    name = "hmac"

    def transform(self, data: bytes) -> bytes:
        return _hmac.new(SECRET, data, hashlib.sha256).digest()
