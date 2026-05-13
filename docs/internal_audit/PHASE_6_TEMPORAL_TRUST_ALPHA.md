Historical snapshot. Not necessarily current verification status. Run the current verification commands before treating any pass/fail claim here as current.

# Phase 6 Temporal Trust Alpha Audit

## Phase Goal

Add the first alpha of Parva Temporal Trust Infrastructure: release signature concepts, an append-only transparency-log prototype, temporal SBOM schema, reconciliation event schema, and public trust documentation.

## Files Created

- `schemas/signature.schema.json`
- `schemas/transparency-log-entry.schema.json`
- `schemas/temporal-sbom.schema.json`
- `tools/trust/common.py`
- `tools/trust/sign_release.py`
- `tools/trust/verify_release_signature.py`
- `tools/trust/append_log_entry.py`
- `tools/trust/verify_log.py`
- `tools/trust/README.md`
- `data/public/releases/parva-bs-public-demo.signature.json`
- `data/public/transparency-log/parva-log.jsonl`
- `docs/TRUST_INFRASTRUCTURE_ALPHA.md`
- `docs/TEMPORAL_SBOM.md`
- `docs/TRANSPARENCY_LOG.md`
- `tests/unit/trust/test_temporal_trust_tools.py`

## Files Modified

- `schemas/reconciliation-event.schema.json`
- `schemas/webhooks/calendar_events.schema.json`
- `tools/validate_schemas.py`
- `docs/future_bs/RECONCILIATION_WORKFLOW.md`

## Signing or Hash Approach

The release signature artifact uses:

```text
alpha_hash_only_sha256
```

This is intentionally documented as alpha hash verification, not production-grade cryptographic signing. No new crypto dependency was added. No custom encryption scheme was invented.

The signature verifier recomputes the public release manifest hash and checks that `data/public/releases/parva-bs-public-demo.signature.json` still matches the manifest.

## Transparency Log Behavior

The alpha log is:

```text
data/public/transparency-log/parva-log.jsonl
```

It contains one tool-generated JSONL entry for `calendar.release.published`. The verifier checks row shape, supported event names, SHA-256 reference shape, signature reference existence, duplicate release artifact entries, and public-safety text patterns.

## Temporal SBOM Behavior

`schemas/temporal-sbom.schema.json` defines how a downstream system can declare calendar release dependencies by release identifier, hash, and source policy.

The included example is structural only and does not include future month values.

## Reconciliation Events

`schemas/reconciliation-event.schema.json` now defines:

- `calendar.official_release.verified`
- `calendar.release.diff_available`
- `calendar.risk_label.changed`
- `calendar.schedule.review_required`
- `calendar.future_assumption.resolved`

The reconciliation documentation uses review and approval language. It does not imply silent production database updates.

## Commands Run

```text
python tools/trust/sign_release.py --signed-at 2026-05-12T00:00:00Z
python tools/trust/append_log_entry.py --timestamp 2026-05-12T00:00:00Z
python tools/trust/verify_release_signature.py
python tools/trust/verify_log.py
python tools/release/verify_release.py data/public/releases/parva-bs-public-demo.manifest.json
python tools/validate_schemas.py
python tools/conformance_runner/run.py
$env:PYTHONPATH='backend'; python -m pytest -q tests/unit/trust/test_temporal_trust_tools.py tests/unit/release/test_verify_release.py tests/public_safety/test_public_release_safety.py
$env:PYTHONPATH='backend'; python -m pytest -q
npm --prefix frontend run build
git grep tracked public files for stale deployment patterns
git grep tracked public files for client-name and overclaim patterns
Select-String targeted Phase 6 files for deployment leaks, client names, overclaim phrases, em dash characters, and sensitive future-range markers
```

## Pass and Fail Results

- Signature generation: passed.
- Transparency log append: passed.
- Signature verification: passed.
- Transparency log verification: passed.
- Existing release verification: passed.
- Schema validation: passed, 16 schemas validated.
- Conformance runner: passed, 27 passed and 0 failed.
- Focused trust and public-safety tests: passed, 14 passed.
- Full backend suite: passed, 672 passed and 7 skipped.
- Frontend build: passed.

## Repo-Wide Search Results

Stale deployment pattern search found archived Cloud Run documentation during Phase 6:

- Removed historical path: docs/archive/DEPLOY_CLOUD_RUN.md, removed during final integration because the public deployment moved to Render.

Classification: historical deployment reference. It is not a live route, config, or Phase 6 artifact.

Overclaim and client-name pattern search found existing public-safety guard-test literals:

- `tests/public_safety/test_public_release_safety.py`

Classification: harmless guard-test literals used to verify public docs avoid those phrases.

Targeted Phase 6 file search found no deployment leaks, client names, banned public overclaims, em dash characters, or sensitive future-range values in the new docs, schemas, tools, signature artifact, or transparency log. One focused test intentionally contains forbidden-token strings as assertions.

## Public Safety Status

- No private future-BS values were added.
- No future prediction vectors were added.
- No client-specific details were added.
- No official authority claim was added.
- Trust docs state alpha limits and official publication override.
- Reconciliation copy requires review and approval before downstream application.

## Quality Review Performed

- Re-read the Phase 6 file after implementation.
- Verified every required schema, doc, tool, signature artifact, and log file exists and is non-empty.
- Verified schemas parse through the repo validator.
- Verified trust tools execute and fail through explicit `TrustToolError` paths.
- Verified the public log is valid JSONL.
- Verified no custom cryptographic scheme was introduced.
- Verified docs describe alpha limitations.
- Verified tests cover release signature verification, log append, log verification, schema validation, and public-safety markers.

## Remaining Risks

- The alpha signature is hash-only and should be replaced by managed signing for production deployments.
- The transparency log is JSONL only. It does not yet provide Merkle proofs or external anchoring.
- The trust alpha covers public demo artifacts, not private deployment release governance.

## Next Recommended Phase

Add managed key support, external transparency anchoring, and organization-specific approval workflows only after a private deployment target is defined.
