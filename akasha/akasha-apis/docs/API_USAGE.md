# API Usage

## Adapter contract

Every adapter should implement:

- `fetch(**kwargs)`
- `normalize(raw, **kwargs)`
- `metadata()`

Optional helper:
- `get(**kwargs)` → fetch + normalize

## Example

```python
from akasha_apis.weather.open_meteo import OpenMeteoWeatherAdapter

adapter = OpenMeteoWeatherAdapter()
payload = adapter.get(latitude=38.42, longitude=-82.44)
print(payload)
```
