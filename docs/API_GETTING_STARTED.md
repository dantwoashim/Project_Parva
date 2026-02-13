# API Getting Started (v2)

## Base URL
- Local: `http://localhost:8000/v2/api`
- Legacy (deprecated): `http://localhost:8000/api`

## Quick Start (cURL)

### 1. Get today's calendar
```bash
curl "http://localhost:8000/v2/api/calendar/today"
```

### 2. Convert a date
```bash
curl "http://localhost:8000/v2/api/calendar/convert?date=2026-02-15"
```

### 3. Compare official vs estimated conversion
```bash
curl "http://localhost:8000/v2/api/calendar/convert/compare?date=2026-02-15"
```

### 4. List upcoming festivals
```bash
curl "http://localhost:8000/v2/api/festivals/upcoming?days=30"
```

### 5. Festival detail + dates
```bash
curl "http://localhost:8000/v2/api/festivals/dashain?year=2026"
```

### 6. Festival explain endpoint
```bash
curl "http://localhost:8000/v2/api/festivals/dashain/explain?year=2026"
```

### 7. Create provenance snapshot
```bash
curl -X POST "http://localhost:8000/v2/api/provenance/snapshot/create"
```

### 8. Verify a festival proof
```bash
curl "http://localhost:8000/v2/api/provenance/proof?festival=dashain&year=2026&snapshot=<snapshot_id>"
```

### 9. List calendar plugins
```bash
curl "http://localhost:8000/v2/api/engine/calendars"
```

### 10. Plugin-based conversion (Tibetan v1)
```bash
curl "http://localhost:8000/v2/api/engine/convert?date=2026-02-15&calendar=tibetan"
```

### 11. Regional variants for a festival
```bash
curl "http://localhost:8000/v2/api/festivals/shivaratri/variants?year=2026"
```

### 12. Islamic observance (announced mode)
```bash
curl "http://localhost:8000/v2/api/engine/observances?plugin=islamic&rule_id=eid-al-fitr&year=2026&mode=announced"
```

### 13. Hebrew conversion
```bash
curl "http://localhost:8000/v2/api/engine/convert?date=2026-02-15&calendar=hebrew"
```

## Python Example
```python
import requests

base = "http://localhost:8000/v2/api"
res = requests.get(f"{base}/calendar/convert", params={"date": "2026-02-15"})
res.raise_for_status()
print(res.json())
```

## JavaScript Example
```js
const base = "http://localhost:8000/v2/api";
const res = await fetch(`${base}/calendar/convert?date=2026-02-15`);
if (!res.ok) throw new Error(`API error ${res.status}`);
const data = await res.json();
console.log(data);
```

## Key Metadata Fields
- `engine_version`: current calculation engine version
- `confidence`: `official` or `estimated` for BS dates
- `source_range`: official lookup range when available
- `estimated_error_days`: expected error window in estimated mode
- `method`: calculation method (for tithi/panchanga)
- `provenance`: snapshot hashes and verification URL

## OpenAPI
- `http://localhost:8000/v2/openapi.json`
- `http://localhost:8000/v2/docs`
