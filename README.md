# Project Parva 🎭 v3.0.0 (LTS)

> **Nepal's Festival Discovery Platform**  
> Ephemeris-powered astronomical calculations • Interactive temple map • Rich cultural narratives

[![Tests](https://img.shields.io/badge/tests-312%20passing-brightgreen)](./tests)
[![Festivals](https://img.shields.io/badge/festivals-50-orange)](./data/festivals/festivals.json)
[![Accuracy](https://img.shields.io/badge/accuracy-97%25-blue)](./docs/DATE_ACCURACY_EVALUATION.md)
[![Date Range](https://img.shields.io/badge/range-2000--2200%20BS-purple)](./docs/IMPLEMENTATION_PLAN_V2.md)

---

## 🌟 What is Project Parva?

Project Parva is a festival timing application for Nepal that solves the annual confusion: "When is Dashain this year?" Unlike static calendar apps, Parva uses **ephemeris-based astronomical calculations** across multiple Nepali calendar systems (Bikram Sambat, Nepal Sambat, Tithi/Lunar) to compute festival dates programmatically.

### v2.0 Upgrade — Ephemeris Engine

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Tithi calculation | Synodic approximation | Swiss Ephemeris (Moshier mode) |
| Accuracy | ±7 hours | ±2 minutes |
| Date range | 2070-2095 BS | 2000-2200 BS |
| Algorithm | `days mod 29.53` | `(moon_long - sun_long) / 12°` |

The platform combines:
- **Ritual Time Engine**: Calculates festival dates using authentic calendar rules and NASA ephemerides
- **Interactive Temple Map**: Shows festival locations using OpenStreetMap data
- **Cultural Narratives**: Deep mythology and ritual information for each festival

### Current Truthful Status
- Implemented state is tracked in: [`/docs/AS_BUILT.md`](./docs/AS_BUILT.md)
- Future roadmap is tracked in: [`/docs/VISION.md`](./docs/VISION.md)

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm

### Backend (FastAPI)

```bash
cd backend
pip install -e .
pip install pyswisseph  # v2.0 ephemeris support
python -m uvicorn app.main:app --reload --port 8000
```

API (v5 authority track) available at: `http://localhost:8000/v5/api`  
API (v4 normalized contract) available at: `http://localhost:8000/v4/api`  
API (v3 LTS compatibility) available at: `http://localhost:8000/v3/api`  
API docs: `http://localhost:8000/v5/docs` (or `http://localhost:8000/docs`)

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

App available at: `http://localhost:5173`

---

## 📁 Project Structure

```
Project Parva/
├── backend/                 # FastAPI backend
│   └── app/
│       ├── calendar/        # BS, NS, Tithi calculation engines
│       │   ├── ephemeris/   # v2.0: Swiss Ephemeris integration
│       │   │   ├── swiss_eph.py
│       │   │   └── positions.py
│       │   ├── tithi/       # v2.0: Precise tithi calculation
│       │   │   ├── tithi_core.py
│       │   │   └── tithi_udaya.py
│       │   ├── panchanga/   # v2.0: Full 5-element panchanga
│       │   └── sankranti.py # v2.0: Solar transit detection
│       ├── festivals/       # Festival API and models
│       ├── locations/       # Temple/location API
│       └── mythology/       # Cultural content models
├── frontend/                # React + Vite frontend
├── data/                    # Festival and temple data
├── tests/                   # 312 unit and integration tests
└── docs/                    # Documentation
    ├── IMPLEMENTATION_PLAN_V2.md  # 5-day sprint plan
    ├── DATE_ACCURACY_EVALUATION.md
    └── DATA_SOURCES.md
```

---

## 🎭 Features

### Calendar Engines (v2.0 Ephemeris)

- **Bikram Sambat (BS)**: Hybrid lookup + computed conversion
- **Nepal Sambat (NS)**: Traditional Newari calendar
- **Tithi Calculator**: Ephemeris-based with Lahiri ayanamsa
- **Full Panchanga**: Tithi, Nakshatra, Yoga, Karana, Vaara

### Panchanga API Example

```bash
curl http://localhost:8000/v3/api/calendar/panchanga?date=2026-02-15

# Response:
{
  "date": "2026-02-15",
  "bs_date": {"year": 2082, "month": 11, "day": 3},
  "tithi": {"number": 14, "paksha": "krishna", "name": "Chaturdashi"},
  "nakshatra": {"number": 9, "name": "Ashlesha"},
  "yoga": {"number": 5, "name": "Shobhana"},
  "karana": {"number": 7, "name": "Vanija"},
  "vaara": "Sunday",
  "confidence": "exact"
}
```

### Festival Discovery
- Browse 50 festivals by date, category, or region
- Filter upcoming events (30/90 day views)
- Full mythology and ritual sequences
- Extended date support (2000-2200 BS)

### Interactive Map
- 15 major temples and religious sites
- Festival-to-location mappings with ritual roles
- Fly-to animations and marker popups

---

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=backend/app

# Test ephemeris accuracy
python -m pytest tests/unit/test_ephemeris.py -v
```

**Current status**: 312 tests passing, 97% accuracy benchmark retained from the v2 evaluation set

---

## 📊 Data

### Festivals (50 entries)
Categories: National, Newari, Buddhist, Hindu, Ethnic  
Complete data includes: dates, mythology, rituals, connected deities

### Temples (15 entries)
Types: Temple, Stupa, Monastery, Heritage Site  
Data includes: coordinates, significance, associated festivals

### Accuracy Validation (v2.0)
- 45-case test suite (15 festivals × 3 years)
- 97% accuracy against official sources
- Tithi accuracy: ±2 minutes at boundaries

---

## 🛠️ API Endpoints

`/v5/api/*` is the authority track (spec + proof-first enriched `data/meta` envelope).  
`/v4/api/*` is the normalized contract track (canonical `data/meta` envelope).  
`/v3/api/*` remains the LTS compatibility track.

### Authority Track (v5)
- `GET /v5/api/resolve?date=YYYY-MM-DD` — Unified BS + panchanga + observance resolution with trace
- `GET /v5/api/spec/conformance` — Spec and conformance status/report
- `GET /v5/api/provenance/verify/trace/{trace_id}` — Deterministic trace integrity verification
- `GET /v5/api/integrations/feeds/all.ics` — Integration-facing ICS feed alias
- `GET /v5/api/festivals/coverage` — Rule-catalog coverage progress toward 300+ target
- `GET /v5/api/public/artifacts/manifest` — Public artifact index (precomputed + reports)
- `GET /v5/api/public/artifacts/dashboard` — Authority dashboard artifact
- `GET /v5/api/public/artifacts/precomputed/{filename}` — Precomputed JSON file download

### Authority Pipelines
- `python3 scripts/rules/ingest_rule_sources.py` — Rule-ingestion pipeline (builds canonical v4 catalog; currently 453 entries)
- `python3 scripts/rules/ingest_rule_sources.py --check --target 300` — CI drift/coverage gate
- `python3 scripts/generate_authority_dashboard.py` — Auto-publishes discrepancy classes + confidence breakdown from CI artifacts
- `python3 scripts/deploy/build_static_artifacts_site.py` — Builds static deployment bundle for GitHub Pages

### Free Deployment
- GitHub Pages workflow: `.github/workflows/deploy-pages.yml`
- Render free-tier API config: `render.yaml`
- Full guide: [`/docs/deployment/DEPLOY_FREE.md`](./docs/deployment/DEPLOY_FREE.md)

### Festivals
- `GET /v3/api/festivals` — List all festivals
- `GET /v3/api/festivals/upcoming` — Upcoming in next N days
- `GET /v3/api/festivals/{id}` — Festival detail with mythology
- `GET /v3/api/festivals/{id}/dates?years=5` — Calculated dates
- `GET /v3/api/festivals/{id}/explain?year=YYYY` — Human-readable date explanation

### Calendar
- `GET /v3/api/calendar/today` — Current date in all calendars
- `GET /v3/api/calendar/convert` — Convert between calendars (with confidence)
- `GET /v3/api/calendar/convert/compare` — Official vs estimated conversion comparison
- `GET /v3/api/calendar/panchanga` — Full 5-element panchanga (v2.0)
- `GET /v3/api/calendar/tithi` — Udaya tithi details with method metadata
- `GET /v3/api/cache/stats` — Precomputed artifact coverage and cache inventory
- `GET /v3/api/engine/config` — Active ephemeris configuration
- `GET /v3/api/engine/health` — Ephemeris health and runtime mode
- `GET /v3/api/engine/calendars` — Registered calendar plugins
- `GET /v3/api/engine/convert?date=YYYY-MM-DD&calendar=...` — Plugin-based conversion
- `GET /v3/api/engine/observance-plugins` — Registered observance plugins
- `GET /v3/api/engine/observance-calculate?plugin=...&rule_id=...&year=...` — Plugin observance calculation
- `GET /v3/api/engine/observances?plugin=...&rule_id=...&year=...` — Backward-compatible alias

### Temples
- `GET /v3/api/temples` — List all temples
- `GET /v3/api/temples/{id}` — Temple detail
- `GET /v3/api/temples/for-festival/{id}` — Temples for a festival

### Provenance
- `GET /v3/api/provenance/root` — Active snapshot metadata and root
- `POST /v3/api/provenance/snapshot/create` — Create hash snapshot record
- `GET /v3/api/provenance/snapshot/{snapshot_id}/verify` — Verify snapshot integrity
- `GET /v3/api/provenance/proof` — Merkle inclusion proof for festival date
- `GET /v3/api/provenance/dashboard` — Public beta metrics artifact
- `GET /v3/api/provenance/transparency/log` — Append-only transparency log tail
- `GET /v3/api/provenance/transparency/audit` — Hash-chain integrity audit
- `GET /v3/api/provenance/transparency/replay` — Replay-derived state
- `GET /v3/api/provenance/transparency/anchor/prepare` — Anchor payload preparation
- `POST /v3/api/provenance/transparency/anchor/record` — Record external anchor ref

### Variants
- `GET /v3/api/festivals/{id}/variants?year=YYYY` — Regional/tradition observance variants

### Cross-Calendar Resolver
- `GET /v3/api/observances?date=YYYY-MM-DD&location=...&preferences=...` — Ranked cross-calendar observances
- `GET /v3/api/observances/today` — Resolved observances for today
- `GET /v3/api/observances/next?from_date=YYYY-MM-DD&days=30` — Next observance in horizon
- `GET /v3/api/observances/stream?start=YYYY-MM-DD&days=7` — Poll-style multi-day observance stream
- `GET /v3/api/observances/conflicts` — Curated conflict scenario dataset

### iCal Feeds
- `GET /v3/api/feeds/ical?festivals=dashain,tihar&years=2` — Ad-hoc ICS feed
- `GET /v3/api/feeds/all.ics` — Full festival feed
- `GET /v3/api/feeds/national.ics` — National-only feed
- `GET /v3/api/feeds/newari.ics` — Newari-only feed
- `GET /v3/api/feeds/custom.ics?festivals=...` — Custom subscription feed

### Webhooks
- `POST /v3/api/webhooks/subscribe` — Create subscription
- `GET /v3/api/webhooks` — List subscriptions
- `GET /v3/api/webhooks/{id}` — Read subscription
- `DELETE /v3/api/webhooks/{id}` — Delete subscription
- `POST /v3/api/webhooks/dispatch?date=YYYY-MM-DD` — Trigger dispatch run

### Forecasting
- `GET /v3/api/forecast/festivals?year=YYYY&festivals=...` — Long-horizon date forecast with confidence decay
- `GET /v3/api/forecast/error-curve?start_year=YYYY&end_year=YYYY` — Accuracy decay curve by horizon

### Explainability
- `GET /v3/api/festivals/{id}/explain?year=YYYY` — Human-readable explanation with `calculation_trace_id`
- `GET /v3/api/explain/{trace_id}` — Deterministic technical reason trace
- `GET /v3/api/explain?limit=20` — Recent trace list

### Reliability & Policy
- `GET /v3/api/reliability/status` — Runtime health + cache/ephemeris status
- `GET /v3/api/reliability/slos` — Evaluated SLO targets from report artifacts
- `GET /v3/api/reliability/playbooks` — Incident response playbook index
- `GET /v3/api/policy` — Response usage policy/disclaimer metadata

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [project-spec.md](./project-spec.md) | Complete project reference |
| [AS_BUILT.md](./docs/AS_BUILT.md) | Evidence-based list of implemented capabilities |
| [VISION.md](./docs/VISION.md) | Planned capabilities not yet implemented |
| [GOVERNANCE_BASELINE.md](./docs/GOVERNANCE_BASELINE.md) | Truthfulness, version, and CI governance baseline |
| [IMPLEMENTATION_PLAN_V2.md](./docs/IMPLEMENTATION_PLAN_V2.md) | 5-day ephemeris upgrade sprint |
| [DATE_ACCURACY_EVALUATION.md](./docs/DATE_ACCURACY_EVALUATION.md) | Validation results |
| [DATA_SOURCES.md](./docs/DATA_SOURCES.md) | Source citations |
| [SDK_USAGE.md](./docs/SDK_USAGE.md) | SDK usage notes (Python/TS/Go) |
| [DEPLOY_FREE.md](./docs/deployment/DEPLOY_FREE.md) | Zero-budget deployment guide (GitHub Pages + Render) |
| [GOVERNANCE.md](./docs/GOVERNANCE.md) | Rule-change governance workflow |
| [YEAR_2_COMPLETION_REPORT.md](./docs/YEAR_2_COMPLETION_REPORT.md) | Year-2 closure summary |
| [YEAR_3_KICKOFF.md](./docs/YEAR_3_KICKOFF.md) | Year-3 startup plan and priorities |
| [YEAR_3_PROGRESS.md](./docs/YEAR_3_PROGRESS.md) | Year-3 execution status (weeks 1–52) |
| [YEAR_3_COMPLETION_REPORT.md](./docs/YEAR_3_COMPLETION_REPORT.md) | Year-3 closure and final validation summary |
| [MIGRATION_V2_V3.md](./docs/MIGRATION_V2_V3.md) | v2 to v3 migration mapping |
| [LTS_POLICY.md](./docs/LTS_POLICY.md) | v3 LTS compatibility and freeze policy |
| [BENCHMARK_SPEC.md](./docs/BENCHMARK_SPEC.md) | Open benchmark pack/harness specification |
| [UNCERTAINTY_SPEC.md](./docs/UNCERTAINTY_SPEC.md) | Uncertainty model and API semantics |
| [FORECASTING_API.md](./docs/FORECASTING_API.md) | Forecast endpoint contract and report generation |
| [M29_ZERO_COST_SCALE.md](./docs/M29_ZERO_COST_SCALE.md) | Precompute + cache + load-test operations |
| [RELIABILITY.md](./docs/RELIABILITY.md) | SLO targets and incident playbooks |
| [POLICY.md](./docs/POLICY.md) | API usage/disclaimer policy |
| [POLICY_QA.md](./docs/POLICY_QA.md) | Policy scenario QA matrix and checks |
| [INSTITUTIONAL_USAGE.md](./docs/INSTITUTIONAL_USAGE.md) | Institutional integration guidance |
| [INSTITUTIONAL_DEPLOYMENT.md](./docs/INSTITUTIONAL_DEPLOYMENT.md) | Offline bundle and deployment steps |
| [EXPLAIN_SPEC.md](./docs/EXPLAIN_SPEC.md) | Deterministic reason-trace schema |
| [EXPLAINABILITY.md](./docs/EXPLAINABILITY.md) | Explainability assistant implementation notes |
| [PARVA_TEMPORAL_SPEC_1_0.md](./docs/PARVA_TEMPORAL_SPEC_1_0.md) | Unified temporal standard document |
| [PARVA_CONFORMANCE_TESTS.md](./docs/PARVA_CONFORMANCE_TESTS.md) | Conformance runner and required checks |
| [SPEC1_ABSTRACT.md](./docs/SPEC1_ABSTRACT.md) | Academic-style Spec 1.0 abstract |
| [SPEC1_ANNOUNCEMENT.md](./docs/SPEC1_ANNOUNCEMENT.md) | Public release note for Spec 1.0 |
| [YEAR_3_RETROSPECTIVE.md](./docs/YEAR_3_RETROSPECTIVE.md) | Year 3 retrospective summary |
| [THREE_YEAR_RETROSPECTIVE.md](./docs/THREE_YEAR_RETROSPECTIVE.md) | 3-year program retrospective |
| [SECURITY.md](./SECURITY.md) | Security posture and reporting policy |

---

## 📜 License

MIT © 2026

---

## 🙏 Acknowledgments

Built with:
- **Swiss Ephemeris** (pyswisseph) — Swiss/Moshier ephemeris mode (default)
- **OpenStreetMap Nepal** — Temple and location data
- **Nepal Government Calendar** — Official holiday verification
- **Rashtriya Panchang** — Traditional astronomical almanac

---

*Project Parva v3.0 LTS — Ephemeris-powered festival discovery*
