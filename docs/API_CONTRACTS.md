# API Contracts (Year 1 Week 7)

## Response Metadata Baseline

All API responses include headers:
- `X-Parva-Engine: v2`
- `X-Parva-Ephemeris: <mode>-<ayanamsa>-<coordinate_system>`

Date/time endpoints should also expose body metadata fields where applicable:
- `confidence`
- `method`
- `engine_version`
- `source_range` (for lookup-backed BS conversion)
- `estimated_error_days` (for estimated BS conversion)

## BS Conversion Metadata Contract

`bikram_sambat` payload now carries explicit trust metadata:

```json
{
  "year": 2082,
  "month": 10,
  "day": 24,
  "month_name": "Magh",
  "confidence": "official",
  "source_range": "2070-2095",
  "estimated_error_days": null
}
```

For out-of-range conversions:

```json
{
  "confidence": "estimated",
  "source_range": null,
  "estimated_error_days": "0-1"
}
```

Explicit comparison endpoint:
- `GET /api/calendar/convert/compare?date=YYYY-MM-DD`

## Engine Config Endpoint

`GET /api/engine/config`

```json
{
  "ayanamsa": "lahiri",
  "coordinate_system": "sidereal",
  "ephemeris_mode": "moshier",
  "header": "moshier-lahiri-sidereal"
}
```

`GET /api/engine/health`

```json
{
  "status": "ok",
  "ephemeris": "swiss_moshier",
  "ayanamsa": "lahiri",
  "coordinate_system": "sidereal",
  "library": "pyswisseph"
}
```

## Engine Type Contracts

Engine output types are defined in:
- `backend/app/engine/types.py`

Interfaces are defined in:
- `backend/app/engine/interface.py`
- `backend/app/sources/interface.py`
