# OpenAPI & API Versioning Specification

## API Version: v2.0

All endpoints are versioned and documented via FastAPI's auto-generated OpenAPI schema.

## Accessing API Documentation

| Format | URL |
|--------|-----|
| Interactive (Swagger UI) | `/docs` |
| Alternative (ReDoc) | `/redoc` |
| Raw OpenAPI JSON | `/api/openapi.json` |

## Versioning Strategy

### Current: `/api/*` (unversioned, default)
All existing endpoints remain at their current paths for backward compatibility.

### Future: `/api/v1/*`
A versioned router (`api_v1.py`) mirrors all current endpoints under `/api/v1/`. When breaking changes are needed, `/api/v2/` will be introduced while `/api/v1/` remains stable.

## Breaking Change Policy

1. **Minor changes** (new optional fields, new endpoints): No version bump
2. **Breaking changes** (field removal, type changes): New version prefix
3. **Deprecation**: 6-month warning period before removal

## Endpoint Inventory

### Calendar Core
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/calendar/convert` | Gregorian → BS, NS, tithi |
| GET | `/api/calendar/today` | Today's calendar info |
| GET | `/api/calendar/panchanga` | Full 5-element panchanga |
| GET | `/api/calendar/panchanga/range` | Multi-day panchanga |
| POST | `/api/calendar/bs-to-gregorian` | BS → Gregorian conversion |
| GET | `/api/calendar/convert/compare` | Official vs estimated BS |
| GET | `/api/calendar/sankranti/{year}` | Solar transits |
| GET | `/api/calendar/ical` | iCalendar feed download |

### Festivals
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/calendar/festivals/calculate/{id}` | Calculate festival dates |
| GET | `/api/calendar/festivals/upcoming` | Upcoming festivals |

### Cross-Calendar
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/calendar/cross/calendars` | List calendar systems |
| GET | `/api/calendar/cross/convert` | Gregorian → any calendar |
| GET | `/api/calendar/cross/convert-all` | Gregorian → all calendars |
| GET | `/api/calendar/cross/between` | Any calendar → any calendar |

### Explainability
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/calendar/explain/date` | Step-by-step date explanation |
| GET | `/api/calendar/explain/festival/{id}` | Festival calculation trace |
| GET | `/api/calendar/explain/uncertainty` | Uncertainty bands |

### Engine
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/engine/health` | Engine health check |
| GET | `/api/engine/config` | Engine configuration |

### Webhooks
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/webhooks/register` | Register webhook |
| DELETE | `/api/webhooks/{id}` | Delete webhook |
| GET | `/api/webhooks/` | List webhooks |
