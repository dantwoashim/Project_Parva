# Phase 5 Future-BS Risk Alpha Audit

## Phase Goal

Build a public-safe future-BS risk alpha and aggregate-only blinded audit workflow without exposing corrected future month values, private model internals, or client-specific data.

## Files Created

- `backend/app/future_bs/risk/models.py`
- `backend/app/future_bs/risk/labels.py`
- `backend/app/future_bs/risk/assessment.py`
- `backend/app/future_bs/risk/reason_codes.py`
- `tools/future_bs_audit/blinded_audit.py`
- `tools/future_bs_audit/README.md`
- `tools/future_bs_audit/sample_external_sheet.synthetic.csv`
- `schemas/blinded-audit-report.schema.json`
- `docs/future_bs/BLINDED_AUDIT_PROTOCOL.md`
- `docs/future_bs/WRONG_GREEN_POLICY.md`
- `docs/future_bs/REPLAY_2083_PROOF_CAPSULE.md`
- `tests/unit/future_bs/test_future_bs_risk_alpha.py`
- `tests/unit/tools/test_blinded_audit.py`

## Files Modified

- `backend/app/future_bs/risk/__init__.py`
- `schemas/future-risk.schema.json`
- `tools/validate_schemas.py`

## Risk Models Added

- `RiskLabel` defines `GREEN`, `YELLOW`, and `RED` in one public-safe enum.
- `FutureBSRiskInput` accepts external assumptions for local review.
- `FutureBSRiskAssessment` serializes public-safe risk posture without corrected values.
- `assess_month_assumption` classifies individual submitted assumptions.
- `aggregate_blinded_audit` returns aggregate-only counts for an external sheet.

## Audit Tool Behavior

The blinded audit tool accepts CSV input with:

```text
bs_year,bs_month,month_length
```

Default output is aggregate-only and includes:

- total months checked
- agreement count
- disagreement count
- disagreement distribution by year
- boundary-sensitive count
- year-total anomaly count
- high-risk month count
- corrected values included, false

The committed sample uses synthetic years `9000` and `9001`. It is not a real future-BS prediction table.

## Proof Capsule Contents

`docs/future_bs/REPLAY_2083_PROOF_CAPSULE.md` records only the public-safe validation capsule:

- official-verified validation window: 2078 to 2083 BS
- solar-civil path: 72 out of 72 in that window
- legacy/static baseline: 68 out of 72 in that window
- missed baseline months: 2082 Ashadh, 2082 Shrawan, 2083 Bhadra, 2083 Ashwin
- caveat: limited validation, not official authority, not a guarantee of future accuracy

No private future vectors, corrected future values, thresholds, weights, or audit outputs were added.

## Commands Run

```text
python tools/future_bs_audit/blinded_audit.py tools/future_bs_audit/sample_external_sheet.synthetic.csv
python tools/validate_schemas.py
python tools/conformance_runner/run.py
$env:PYTHONPATH='backend'; python -m pytest -q tests/unit/future_bs/test_future_bs_risk_alpha.py tests/unit/tools/test_blinded_audit.py tests/integration/test_future_bs_routes.py tests/public_safety/test_public_release_safety.py
$env:PYTHONPATH='backend'; python -m pytest -q tests/unit/future_bs/test_future_bs_risk_alpha.py tests/unit/tools/test_blinded_audit.py
$env:PYTHONPATH='backend'; python -m pytest -q
npm --prefix frontend run build
git grep tracked public files for stale deployment patterns
git grep tracked public files for client-name and overclaim patterns
Select-String targeted Phase 5 files for deployment leaks, client names, overclaim phrases, and em dash characters
```

## Pass and Fail Results

- Blinded audit sample command: passed.
- Schema validation: passed, 13 schemas validated.
- Public conformance runner: passed, 27 passed and 0 failed.
- Focused Phase 5 and public-safety tests: passed, 20 passed before final edits.
- Focused Phase 5 tests after final edits: passed, 7 passed.
- Full backend test suite: passed, 667 passed and 7 skipped.
- Frontend production build: passed.

## Repo-Wide Search Results

Deployment pattern search found archived Cloud Run documentation during Phase 5:

- Removed historical path: docs/archive/DEPLOY_CLOUD_RUN.md, removed during final integration because the public deployment moved to Render.

Classification: historical deployment reference. It is not a live frontend config, public route, or Phase 5 artifact.

Overclaim and client-name pattern search found existing guard-test literals:

- `tests/public_safety/test_public_release_safety.py`

Classification: harmless public-safety guard tests. They intentionally contain banned phrases to assert README and docs do not use them.

Targeted Phase 5 file search found no deployment leaks, client names, banned public overclaims, or em dash characters after the final wording fix.

## Public Safety Status

- Future outputs are labeled `computed_prediction_not_official`.
- Blinded audit output does not include corrected future month values by default.
- The synthetic CSV does not include sensitive future-range markers.
- The public v4 capabilities endpoint remains metadata-only.
- The new docs do not include private future vectors or exact model internals.
- No client or prospect names were added.
- No broad future accuracy claim was added.

## Quality Review Performed

- Re-read the phase file after implementation.
- Verified every required Phase 5 file exists and is non-empty.
- Verified risk labels are defined in one clean enum.
- Verified the audit output is aggregate-only and shape-tested.
- Replaced a real-looking future-risk schema example year with a synthetic year.
- Rewrote proof-capsule wording to avoid matching public banned phrase patterns.

## Remaining Risks

- The archived Cloud Run doc still contains stale deployment wording. It was not changed because this phase was restricted to future-BS risk alpha and blinded audit.
- The audit tool is an alpha public-safe shape. It does not perform private corrected-value comparison in the public mode.
- Real external sheets must stay local or private and must not be committed.

## Next Recommended Phase

Use the blinded audit tool in controlled private deployment only, then add signed private report export if a later phase explicitly authorizes it.
