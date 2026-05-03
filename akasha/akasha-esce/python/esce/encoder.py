# esce/encoder.py — Pipeline execution bridge to C core
# Akasha organ: akasha-esce / layer: transformation

from esce._core import xor_bytes  # C extension compiled from core/esce_core.c


def encode_bytes(data: bytes, key: int = 42) -> bytes:
    """XOR-encode bytes with key using the C primitive."""
    return xor_bytes(data, key)


def decode_bytes(data: bytes, key: int = 42) -> bytes:
    """XOR is self-inverse: decode == encode."""
    return xor_bytes(data, key)
