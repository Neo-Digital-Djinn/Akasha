# esce/plugins/xor_plugin.py — C-backed XOR transform plugin
# Demo only — not a hardened cipher.

from .base import PluginBase
from esce.encoder import encode_bytes
from esce.config import DEFAULT_KEY


class XORPlugin(PluginBase):
    name = "xor"

    def transform(self, data: bytes) -> bytes:
        return encode_bytes(data, DEFAULT_KEY)
