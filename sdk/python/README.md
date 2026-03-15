# Parva Python SDK

`parva-sdk` is the Python client for Project Parva's stable public-beta `v3`
API surface. It supports the read-only calendar/festival endpoints plus the
POST-first personal compute workflows used by the app.

## Install

```bash
py -3.11 -m pip install -e sdk/python
```

## Quick start

```python
from parva_sdk import ParvaClient

client = ParvaClient("http://localhost:8000/v3/api")

today = client.today()
convert = client.convert("2026-10-21")
upcoming = client.upcoming(7)
```

## Personal compute helpers

These helpers use JSON POST requests and normalize numeric coordinates into the
string form expected by the public API.

```python
from parva_sdk import ParvaClient

client = ParvaClient("http://localhost:8000/v3/api")

compass = client.temporal_compass(
    "2026-10-21",
    latitude=27.7172,
    longitude=85.3240,
)

panchanga = client.personal_panchanga(
    "2026-10-21",
    latitude=27.7172,
    longitude=85.3240,
)

heatmap = client.muhurta_heatmap(
    "2026-10-21",
    ceremony_type="travel",
    latitude=27.7172,
    longitude=85.3240,
)

kundali = client.kundali(
    "2026-02-15T06:30:00+05:45",
    latitude=27.7172,
    longitude=85.3240,
)
```

Additional helpers:

- `muhurta_day(...)`
- `rahu_kalam(...)`
- `auspicious_muhurta(...)`
- `kundali_lagna(...)`
- `kundali_graph(...)`
- `observances(...)`
- `resolve(...)`
- `spec_conformance(...)`
- `verify_trace(...)`

## Response model

All helpers return `DataEnvelope`, which keeps the full API payload under
`.data` and exposes parsed metadata under `.meta` when the response includes
top-level method, confidence, provenance, or policy fields.

```python
response = client.personal_panchanga("2026-10-21")

print(response.data["tithi"]["name"])
print(response.meta.method)
print(response.meta.quality_band)
print(response.meta.trace_id)
```

## Deprecated import path

`from parva import ParvaClient` still works for compatibility, but it emits a
`DeprecationWarning`. New code should import from `parva_sdk`.
