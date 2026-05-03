# esce/plugin_loader.py — Dynamic plugin discovery and loading
# Axiom 6 (Modularity): plugins are independently discoverable and replaceable.

import importlib
from .plugins.base import PluginBase


def load_plugins(plugin_names: list[str]) -> list[PluginBase]:
    """
    Dynamically import and instantiate plugins by name.
    Each name maps to esce.plugins.<name>_plugin module.
    Raises ImportError clearly if a plugin module is missing.
    """
    plugins: list[PluginBase] = []
    for name in plugin_names:
        module_path = f"esce.plugins.{name}_plugin"
        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError as exc:
            raise ImportError(
                f"ESCE plugin '{name}' not found at '{module_path}'. "
                f"Available built-ins: xor, hash, hmac."
            ) from exc

        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            if (
                isinstance(obj, type)
                and issubclass(obj, PluginBase)
                and obj is not PluginBase
            ):
                plugins.append(obj())
                break  # one plugin class per module

    return plugins
