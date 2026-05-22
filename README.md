# Project Parva

[![CI](https://github.com/dantwoashim/Project_Parva/actions/workflows/ci.yml/badge.svg)](https://github.com/dantwoashim/Project_Parva/actions/workflows/ci.yml)
[![Public verification](https://github.com/dantwoashim/Project_Parva/actions/workflows/public-verification.yml/badge.svg)](https://github.com/dantwoashim/Project_Parva/actions/workflows/public-verification.yml)
![Benchmark](public-benchmark/results/benchmark.svg)

Proof-carrying Nepali time infrastructure for Bikram Sambat APIs, Panchanga computation, payroll/date-risk validation, and deterministic software-agent verification.

Project Parva is an open-source temporal infrastructure stack for Nepali date and time systems: BS to AD conversion, AD to BS conversion, Nepali date validation, holidays, working days, fiscal years, BS month metadata, Panchanga signals, source/method provenance, proof receipts, local verification, SDKs, MCP tools, and public reproducibility gates.

It is built for developers searching for a Nepali date API or Bikram Sambat API, software teams validating payroll/fiscal/calendar risk, software agents that must not guess Nepali dates, and reviewers who need deterministic evidence instead of marketing claims.

## Start Here

- Quickstart: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- OpenAPI snapshot: [docs/api-docs/openapi.json](docs/api-docs/openapi.json)
- API versioning: [docs/API_VERSIONING_AND_DEPRECATION.md](docs/API_VERSIONING_AND_DEPRECATION.md)
- Proof mode: [docs/PROOF_MODE.md](docs/PROOF_MODE.md)
- Panchanga engine: [docs/PANCHANGA_ENGINE.md](docs/PANCHANGA_ENGINE.md)
- Agent tooling guide: [docs/AGENT_TOOLING_GUIDE.md](docs/AGENT_TOOLING_GUIDE.md)
- Safe claims: [docs/SAFE_CLAIMS.md](docs/SAFE_CLAIMS.md)
- Public benchmark: [public-benchmark/README.md](public-benchmark/README.md)
- Public conformance index: [docs/benchmarks/NEPALI_DATE_CONFORMANCE_INDEX.md](docs/benchmarks/NEPALI_DATE_CONFORMANCE_INDEX.md)
- Public failure classes: [docs/benchmarks/PUBLIC_NEPALI_DATE_FAILURE_CLASSES.md](docs/benchmarks/PUBLIC_NEPALI_DATE_FAILURE_CLASSES.md)
- External reviewer packet: [docs/external/REVIEWER_PACKET.md](docs/external/REVIEWER_PACKET.md)

Live public evaluation surfaces:

- Website: [https://prabinghimire1.com.np](https://prabinghimire1.com.np)
- API docs: [https://api.prabinghimire1.com.np/docs](https://api.prabinghimire1.com.np/docs)
- OpenAPI: [https://api.prabinghimire1.com.np/openapi.json](https://api.prabinghimire1.com.np/openapi.json)

The hosted API is a public evaluation deployment. First requests may be slower when the instance wakes up.

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

Parva computes Panchanga signals as method-backed astronomical outputs, not as official Panchanga authority.

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

## Architecture Overview

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

- Membranes and replay: [backend/app/membranes](backend/app/membranes)
- Source coverage: [backend/app/sources/coverage.py](backend/app/sources/coverage.py)
- Panchanga proof: [backend/app/panchanga](backend/app/panchanga)
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

- government authority
- legal, tax, payroll, or banking authority
- religious or ritual final authority
- official future date authority
- official Panchanga authority
- external certification
- PyPI/npm publication unless the package is actually published
- MCP registry acceptance unless accepted by a registry
- customers, adoption, or design partners unless real evidence exists
- public exact unsupported Future-BS predictions

## Project Status

Local/offline implementation is strong and improving. The civil temporal core has replay-verifiable proof support and local fixtures. Panchanga now has a proof-carrying method-docketed path with fixture replay and a JPL provider interface.

The external ceiling is not complete. There are no real external witnesses, institutional signatures, official approval, third-party certification, or customer/adoption proof in this repository.

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
