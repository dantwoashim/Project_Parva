# Project Parva

[![CI](https://github.com/dantwoashim/Project_Parva/actions/workflows/ci.yml/badge.svg)](https://github.com/dantwoashim/Project_Parva/actions/workflows/ci.yml)
[![Public verification](https://github.com/dantwoashim/Project_Parva/actions/workflows/public-verification.yml/badge.svg)](https://github.com/dantwoashim/Project_Parva/actions/workflows/public-verification.yml)
![Benchmark](public-benchmark/results/benchmark.svg)

Project Parva is an open-source Nepali date/time API and conformance project.

It covers BS to AD, AD to BS, Nepali date validation, holidays, working days,
Nepal fiscal year logic, BS month metadata, Panchanga computation, proof
receipts, local verification, SDKs, MCP tools, and public regression fixtures.

The project exists because Nepali date bugs often hide until a boundary is hit:
a frontend calendar table disagrees with backend data, a payroll month has the
wrong number of days, a datepicker accepts an invalid BS date, or a future BS
date changes after someone already used it in a workflow.

Parva treats those cases as conformance problems, not just conversion problems.
It records source and method provenance, separates exact evidence from
review-needed evidence, and gives developers a way to test what their Nepali
calendar API or Nepali date converter is actually doing.

## Start Here

- Quickstart: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- OpenAPI snapshot: [docs/api-docs/openapi.json](docs/api-docs/openapi.json)
- API versioning: [docs/API_VERSIONING_AND_DEPRECATION.md](docs/API_VERSIONING_AND_DEPRECATION.md)
- Proof mode: [docs/PROOF_MODE.md](docs/PROOF_MODE.md)
- Panchanga engine: [docs/PANCHANGA_ENGINE.md](docs/PANCHANGA_ENGINE.md)
- Agent tooling guide: [docs/AGENT_TOOLING_GUIDE.md](docs/AGENT_TOOLING_GUIDE.md)
- Architecture: [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
- Migration status: [docs/architecture/MIGRATION_STATUS.md](docs/architecture/MIGRATION_STATUS.md)
- Artifact policy: [artifacts/POLICY.md](artifacts/POLICY.md)
- Safe claims: [docs/SAFE_CLAIMS.md](docs/SAFE_CLAIMS.md)
- Public benchmark: [public-benchmark/README.md](public-benchmark/README.md)
- Public conformance index: [docs/benchmarks/NEPALI_DATE_CONFORMANCE_INDEX.md](docs/benchmarks/NEPALI_DATE_CONFORMANCE_INDEX.md)
- Public failure classes: [docs/benchmarks/PUBLIC_NEPALI_DATE_FAILURE_CLASSES.md](docs/benchmarks/PUBLIC_NEPALI_DATE_FAILURE_CLASSES.md)
- Nepal compliance profile: [docs/conformance/nepal-compliance-profile.md](docs/conformance/nepal-compliance-profile.md)
- Yarsa source-drift case study: [docs/case-studies/yarsa-calendar-source-drift.md](docs/case-studies/yarsa-calendar-source-drift.md)
- External reviewer packet: [docs/external/REVIEWER_PACKET.md](docs/external/REVIEWER_PACKET.md)

Live public evaluation surfaces:

- Website: [https://prabinghimire1.com.np](https://prabinghimire1.com.np)
- API docs: [https://api.prabinghimire1.com.np/docs](https://api.prabinghimire1.com.np/docs)
- OpenAPI: [https://api.prabinghimire1.com.np/openapi.json](https://api.prabinghimire1.com.np/openapi.json)

The hosted API is a public evaluation deployment. First requests may be slower when the instance wakes up.

## Why This Exists

Most Nepali date bugs are small on paper and expensive in context.

Many systems carry hardcoded Bikram Sambat month tables. A backend CSV, a
frontend Nepali datepicker bundle, and a reporting job can each have their own
copy. They may all look reasonable until one month differs by a day.

That one day can move:

- a payroll period,
- a fiscal-year boundary,
- a certificate or DOB validation,
- an invoice/report date,
- an attendance or leave record,
- a future BS date that should have stayed review-needed.

Software agents add another failure mode: if the tool does not expose source,
confidence, and boundary data, the model will often answer as if the date is
settled. Parva is built to make those boundaries visible.

The project turns public Nepali date failures into fixtures and checks where
the evidence is exact enough. When the evidence is partial, it stays marked for
review instead of becoming a fake assertion.

## Free Nepali Date Risk Audit

If you maintain Nepal-facing payroll, ERP, accounting, attendance, school,
cooperative, public-service, government-form, or datepicker software, you can
send one small workflow or sample output.

No integration required. No dependency required. No sales call required. No
authority claim.

Good inputs:

- 10 sample BS/AD date outputs
- one payroll, fiscal-year, invoice, attendance, report, certificate, or DOB workflow
- one public repo, issue, Nepali datepicker, or library case
- one real edge case your team has seen in production or testing

Checks:

- BS/AD conversion boundaries
- invalid BS dates
- month lengths
- frontend/backend calendar source drift
- fiscal and payroll month boundaries
- holiday and working-day assumptions
- future BS dates that should be marked review-needed

You get:

- a short technical report
- pass, warning, and review-needed findings
- suggested regression tests
- source and provenance notes
- authority-boundary notes

Request one:

- GitHub: [dantwoashim](https://github.com/dantwoashim)
- Email: <twodan033@gmail.com>

Fast conformance path:

```powershell
py -3.11 tools\conformance_runner\run.py --suite public-nepali-date-issues
py -3.11 tools\conformance_runner\run.py --profile nepal-compliance
py -3.11 tools\conformance_runner\run.py --suite public-nepali-date-issues --write-report reports\conformance\public-issue-suite-summary.json
```

## What Parva Does

| Area | What it provides |
| --- | --- |
| Nepali date API | BS to AD, AD to BS, today, validation, month metadata, supported-range metadata |
| Civil proof mode | Replay-verifiable membranes for conversion, validation, holidays, working days, fiscal years, and BS months |
| Panchanga engine | Method-docketed sunrise, tithi, nakshatra, yoga, karana, paksha, vara, ephemeris metadata, and proof receipts |
| Payroll/date-risk audit | CSV/API-oriented decision-support checks for invalid dates, holidays, non-working days, fiscal boundaries, and review-required cases |
| Local verification | Shared proof fixtures and a buildable `@project-parva/local-kernel` npm package for offline replay checks |
| SDKs | Python and JavaScript clients with proof modes and conservative verification helpers |
| Agent/MCP | Read-only, public-safe agent tool wrappers and MCP adapter surfaces that preserve boundaries and review gates |
| Benchmark | Public Nepali Time Reliability Benchmark for deterministic date reasoning, source awareness, and review behavior |
| Governance | Source/method dockets, public claims checker, route maturity, OpenAPI drift checks, and reproducible public verification |
| Research boundary | Future-BS research kept separate from public authority claims, with compatibility shims only where older imports need them |

## Public Conformance Work

Parva tracks public Nepali date issues and turns them into fixtures or runnable
checks when the evidence is exact enough. The suite separates verified public
issues, reported issues, partial evidence, business workflow evidence, and
future-date review cases.

Project Parva's benchmark work contributed a standalone calendar source
consistency guard to `yarsa/nepal-compliance`.

That check compared duplicated frontend/backend BS month tables. It did not add
a Parva dependency, change upstream runtime behavior, or prove production
impact.

Run the public issue conformance suite:

```powershell
py -3.11 tools\conformance_runner\run.py --suite public-nepali-date-issues
py -3.11 tools\conformance_runner\run.py --profile nepal-compliance
py -3.11 tools\conformance_runner\run.py --suite public-nepali-date-issues --write-report reports\conformance\public-issue-suite-summary.json
py -3.11 -m pytest tests/conformance -q
```

Conformance docs:

- [Public conformance index](docs/benchmarks/NEPALI_DATE_CONFORMANCE_INDEX.md)
- [Failure classes from public issues](docs/benchmarks/PUBLIC_NEPALI_DATE_FAILURE_CLASSES.md)
- [Generated artifact: public issue summary](reports/conformance/public-issue-suite-summary.md)
- [Nepal compliance profile](docs/conformance/nepal-compliance-profile.md)
- [Yarsa source-drift case study](docs/case-studies/yarsa-calendar-source-drift.md)
- [Conformance Milestone 001](docs/releases/CONFORMANCE_MILESTONE_001.md)

These fixtures are public regression and review artifacts. They are not
calendar publication, legal guidance, tax guidance, payroll approval, banking
guidance, or ritual authority.

## Who This Helps

- Date library maintainers who want regression cases from real public issues.
- ERP, payroll, accounting, school, cooperative, and attendance teams that need
  safer BS/AD boundaries.
- Reviewers of public-service or government-form workflows where invalid BS
  dates should not slip through.
- Developers building a Nepali calendar API, Bikram Sambat API, or Nepali
  datepicker regression suite.
- Software-agent and MCP tool builders who need deterministic answers with
  proof receipts instead of guessed dates.
- Auditors and maintainers who need source notes, not broad claims.

## Quickstart

Base URL:

```text
https://api.prabinghimire1.com.np/v3/api
```

AD to BS:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/convert?date=2025-04-14"
```

BS to AD:

```bash
curl -X POST "https://api.prabinghimire1.com.np/v3/api/calendar/bs-to-gregorian" \
  -H "Content-Type: application/json" \
  -d '{"year":2082,"month":1,"day":1}'
```

Validate a BS date:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/validate-bs-date?year=2082&month=1&day=32"
```

Holiday membership:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/compliance/holiday?bs_date=2082-01-01"
```

Working-day decision support:

```bash
curl -X POST "https://api.prabinghimire1.com.np/v3/api/compliance/evaluate-date" \
  -H "Content-Type: application/json" \
  -d '{"profile_id":"nepal_private_company_default","bs_date":"2082-01-01","decision_intent":"general"}'
```

Fiscal year:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/enterprise/fiscal-year/2082"
```

BS month metadata:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/enterprise/bs-months/2082?mode=compare"
```

Panchanga summary:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/panchanga?date=2025-04-14"
```

## Proof Mode

Stable civil routes and Panchanga can return proof receipts:

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/convert?date=2025-04-14&proof=replay"
```

```bash
curl "https://api.prabinghimire1.com.np/v3/api/calendar/panchanga?date=2025-04-14&proof=replay&lat=27.7172&lon=85.324&tz=Asia/Kathmandu"
```

A proof response includes a membrane capsule, identity hash, witness hash, field provenance, boundary vector, source or method docket references, policy trace, and replay instructions. The verifier must replay operation semantics or validate pinned proof content; hash presence alone is not enough.

Proof-supported civil operations:

- `convert_bs_to_ad`
- `ad_to_bs`
- `validate_bs_date`
- `holiday`
- `working_day`
- `fiscal_year`
- `bs_months`

Panchanga proof currently covers method-docketed `panchanga_summary` with pinned fixture replay and explicit ephemeris metadata.

## Panchanga Engine

Parva computes Panchanga signals as method-backed astronomical outputs, not as a final almanac, publication, or ritual decision source.

The proof-carrying Panchanga layer records:

- date, latitude, longitude, timezone
- ephemeris provider and provider kind
- fixture or kernel hash when applicable
- ayanamsa and sidereal mode
- sunrise attribution rule
- method dockets for sunrise, tithi, nakshatra, yoga, karana, and related calculations
- field provenance and boundary vector
- `computed_not_official`, `not_panchanga_authority`, and `not_ritual_final_authority`

JPL support is explicit and bounded. The repo exposes a JPL DE440-family provider interface and kernel-hash disclosure path. Large JPL kernels are not bundled. If no kernel is configured, Parva must not silently claim JPL-backed output.

See [docs/PANCHANGA_ENGINE.md](docs/PANCHANGA_ENGINE.md), [docs/spec/PARVA_EPHEMERIS_PROVIDER_v1.md](docs/spec/PARVA_EPHEMERIS_PROVIDER_v1.md), and [docs/spec/PARVA_PANCHANGA_PROOF_v1.md](docs/spec/PARVA_PANCHANGA_PROOF_v1.md).

## Payroll and Date-Risk Audit

Parva includes a proof-carrying payroll/date-risk workflow for decision support. It checks rows for:

- invalid BS dates
- BS/AD mismatches
- holiday conflicts
- non-working-day conflicts
- fiscal-year boundary issues
- unsupported or review-required ranges
- source or method authority weakness

The workflow can emit row-level proof packs and a Timepack-style aggregate report. It is a precheck/audit aid, not legal, tax, payroll, banking, or compliance authority.

## Local and Offline Verification

Generate shared proof fixtures:

```bash
py -3.11 scripts/release/generate_proof_fixtures.py
```

Run backend fixture replay:

```bash
py -3.11 -m pytest tests/integration/test_shared_proof_fixtures.py -q
```

Run the local kernel:

```bash
cd packages/parva-local-kernel
npm install
npm test
```

The local kernel is a buildable npm package: `@project-parva/local-kernel`. It verifies shared civil fixtures, Panchanga fixtures, proof packs, and Timepack-shaped artifacts without calling the live API.

## SDKs

Python:

```python
from parva import ParvaClient

client = ParvaClient()
payload = client.ad_to_bs("2025-04-14", proof="replay")
print(payload["proof"]["identity_hash"])
```

JavaScript:

```js
import { ParvaClient } from "@project-parva/parva-js";

const client = new ParvaClient();
const payload = await client.getPanchanga({
  date: "2025-04-14",
  proof: "replay",
  lat: 27.7172,
  lon: 85.324,
  tz: "Asia/Kathmandu",
});
console.log(payload.proof.identity_hash);
```

Packages in this repository are prepared for public-beta dry runs. This README does not claim PyPI publication, npm publication, registry acceptance, external certification, or customer adoption.

## Agent and MCP Usage

Parva is useful for software agents because it gives deterministic temporal tools instead of asking models to guess Nepali dates.

Agent-safe surfaces must preserve:

- source or method status
- confidence and boundary vector
- `review_required`
- `not_authority`
- field provenance
- proof links or receipts where available

Packages:

- agent tools: [packages/parva-agent-tools](packages/parva-agent-tools)
- MCP server: [packages/parva-mcp-server](packages/parva-mcp-server)
- Agent guide: [docs/AGENT_TOOLING_GUIDE.md](docs/AGENT_TOOLING_GUIDE.md)

## Future BS Research Forecast

Parva publishes a deterministic research snapshot for `2084-2200 BS` through three read-only endpoints:

```text
GET /v4/api/future-bs/capabilities
GET /v4/api/future-bs/methodology
GET /v4/api/future-bs/forecast/{bs_year}
```

The selected pipeline combines sidereal solar-ingress solving, Nepal civil-time assignment, separate broad-reference and official-authority towers, past-only civil-rule learning, source-aware month-start reconciliation, complete-year constraints, prediction sets, and boundary-risk labels. The forecast response includes all twelve month lengths, normalized model support, agreement, boundary distance, risk flags, method versions, and validation scope.

The official `2078-2083 BS` window reaches `72/72` exact month matches under chronological rolling validation, with each target year trained only on earlier years. It remains a small development-window result rather than broad independent accuracy proof. Broad validation remains below the project's 528 verified-month evidence threshold. Every forecast carries `computed_prediction_not_official`, `review_required=true`, and an authoritative-publication override.

The v7 forecast is now locked by a public source commit, snapshot digest, 117 per-year commitments, and a Merkle root. Later official calendars are scored only from hashed source artifacts reviewed by two people; historical source recovery remains a separate provenance lane.

- Public API contract: [docs/future_bs/API.md](docs/future_bs/API.md)
- Selected method: [docs/future_bs/METHODOLOGY.md](docs/future_bs/METHODOLOGY.md)
- Frozen v7 forecast: [docs/future_bs/V7_FORECAST_FREEZE.md](docs/future_bs/V7_FORECAST_FREEZE.md)
- Official-source acquisition: [docs/future_bs/OFFICIAL_CALENDAR_ACQUISITION_PROTOCOL.md](docs/future_bs/OFFICIAL_CALENDAR_ACQUISITION_PROTOCOL.md)
- BS 2082 boundary diagnosis: [docs/future_bs/2082_BOUNDARY_DIAGNOSIS.md](docs/future_bs/2082_BOUNDARY_DIAGNOSIS.md)
- Research boundary: [docs/future_bs/RESEARCH_BOUNDARY.md](docs/future_bs/RESEARCH_BOUNDARY.md)

## Architecture Overview

Current code is split by responsibility:

- public API/runtime code lives under `backend/app` lanes such as `calendar`, `panchanga`, `sources`, `membranes`, `rules`, `timegraph`, `trust`, and `services`
- Future-BS research and model-risk work lives under `backend/app/research/future_bs`
- `backend/app/future_bs` is a compatibility namespace, not the canonical implementation location
- backend runtime tests live under `tests/backend_runtime`
- local-kernel tests live under `tests/local_kernel`
- tracked MoHA public holiday source PDFs live under `data/source_archive/moha` with `data/source_archive/moha/manifest.json`
- generated or release-sensitive artifacts follow [artifacts/POLICY.md](artifacts/POLICY.md)

```text
public route / SDK / MCP tool
  -> canonical query
  -> source or method coverage resolution
  -> policy decision trace
  -> field-level provenance
  -> boundary vector
  -> membrane capsule
  -> proof pack / Timepack
  -> backend replay verifier and local-kernel verifier
```

Core architecture files:

- Architecture map: [docs/architecture/ARCHITECTURE.md](docs/architecture/ARCHITECTURE.md)
- Migration status: [docs/architecture/MIGRATION_STATUS.md](docs/architecture/MIGRATION_STATUS.md)
- Membranes and replay: [backend/app/membranes](backend/app/membranes)
- Source coverage: [backend/app/sources/coverage.py](backend/app/sources/coverage.py)
- Panchanga proof: [backend/app/panchanga](backend/app/panchanga)
- Future-BS research boundary: [backend/app/research/future_bs](backend/app/research/future_bs)
- Local kernel: [packages/parva-local-kernel](packages/parva-local-kernel)
- Public verification: [scripts/release/verify_public.py](scripts/release/verify_public.py)
- Semantic depth gate: [scripts/release/check_ceiling_depth_semantics.py](scripts/release/check_ceiling_depth_semantics.py)

## Public Verification

Run:

```bash
py -3.11 scripts/release/verify_public.py
```

Focused checks:

```bash
py -3.11 scripts/release/check_public_claims.py
py -3.11 scripts/check_path_leaks.py
py -3.11 scripts/check_future_bs_public_leakage.py
py -3.11 scripts/release/check_public_openapi_drift.py
py -3.11 scripts/release/check_ceiling_depth_semantics.py
```

Frontend:

```bash
cd frontend
npm test -- --run
npm run build
```

## Safe Claims

Safe claims when the relevant verification commands pass:

- Parva provides source-aware Nepali temporal APIs.
- Parva supports proof receipts for stable civil temporal operations.
- Parva supports method-docketed Panchanga computation with explicit non-authority boundaries.
- Parva can run local/offline verification against committed proof fixtures.
- Parva can help software agents avoid guessing Nepali dates.
- Parva can support payroll/date-risk prechecks and vendor conformance review.

## Forbidden Claims

Do not claim:

- government approval or public-office endorsement
- legal, tax, payroll, or banking decision authority
- religious or ritual final authority
- settled authority for unsupported future BS dates
- final Panchanga or ritual authority
- external certification
- PyPI/npm publication unless the package is actually published
- MCP registry acceptance unless accepted by a registry
- customers, adoption, or design partners unless real evidence exists
- unqualified Future-BS certainty or authority claims

## Project Status

The public reproducibility gate is the source of truth for release readiness:

```bash
py -3.11 scripts/release/verify_public.py
```

The civil temporal core has replay-verifiable proof support and local fixtures. Panchanga has a proof-carrying method-docketed path with fixture replay and a bounded JPL provider interface. Future-BS publishes a curated research snapshot while raw model workflows remain controlled.

The external ceiling is not complete. There are no real external witnesses, institutional signatures, official approval, third-party certification, or customer/adoption proof in this repository.

## License and Source Availability

Project Parva is licensed under `AGPL-3.0-or-later`. Network deployments must
set `PARVA_SOURCE_URL` to the corresponding source repository or source archive
for the deployed version. The application exposes `/source` as a redirect to
that configured location and adds a `rel="source"` link to HTTP responses.

Deployment details are documented in [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md).

## Roadmap

Near-term:

- broaden local-kernel replay beyond current fixtures
- expand Panchanga proof fixtures and provider coverage
- deepen proof-pack and Timepack CLI workflows
- harden payroll/date-risk audit reports for external review
- add more proof-aware UI surfaces
- expand benchmark and conformance cases
- collect bounded external technical review without overclaiming authority

## Contributing

Contributions should preserve Parva's core rules:

- no low-authority data may become high-authority output
- no proof verifier may only check object shape or hash presence
- proof-supported operations need replay tests and tamper tests
- public docs must not overclaim authority
- future-sensitive outputs must remain review-aware

Before opening a pull request, run:

```bash
py -3.11 -m pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20
py -3.11 scripts/release/check_public_claims.py
py -3.11 scripts/release/check_ceiling_depth_semantics.py
```

Use Python 3.11 and Node 20 for reproducible verification.
