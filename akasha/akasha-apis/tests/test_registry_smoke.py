from akasha_apis.registry import list_registered_adapters


def test_registry_returns_list():
    items = list_registered_adapters()
    assert isinstance(items, list)
    assert len(items) >= 1
