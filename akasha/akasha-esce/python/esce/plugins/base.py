# esce/plugins/base.py — Plugin interface contract
# All ESCE plugins must subclass PluginBase.


class PluginBase:
    name: str = "base"

    def transform(self, data: bytes) -> bytes:
        raise NotImplementedError(f"Plugin '{self.name}' must implement transform()")
