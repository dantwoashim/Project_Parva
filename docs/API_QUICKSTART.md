# API Quickstart

Project Parva's stable public-beta API lives under `/v3/api/*`.

Base URL (deployment example):

```text
https://your-host.example/v3/api
```

## What is stable now

- Read-only calendar and festival endpoints
- POST-first personal compute flows for location-sensitive requests
- Integration metadata such as `calculation_trace_id`, `method`, `quality_band`, and `provenance`

## Start the stack

```bash
py -3.11 -m pip install -e .[test,dev]
uvicorn app.main:app --app-dir backend --reload --port 8000
```

## 1. Calendar today

```bash
curl https://your-host.example/v3/api/calendar/today
```

## 2. Gregorian to Bikram Sambat conversion

```bash
curl "https://your-host.example/v3/api/calendar/convert?date=2026-10-21"
```

## 3. Personal Panchanga with POST JSON

Privacy-sensitive inputs should use POST bodies instead of query strings.

```bash
curl -X POST https://your-host.example/v3/api/personal/panchanga ^
  -H "Content-Type: application/json" ^
  -d "{\"date\":\"2026-10-21\",\"lat\":\"27.7172\",\"lon\":\"85.3240\",\"tz\":\"Asia/Kathmandu\"}"
```

## 4. Muhurta heatmap

```bash
curl -X POST https://your-host.example/v3/api/muhurta/heatmap ^
  -H "Content-Type: application/json" ^
  -d "{\"date\":\"2026-10-21\",\"lat\":\"27.7172\",\"lon\":\"85.3240\",\"tz\":\"Asia/Kathmandu\",\"type\":\"travel\",\"assumption_set\":\"np-mainstream-v2\"}"
```

## 5. Kundali

```bash
curl -X POST https://your-host.example/v3/api/kundali ^
  -H "Content-Type: application/json" ^
  -d "{\"datetime\":\"2026-02-15T06:30:00+05:45\",\"lat\":\"27.7172\",\"lon\":\"85.3240\",\"tz\":\"Asia/Kathmandu\"}"
```

## 6. Upcoming festivals

```bash
curl "https://your-host.example/v3/api/festivals/upcoming?days=30&quality_band=computed"
```

## JavaScript example

```js
const response = await fetch('https://your-host.example/v3/api/temporal/compass', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    date: '2026-10-21',
    lat: '27.7172',
    lon: '85.3240',
    tz: 'Asia/Kathmandu',
    quality_band: 'computed',
  }),
});

const payload = await response.json();
console.log(payload.primary_readout.tithi_name);
console.log(payload.calculation_trace_id);
```

## Python SDK example

```python
from parva_sdk import ParvaClient

client = ParvaClient("https://your-host.example/v3/api")

compass = client.temporal_compass(
    "2026-10-21",
    latitude=27.7172,
    longitude=85.3240,
)

print(compass.data["primary_readout"]["tithi_name"])
print(compass.meta.trace_id)
```

## Metadata to preserve

For integrations that store or forward Parva output, keep these fields:

- `calculation_trace_id`
- `method`
- `method_profile`
- `quality_band`
- `assumption_set_id`
- `provenance`
- `policy`

## Operational notes

- Personal compute responses are served with `Cache-Control: no-store`.
- If you need a drop-in website integration, see `docs/EMBED_GUIDE.md`.
- For local development, point the same `/v3/api` path at your local backend instead of the deployment example above.
