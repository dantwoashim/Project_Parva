# UI Temporal Cartography Spec (v2)

## Scope
This document defines the current product IA and UX behavior for the Temporal Cartography redesign implemented in the v3 public profile.

## Experience Modes
1. `Observance` (default)
- Compact, practical labels.
- User-facing recommendations first.
- Technical metadata hidden unless user asks.

2. `Authority`
- Progressive disclosure of trace/provenance/confidence/method.
- `AuthorityInspector` enabled on major routes.
- JSON payload copy flow retained in inspector.

Mode + language + quality preferences are persisted via `TemporalContext` local storage.

## Global State Contract
`TemporalContextState`
- `date: string` (`YYYY-MM-DD`)
- `location: { latitude: number, longitude: number }`
- `timezone: string`
- `mode: "observance" | "authority"`
- `language: "en" | "ne"`
- `qualityBand: "computed" | "provisional" | "inventory" | "all"`

## Route IA
1. `/` -> Temporal Compass
2. `/festivals` -> Explorer Ribbon
3. `/festivals/:festivalId` -> Festival Detail
4. `/panchanga`
5. `/personal`
6. `/muhurta`
7. `/kundali`
8. `/feeds`
9. `/dashboard` (legacy overview)

## Route Specs
### `/` Temporal Compass
Primary widgets:
- BS date + active tithi readout
- Orbital ring (tithi phase ratio)
- Horizon strip (sunrise, sunset, current muhurta)
- Today festival quick cards

Data source:
- `GET /v3/api/temporal/compass`

Authority mode:
- Shows `Temporal Compass Authority` inspector card.

### `/festivals` Explorer Ribbon
Primary widgets:
- Timeline filters (`from`, `window`, `category`, `region`)
- Month-grouped ribbon with sticky month headers
- Quality marker on each card (`computed|provisional|inventory`)

Data source:
- `GET /v3/api/festivals/timeline`

Authority mode:
- Shows explorer trace and metadata in inspector.

### `/festivals/:festivalId` Detail
Primary widgets:
- Hero + schedule summary + countdown
- Mythology and rituals
- Related festivals
- Calculation metadata + trace viewer

Canonical ritual contract:
- UI reads `festival.ritual_sequence.days[]` first.
- Legacy structures are normalized as fallback.

### `/panchanga`
Primary widgets:
- Day picker + BS date
- 5 panchanga cards (tithi, nakshatra, yoga, karana, vaara)
- Moon phase visualization
- Festival chips on selected day
- Knowledge panel (bilingual glossary-backed)

Data sources:
- `GET /v3/api/calendar/panchanga`
- `GET /v3/api/resolve`
- `GET /v3/api/festivals/on-date/{date}`
- `GET /v3/api/glossary?domain=panchanga&lang=`

### `/personal`
Primary widgets:
- Date + location + timezone controls
- Personalized panchanga cards
- Sunrise delta indicator vs Kathmandu baseline

Data source:
- `GET /v3/api/personal/panchanga`

### `/muhurta`
Primary widgets:
- Ceremony type + assumption set controls
- 24h heatmap (primary)
- Selected window reason + confidence breakdown
- Rahu kalam and tara bala summaries
- Knowledge panel

Data source:
- `GET /v3/api/muhurta/heatmap`

### `/kundali`
Primary widgets:
- Birth datetime/location form
- Rashi summary cards
- Interactive SVG graph (house/graha/aspect selection)
- Insight sidebar
- Graha table
- Knowledge panel

Data sources:
- `GET /v3/api/kundali`
- `GET /v3/api/kundali/graph`
- `GET /v3/api/glossary?domain=kundali&lang=`

### `/feeds`
Primary widgets:
- Quick iCal cards (all/national/newari)
- Custom festival feed builder

## Design System Rules
- Theme direction: Digital Brass & Slate.
- Motion is functional, not decorative.
- Target minimum tap size: 44px.
- Numeric readouts use tabular alignment.
- Loading/error/success states are explicit for every route.

## Feature Flags
Current flag names reserved for staged rollout:
- `ui_temporal_compass`
- `ui_festival_ribbon`
- `ui_muhurta_heatmap`
- `ui_kundali_graph`
- `ui_bimodal_authority`

## Validation Gates
1. Frontend tests + visual regression snapshots.
2. Route-level keyboard accessibility checks.
3. Bilingual glossary fetch with fallback.
4. No ritual timeline render without canonical normalization pass.
