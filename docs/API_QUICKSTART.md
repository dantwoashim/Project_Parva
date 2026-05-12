# API Quickstart

Project Parva's stable public-beta API lives under `/v3/api/*`.

The lightweight public demo may expose a narrower subset for evaluation. Private or full deployments can enable the broader stable API surface with controlled configuration.

Base URL (deployment example):

```text
https://api.prabinghimire1.com.np/v3/api
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
curl https://api.prabinghimire1.com.np/v3/api/calendar/today
```

## 2. Gregorian to Bikram Sambat conversion

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/convert?date=2026-10-21"
```

## 3. Personal Panchanga with POST JSON

Privacy-sensitive inputs should use POST bodies instead of query strings.

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/personal/panchanga ^
  -H "Content-Type: application/json" ^
  -d "{\"date\":\"2026-10-21\",\"lat\":\"27.7172\",\"lon\":\"85.3240\",\"tz\":\"Asia/Kathmandu\"}"
```

## 4. Muhurta heatmap

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/muhurta/heatmap ^
  -H "Content-Type: application/json" ^
  -d "{\"date\":\"2026-10-21\",\"lat\":\"27.7172\",\"lon\":\"85.3240\",\"tz\":\"Asia/Kathmandu\",\"type\":\"travel\",\"assumption_set\":\"np-mainstream-v2\"}"
```

## 5. Kundali

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/kundali ^
  -H "Content-Type: application/json" ^
  -d "{\"datetime\":\"2026-02-15T06:30:00+05:45\",\"lat\":\"27.7172\",\"lon\":\"85.3240\",\"tz\":\"Asia/Kathmandu\"}"
```

## 6. Upcoming festivals

```bash
curl "https://api.prabinghimire1.com.np/v3/api/festivals/upcoming?days=30&quality_band=computed"
```

## JavaScript example

```js
const response = await fetch('https://api.prabinghimire1.com.np/v3/api/temporal/compass', {
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

## Future-BS capabilities summary

The public future-BS route returns capability metadata only. It does not return direct future month lengths or private audit outputs.

```bash
curl https://api.prabinghimire1.com.np/v4/api/future-bs/capabilities
```

Future-BS research outputs are labeled:

```text
computed_prediction_not_official
```

## Python SDK example

```python
from parva import ParvaClient

client = ParvaClient("https://api.prabinghimire1.com.np/v3/api")

today = client.get_today()
ad_to_bs = client.ad_to_bs("2026-04-14")
bs_to_ad = client.bs_to_ad(2083, 1, 1)
validation = client.validate_bs_date(2083, 1, 32)
future_bs_capabilities = client.get_future_bs_capabilities()

print(today["publication_status"] if "publication_status" in today else "calendar_payload")
print(future_bs_capabilities["publication_status"])
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
