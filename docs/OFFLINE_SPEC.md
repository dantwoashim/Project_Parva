# Offline Package Specification

## Purpose

Parva Offline Packages are self-contained JSON files that contain all computed calendar data for a BS year. They enable:
- Mobile apps without internet
- Embedded systems
- Print calendar generation
- Archival preservation

## Package Format

```json
{
  "parva_offline_package": "1.0",
  "bs_year": 2082,
  "gregorian_year": 2025,
  "generated": "2026-02-16",
  "festivals": {
    "dashain": {"start": "2025-10-02", "end": "2025-10-11", ...},
    ...
  },
  "bs_calendar": {
    "1": {"name": "Baishakh", "days": 31, "dates": [...]},
    ...
  },
  "panchanga_sample": [
    {"date": "2025-01-01", "tithi": "Shukla Panchami", ...},
    ...
  ]
}
```

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `parva_offline_package` | string | Version identifier |
| `bs_year` | int | Bikram Sambat year |
| `gregorian_year` | int | Approximate Gregorian year |
| `festivals` | object | Festival ID → date mapping |
| `bs_calendar` | object | Month-by-month BS calendar |
| `panchanga_sample` | array | Daily panchanga entries |

## Generation

```bash
python -m backend.tools.generate_offline --bs-year 2082 --output offline_2082.json
```

## Size Estimates

| Content | Approximate Size |
|---------|-----------------|
| Festivals only | ~5 KB |
| BS calendar | ~50 KB |
| Full year panchanga | ~200 KB |
| Complete package | ~250 KB |
