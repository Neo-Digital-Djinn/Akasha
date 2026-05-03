# akasha-esce

**Extensible Stream Cipher Engine**  
Akasha Constellation · Layer: Transformation · Status: Canonical

A modular, deterministic, plugin-driven byte-transformation pipeline with a
C-backed XOR primitive, streaming file support, and a clean CLI.

> ⚠️ Architectural framework and research organ — not a hardened cryptographic system.

---

## Installation (Debian 13)

```bash
# System dependencies (one-time)
sudo apt install python3-dev build-essential

# Install ESCE
pip install .

# Development / editable
pip install -e .
```

---

## CLI Usage

```bash
# Encode text (XOR pipeline, hex output)
esce encode-text "hello"

# Hash text (SHA-256, hex output)
esce hash-text "hello"

# Encode file (chunked streaming)
esce encode-file input.bin output.bin

# Decode file (XOR is self-inverse)
esce decode-file output.bin recovered.bin
```

---

## Architecture

```
core/
    esce_core.c         C XOR primitive (compiled as esce._core)

python/esce/
    encoder.py          Bridge to C core
    pipeline.py         Ordered plugin orchestration
    plugin_loader.py    Dynamic plugin discovery
    config.py           Central config (key, chunk size, default pipeline)
    cli.py              Command-line interface

python/esce/plugins/
    base.py             PluginBase interface contract
    xor_plugin.py       C-backed XOR (demo)
    hash_plugin.py      SHA-256
    hmac_plugin.py      HMAC-SHA256

tests/
    test_hash.py
    test_pipeline.py
```

---

## Plugin Interface

```python
from esce.plugins.base import PluginBase

class MyPlugin(PluginBase):
    name = "my_plugin"

    def process(self, data: bytes) -> bytes:
        return data  # your transform here
```

Drop into `python/esce/plugins/` — the loader discovers it automatically.

---

## Built-in Plugins

| Plugin | Backend | Description |
|--------|---------|-------------|
| `xor`  | C ext   | XOR each byte with key (demo only) |
| `hash` | hashlib | SHA-256 digest |
| `hmac` | hashlib | HMAC-SHA256 |

---

## Testing

```bash
pip install pytest
pytest --tb=short -v
```

---

## Akasha Constellation

- **Layer:** transformation
- **Peers:** `akasha-cantus`, `akasha-cipher-lab`
- **Feeds into:** `akasha-events`, `akasha-anomaly`
- **Axiom alignment:** see `repo-manifest.yaml` and `CONSTELLATION_ENTRY.md`

---

## Security Notice

ESCE does **not** implement authenticated encryption, key derivation, or
side-channel protection. It is suitable for pipeline architecture research,
plugin system experimentation, and educational transformation frameworks.

---

## License

MIT
