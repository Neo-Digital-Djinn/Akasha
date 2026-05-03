# esce/config.py — Central configuration for ESCE pipeline
# Akasha organ: akasha-esce / layer: transformation

DEFAULT_PIPELINE: list[str] = ["xor"]
DEFAULT_KEY: int = 23
CHUNK_SIZE: int = 1024 * 1024  # 1 MiB — stream-safe for Debian file ops
