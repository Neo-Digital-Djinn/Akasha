# esce/plugins/hash_plugin.py — SHA-256 hash transform plugin

import hashlib
from .base import PluginBase


class HASHPlugin(PluginBase):
    name = "hash"

    def transform(self, data: bytes) -> bytes:
        return hashlib.sha256(data).digest()
