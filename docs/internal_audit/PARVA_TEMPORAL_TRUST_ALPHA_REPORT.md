Historical snapshot. Not necessarily current verification status. Run the current verification commands before treating any pass/fail claim here as current.

# Parva Temporal Trust Alpha Report

Date: 2026-05-13

## Layer 5 Status

Layer 5 is complete for the public alpha scope.

Project Parva now has a public-safe temporal trust foundation for source registry inspection, release manifest inspection, trust log verification, release diffing, evidence packets, release-id metadata, API trust routes, SDK trust helpers, and fresh-clone public verification.

This layer does not claim legal authority, government publication authority, broad future-calendar certainty, or production-grade signing. Public future-BS research remains labeled `computed_prediction_not_official`.

## Source Registry

The public source registry at `data/public/releases/parva-bs-public-demo.sources.json` was strengthened with Layer 5 source tiers:

- `official`
- `semi_official`
- `public_corpus`
- `publisher`
- `calculated`
- `fixture`
- `research`
- `private`
- `unknown`

The current public registry contains 11 public-safe sources. Public corpus, calculated, publisher, official-overlap, and research records are kept separate. Weak or research sources are not promoted into official authority.

## Release Manifest And Trust Log

The public release manifest at `data/public/releases/parva-bs-public-demo.manifest.json` now includes:

- release id
- release type
- status
- source policy
- artifact hashes
- capabilities
- default confidence
- claim boundary
- warnings

The alpha signature file was regenerated at `data/public/releases/parva-bs-public-demo.signature.json` using the existing hash-only public-preview signing path. This is intentionally `unsigned_public_preview` style trust infrastructure, not a production signature.

The trust log at `data/public/trust/parva-trust-log.jsonl` records the public release event with a stable SHA-256 entry hash and artifact checksums. The existing transparency log at `data/public/transparency-log/parva-log.jsonl` also verifies.

## Evidence Packets

Evidence packet generation now works for:

- date conversion
- compliance decision evidence

Packets include:

- packet id
- packet type
- generated timestamp
- input
- result
- release id
- source records
- confidence
- claim boundary
- warnings
- trace id
- packet hash
- signature status

Evidence packets wrap existing service logic rather than duplicating calendar conversion or compliance logic.

## Release Diff And Version Pinning

Release diff works at the manifest, source, artifact, and capability metadata level.

Version pinning behavior is explicit:

- missing release id uses the active public release
- valid release id works through query, body, or header where applicable
- unknown release id returns a clear 404-style trust error
- response metadata includes the active release id

Only one public release currently exists, so semantic release-to-release calendar impact is not claimed.

## API Endpoints

Public-safe trust endpoints are available under `/v3/api/trust/*`:

- `GET /v3/api/trust/capabilities`
- `GET /v3/api/trust/sources`
- `GET /v3/api/trust/sources/{source_id}`
- `GET /v3/api/trust/releases`
- `GET /v3/api/trust/releases/{release_id}`
- `GET /v3/api/trust/releases/{from_release}/diff/{to_release}`
- `GET /v3/api/trust/log`
- `POST /v3/api/trust/evidence/date-conversion`
- `POST /v3/api/trust/evidence/compliance-decision`

The public route inventory verifies 169 canonical v3 routes.

## SDKs

JavaScript and Python SDKs now expose trust helpers for:

- list sources
- get source
- list releases
- get release
- diff releases
- get trust log
- create date conversion evidence
- create compliance decision evidence

SDK tests verify these helpers preserve release, source, confidence, warning, trace, and packet integrity fields.

## Documentation And OpenAPI

Layer 5 added or updated:

- `docs/TRUST_INFRASTRUCTURE.md`
- `docs/SOURCE_REGISTRY.md`
- `docs/RELEASES.md`
- `docs/EVIDENCE_PACKETS.md`
- `docs/API_TRUST.md`
- `docs/API_QUICKSTART.md`
- `docs/API_REFERENCE_V3.md`
- `docs/PUBLIC_API_BOUNDARY.md`
- `docs/ROUTE_ACCESS.md`
- `docs/api-docs/openapi.json`

The static public OpenAPI artifact was regenerated from the public demo route profile and contains 30 public-safe paths. It includes the source-aware metadata schema required by the public contract tests.

## Commands Run

| Command | Result |
|---|---:|
| `py -3.11 -m pytest tests\contract\test_layer5_trust_contract.py -q` | Pass, 12 tests |
| `py -3.11 scripts\parva_trust_verify.py` | Pass |
| `py -3.11 scripts\parva_release_diff.py --from parva-bs-public-demo --to parva-bs-public-demo` | Pass |
| `py -3.11 scripts\parva_evidence_packet.py --type date_conversion --ad-date 2026-04-14` | Pass |
| `py -3.11 -m ruff check backend\app\api\trust_routes.py backend\app\services\trust_infrastructure_service.py scripts\parva_trust_verify.py scripts\parva_release_diff.py scripts\parva_evidence_packet.py packages\parva-python\parva\__init__.py packages\parva-python\parva\client.py tests\contract\test_layer5_trust_contract.py` | Pass |
| `py -3.11 scripts\release\generate_public_demo_openapi.py` | Pass, 30 paths |
| `py -3.11 -m json.tool docs\api-docs\openapi.json` | Pass |
| `py -3.11 scripts\release\check_documented_routes.py` | Pass, 169 canonical v3 routes |
| `py -3.11 -m pytest tests\contract\test_layer3_source_metadata_contract.py::test_static_openapi_docs_include_source_aware_metadata_schema -q` | Pass |
| `py -3.11 -m pytest tests\contract\test_layer5_trust_contract.py tests\contract\test_layer4_compliance_contract.py tests\contract\test_layer3_source_metadata_contract.py tests\contract\test_layer2_public_api_contract.py -q` | Pass, 33 tests |
| `npm --prefix packages/parva-js test` | Pass, 8 tests |
| `py -3.11 -m pytest packages\parva-python\tests -q` | Pass, 9 tests |
| `py -3.11 scripts\check_docs_links.py` | Pass |
| public-safety prohibited phrase grep across README, docs, backend, packages, frontend, and tests | Pass, no matches |
| `rg -n "project-parva-api\|run\.app\|asia-south1" frontend README.md docs backend packages .env.example` | Pass, no matches |
| em dash grep across checked public docs, frontend, and SDK README files | Pass, no matches |
| `py -3.11 scripts\release\verify_public.py` | Pass |
| `git diff --check` | Pass with line-ending warnings only |

The public reproducibility gate reported:

- backend tests: 706 passed, 8 skipped
- Python SDK tests: 9 passed
- frontend tests: 112 passed
- JavaScript SDK tests: 8 passed
- frontend lint: pass
- frontend build: pass
- backend lint: pass
- secret scan: pass
- path leak scan: pass
- documentation links: pass
- trust verification: pass

## Public Safety Checks

Verified:

- no prohibited client or prospect names in checked public scope
- no old Cloud Run host references in checked public scope
- no em dashes in checked public README, docs, frontend, or SDK README files
- public trust verification does not require private archives
- trust packets do not use production signatures
- private future-BS prediction and export surfaces remain gated outside the public trust surface

## Remaining Risks

- The alpha signature is hash-only preview infrastructure. A production signing key backend is still a future operational task.
- Only one public release currently exists, so release diff is metadata-level and same-release diff has no changed artifacts.
- Evidence packets are public-safe explanations, not legal certificates.
- Public verification passes locally on this Windows environment. CI should run `py -3.11 scripts\release\verify_public.py` or equivalent on every release.

## Recommended Layer 6 Start

Layer 6 should start with production-grade release signing policy, CI enforcement for trust artifact drift, and private-source extension hooks that do not affect public reproducibility.
