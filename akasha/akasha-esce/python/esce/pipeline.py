# esce/pipeline.py — Ordered plugin orchestration
# Axiom 1 (Coherence): explicit ordering — no implicit behavior.
# Axiom 6 (Modularity): each plugin stage is independently replaceable.

from .plugin_loader import load_plugins
from .config import DEFAULT_PIPELINE


class Pipeline:
    def __init__(self, plugin_order: list[str] | None = None):
        self.plugin_order = plugin_order or DEFAULT_PIPELINE
        self.plugins = load_plugins(self.plugin_order)

    def process(self, data: bytes) -> bytes:
        """Run data through each plugin in declared order."""
        for plugin in self.plugins:
            data = plugin.transform(data)
        return data
