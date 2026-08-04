---
status: public-beta
tier: 1
lane: dx
last_verified: 2026-05-14
owner: dx-team
---

# API Reference v3

Status: stable core plus public/developer preview route profiles.

Project Parva v3 APIs are designed to run in two deployment profiles:

1. A public demo profile for safe API evaluation.
2. A private or full deployment profile for organizations that need controlled calendar validation, internal audit workflows, or sensitive future-BS research surfaces.

The current public deployment uses:

| Layer | Platform | URL |
|---|---|---|
| Frontend | Cloudflare Pages | https://prabinghimire1.com.np |
| Backend API | Render | https://api.prabinghimire1.com.np |
| Source code | GitHub | https://github.com/dantwoashim/Project_Parva |

The public backend is intentionally narrower than a full private deployment. It exposes stable public calendar and methodology surfaces, while private or experimental future-BS workflows stay disabled by default.

## Public deployment boundary

The public API demo is for technical evaluation, documentation, and public-safe calendar functionality.

Public surfaces may include:

- health/status endpoints
- BS/AD conversion
- current Nepali date
- BS date validation
- fiscal-year helpers where enabled
- compliance-profile helpers in full/private deployments where enabled
- TimeGraph fact and trace helpers where enabled
- RuleLang structured temporal rule helpers where enabled
- impact simulation helpers where enabled
- agent-safe temporal tools where enabled
- Parva Protocol preview helpers where enabled
- public panchanga endpoints where enabled
- public festival endpoints where enabled
- future-BS capability, methodology, and curated single-year forecast routes

Private or experimental surfaces must stay disabled by default on the public deployment:

- raw future BS model workflows
- bulk future range prediction
- CSV/XLSX future exports
- model runs
- backtests
- residual analysis
- client sheet comparison
- loan-impact simulation
- corrected future values
- private audit workflows

Future-BS research outputs are treated as:

`computed_prediction_not_official`

Project Parva is not an official government calendar publication, legal authority, tax authority, banking-contract authority, or replacement for official Nepali calendar publication.

## API host

The public frontend is hosted on Cloudflare Pages. The public backend API is hosted on Render.

Production URLs:

```text
https://prabinghimire1.com.np
https://api.prabinghimire1.com.np
```

## Core public API contract

The public v3 contract is centered on a small set of stable calendar and enterprise helpers.

| Endpoint | Method | Purpose |
|---|---:|---|
| `/v3/api/calendar/today` | GET | Current Nepali calendar context |
| `/v3/api/calendar/convert?date=YYYY-MM-DD` | GET | Gregorian to Bikram Sambat conversion |
| `/v3/api/calendar/bs-to-gregorian` | POST | Bikram Sambat to Gregorian conversion and BS date validation |
| `/v3/api/calendar/dual-month?year=YYYY&month=M` | GET | Gregorian month calendar with BS context |
| `/v3/api/enterprise/fiscal-year/{bs_year}` | GET | Nepali fiscal-year boundaries |
| `/v3/api/enterprise/bs-months/{bs_year}` | GET | BS month metadata for a year; defaults to canonical trust-arrest selection over solar-civil sankranti computation; `?mode=solar_civil`, `?mode=static_lookup`, and `?mode=compare` are explicit audit/reference modes |
| `/v3/api/enterprise/business-days` | POST | Weekend-rule business-day count for a BS date range |
| `/v3/api/enterprise/capabilities` | GET | Enterprise calendar capability metadata |
| `/v3/api/compliance/profiles` | GET | Enterprise compliance profile catalog |
| `/v3/api/compliance/evaluate-date` | POST | Source-aware working-day and review-required decision |
| `/v3/api/compliance/next-working-day` | POST | Next working day for a profile with bounded search |
| `/v3/api/compliance/previous-working-day` | POST | Previous working day for a profile with bounded search |
| `/v3/api/compliance/add-working-days` | POST | Add or subtract working days with a bounded search window |
| `/v3/api/compliance/month-closing-day` | POST | Last calendar day and last working day for a BS month |
| `/v3/api/compliance/fiscal-period` | POST | Nepali fiscal period for a BS or AD date |
| `/v3/api/trust/capabilities` | GET | Public trust infrastructure metadata |
| `/v3/api/trust/sources` | GET | Public source registry records |
| `/v3/api/trust/releases` | GET | Public release manifests |
| `/v3/api/trust/releases/{from_release}/diff/{to_release}` | GET | Metadata-level release diff |
| `/v3/api/trust/log` | GET | Public trust log entries |
| `/v3/api/trust/evidence/date-conversion` | POST | Hashable date-conversion evidence packet |
| `/v3/api/trust/evidence/compliance-decision` | POST | Hashable compliance decision evidence packet |
| `/v3/api/timegraph/capabilities` | GET | Public TimeGraph capability metadata |
| `/v3/api/timegraph/facts` | GET | Bounded public temporal fact listing |
| `/v3/api/timegraph/facts/{fact_id}` | GET | Fact detail with direct relationships |
| `/v3/api/timegraph/facts/{fact_id}/trace` | GET | Bounded source, release, decision, and evidence trace |
| `/v3/api/timegraph/query` | POST | Filtered public TimeGraph query |
| `/v3/api/timegraph/conflicts` | GET | Public conflict records, including fixture-only conflict tests |
| `/v3/api/rules/capabilities` | GET | RuleLang capability and safety summary |
| `/v3/api/rules` | GET | Public RuleLang rule registry |
| `/v3/api/rules/{rule_id}` | GET | Public RuleLang rule definition |
| `/v3/api/rules/validate` | POST | Validate a structured RuleLang rule |
| `/v3/api/rules/{rule_id}/evaluate` | POST | Execute a public RuleLang rule |
| `/v3/api/rules/{rule_id}/test` | POST | Run embedded tests for a public rule |
| `/v3/api/rules/evaluate` | POST | Evaluate a public-safe custom rule |
| `/v3/api/rules/explain` | POST | Return a rule decision and bounded explanation trace |
| `/v3/api/impact/capabilities` | GET | Temporal impact simulator capability summary |
| `/v3/api/impact/simulate-change-set` | POST | Bounded impact simulation for public temporal changes |
| `/v3/api/impact/simulate-release-diff` | POST | Impact simulation from a semantic release diff |
| `/v3/api/agent/capabilities` | GET | Agent-safe temporal intelligence capability summary |
| `/v3/api/agent/tools` | GET | Deterministic agent tool registry |
| `/v3/api/agent/verify-claim` | POST | Verify a supported temporal claim with review gates |
| `/v3/api/agent/plan-schedule` | POST | Produce a bounded schedule plan with source-aware metadata |
| `/v3/api/protocol/version` | GET | Parva Protocol version metadata |
| `/v3/api/protocol/capabilities` | GET | Parva Protocol public preview capability summary |
| `/v3/api/protocol/conformance/run` | POST | Run the local protocol conformance preview |
| `/v3/api/protocol/credentials/issue` | POST | Issue a hash-only preview calendar credential |
| `/v3/api/protocol/credentials/verify` | POST | Verify a hash-only preview calendar credential |
| `/v3/api/policy` | GET | Source and claim-boundary policy metadata |
| `/v4/api/future-bs/capabilities` | GET | Public-safe future-BS research capability summary |
| `/v4/api/future-bs/methodology` | GET | Selected solar-civil model and validation methodology |
| `/v4/api/future-bs/forecast/{bs_year}` | GET | Curated month-length forecast for one year from 2084 through 2200 BS |

Core calendar and enterprise responses include source, confidence, provenance, engine, or policy fields where meaningful. Future-BS forecast responses remain labeled `computed_prediction_not_official` and require review.

## Source-aware metadata

Core temporal responses include an additive `meta` object where meaningful:

```json
{
  "meta": {
    "source": {
      "id": "parva_public_bs_ad_corpus",
      "label": "Parva public BS/AD corpus",
      "tier": "software_table_reference",
      "authority": "derived_reference_not_legal_authority",
      "version": "parva-public-calendar-v1"
    },
    "confidence": "source_backed",
    "data_version": "parva-public-calendar-v1",
    "release_id": "parva-bs-public-demo",
    "claim_boundary": "public_corpus_reference_only",
    "warnings": ["not_legal_tax_or_banking_contract_authority"],
    "trace_id": "request-trace-id",
    "result_class": "ad_to_bs_conversion"
  }
}
```

See `docs/SOURCE_AWARE_METADATA.md` for source tiers, confidence levels, claim boundaries, and unsupported-range behavior.

## Trust API preview

The trust layer exposes source registry records, release manifests, release diffs, trust logs, and evidence packets.

Example:

```bash
curl https://api.prabinghimire1.com.np/v3/api/trust/capabilities
```

Date-conversion evidence packet:

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/trust/evidence/date-conversion \
  -H "Content-Type: application/json" \
  -d '{"ad_date":"2026-04-14"}'
```

Evidence packets include a release id, source records, confidence, claim boundary, warnings, trace id, and packet hash. Public packets use `unsigned_public_preview` and are not legal certificates.

See `docs/API_TRUST.md`, `docs/RELEASES.md`, and `docs/EVIDENCE_PACKETS.md`.

## TimeGraph preview

TimeGraph links public temporal facts to sources, releases, profiles,
relationships, evidence packets, and conflicts.

Example:

```bash
curl https://api.prabinghimire1.com.np/v3/api/timegraph/capabilities
```

Trace a public date-mapping fact:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/timegraph/facts/fact_bs_ad_2083_01_01/trace?depth=2"
```

TimeGraph responses are bounded and public-safe. They are audit support, not legal,
tax, payroll, banking-contract, or government authority.

See `docs/TIMEGRAPH.md`, `docs/TIMEGRAPH_FACTS.md`, `docs/TIMEGRAPH_API.md`, and `docs/TIMEGRAPH_CONFLICTS.md`.

## RuleLang preview

RuleLang is a structured rule engine for institutional temporal decisions. It uses JSON rules, allowlisted temporal functions, bounded loops, risk policies, reason codes, and explanation traces.

Example:

```bash
curl https://api.prabinghimire1.com.np/v3/api/rules/capabilities
```

Evaluate a public rule:

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/rules/last_working_day_of_nepali_month/evaluate \
  -H "Content-Type: application/json" \
  -d '{"input":{"bs_month":"2082-04","profile_id":"nepal_private_company_default"}}'
```

RuleLang is decision support. It is not legal, tax, payroll, banking-contract, or government authority.

See `docs/RULELANG.md`, `docs/RULELANG_SCHEMA.md`, `docs/RULELANG_BUILTINS.md`, `docs/RULELANG_API.md`, and `docs/RULELANG_SECURITY.md`.

## Impact, agent, and protocol previews

The impact simulator, agent-safe tool layer, and Parva Protocol preview are public-safe alpha surfaces. They expose bounded simulation, deterministic temporal tools, conformance metadata, and hash-only credential checks. They do not expose private future-BS vectors, private calibration logic, or legal authority.

Examples:

```bash
curl https://api.prabinghimire1.com.np/v3/api/impact/capabilities
curl https://api.prabinghimire1.com.np/v3/api/agent/tools
curl https://api.prabinghimire1.com.np/v3/api/protocol/version
```

See `docs/IMPACT_API.md`, `docs/AGENT_API.md`, and `docs/PARVA_PROTOCOL.md`.

## Error envelope

Public input errors preserve the legacy `detail` field and also include a structured error object:

```json
{
  "detail": "Invalid date format. Use YYYY-MM-DD",
  "request_id": "trace-id",
  "version": "3.0.0",
  "error": {
    "code": "BAD_REQUEST",
    "message": "Invalid date format. Use YYYY-MM-DD",
    "details": {},
    "trace_id": "trace-id"
  }
}
```

Validation errors use `REQUEST_VALIDATION_ERROR` and include validation details under `error.details.errors`.

## SDK coverage

The alpha JavaScript and Python SDKs cover the same core public surfaces:

- today
- AD to BS conversion
- BS to AD conversion
- BS date validation through conversion
- month calendar
- fiscal-year boundaries
- BS month metadata
- business-day helper
- enterprise capabilities
- compliance profile helpers
- trust source, release, log, and evidence helpers
- TimeGraph fact, relationship, trace, and conflict helpers
- RuleLang registry, validation, execution, test, and explanation helpers
- impact simulator helpers
- agent-safe deterministic temporal helpers
- Parva Protocol conformance and credential helpers
- public policy
- future-BS capabilities summary

SDK examples are in `docs/API_QUICKSTART.md`.

## Compliance preview

The compliance preview endpoints are decision-support surfaces for organizations. They return profile id, normalized dates, decision flags, reason codes, fiscal period context, source-aware metadata, warnings, and a review-required flag. They are not legal, tax, payroll, banking-contract, or government authority.

Built-in profile ids:

- `nepal_public_general`
- `nepal_government_general`
- `nepal_banking_general`
- `nepal_private_company_default`
- `nepal_school_general`
- `custom_demo_company`

Reason codes are machine-readable. Common codes include `WEEKDAY`, `WEEKEND`, `SATURDAY_NON_WORKING`, `PUBLIC_HOLIDAY_MATCH`, `NO_MATCHING_PUBLIC_HOLIDAY`, `PROFILE_REQUIRES_OFFICIAL_SOURCE`, `SOURCE_CONFIDENCE_TOO_LOW`, `FUTURE_DATE_REVIEW_REQUIRED`, and `PAYROLL_REVIEW_REQUIRED`.

Example:

```bash
curl -X POST https://api.prabinghimire1.com.np/v3/api/compliance/evaluate-date \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"nepal_private_company_default","bs_date":"2082-04-02"}'
```

Response shape:

```json
{
  "profile_id": "nepal_private_company_default",
  "date": {
    "bs": "2082-04-02",
    "ad": "2025-07-17"
  },
  "decision": {
    "is_working_day": true,
    "is_business_day": true,
    "is_payroll_safe": true,
    "requires_human_review": false,
    "reason_codes": ["WEEKDAY", "NO_MATCHING_PUBLIC_HOLIDAY"],
    "holiday": null
  },
  "meta": {
    "confidence": "official_verified",
    "claim_boundary": "enterprise_decision_support_not_legal_authority",
    "warnings": ["not_legal_tax_or_banking_contract_authority"]
  }
}
```

See `docs/ENTERPRISE_COMPLIANCE.md` for profile definitions, limitation language, and reason-code details.

## Performance posture

The public API is optimized for lightweight calendar evaluation. Health, readiness, conversion, today, month, fiscal-year, and month metadata endpoints should be fast under local test conditions. Festival, panchanga, kundali, and location-sensitive surfaces may do more computation and should be measured separately for deployment-specific budgets.

Use this local helper to measure warmed public endpoints:

```bash
python3.11 scripts/release/measure_public_api_performance.py
```

## Canonical route families

The canonical route inventory is generated from the FastAPI app and checked in `docs/ROUTE_ACCESS.md`.

Current v3 route families:

- `admin`
- `agent`
- `billing`
- `cache`
- `calendar`
- `compliance`
- `engine`
- `enterprise`
- `explain`
- `feeds`
- `festivals`
- `forecast`
- `glossary`
- `impact`
- `integrations`
- `keys`
- `kundali`
- `me`
- `muhurta`
- `observances`
- `personal`
- `places`
- `policy`
- `provenance`
- `protocol`
- `public`
- `reliability`
- `resolve`
- `rules`
- `spec`
- `temples`
- `temporal`
- `timegraph`
- `trust`
- `webhooks`

Route presence in this reference does not mean every route is available on the lightweight public demo. Public and private deployment boundaries are documented in `docs/PUBLIC_API_BOUNDARY.md`.
