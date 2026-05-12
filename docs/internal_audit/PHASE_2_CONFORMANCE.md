# Phase 2 Conformance Audit

## Phase Goal

Phase 2 adds a public-safe conformance suite that lets Project Parva behavior be checked without depending on the hosted API. The suite covers stable conversion behavior, round trips, invalid BS date handling, fiscal boundaries, public release manifest shape, public-safe future-risk response shape, and panchanga response shape.

The suite is intentionally not a future-BS prediction corpus. It contains historical, current, or synthetic shape cases only.

## Files Created

- `conformance/README.md`
- `conformance/conversion/bs_to_ad_cases.json`
- `conformance/conversion/ad_to_bs_cases.json`
- `conformance/conversion/round_trip_cases.json`
- `conformance/validation/invalid_bs_dates.json`
- `conformance/fiscal/fiscal_boundary_cases.json`
- `conformance/release/release_manifest_cases.json`
- `conformance/future-risk-shape/public_safe_cases.json`
- `conformance/panchanga-shape/public_safe_shape_cases.json`
- `tools/conformance_runner/README.md`
- `tools/conformance_runner/run.py`
- `tests/conformance/test_conformance_runner.py`

## Files Modified

- `docs/future_bs/ACCURACY.md`

The accuracy policy document was rewritten to remove unsafe overclaim wording found during the required repository search. It now states that future-BS research is for validation and risk detection, not official publication authority.

## Runner Behavior

`tools/conformance_runner/run.py`:

- Loads all required conformance JSON files.
- Validates root file shape and per-case required fields.
- Runs local backend checks for conversion, round trip, invalid-date, fiscal, and panchanga shape cases.
- Validates future-risk cases as shape-only cases with `publication_status` set to `computed_prediction_not_official`.
- Rejects sensitive future value fields in public-safe shape cases.
- Supports optional API mode with `--api` when `PARVA_CONFORMANCE_BASE_URL` is set.
- Prints a readable pass/fail summary.
- Exits nonzero on malformed or failing cases.

## Quality Checks Performed

- Verified every required conformance file exists and is non-empty.
- Verified every JSON case file parses.
- Verified the runner passes the committed suite.
- Verified the runner fails on a malformed copied case with a missing required key.
- Verified the focused runner tests pass.
- Verified full backend tests pass.
- Verified frontend production build passes.
- Re-read the phase specification after implementation and before final verification.
- Removed generated Python cache files from the working tree.

## Commands Run

| Command | Result |
|---|---|
| `python tools/conformance_runner/run.py` | Passed, 27 of 27 cases |
| `python -m json.tool conformance/conversion/bs_to_ad_cases.json` | Passed |
| all conformance JSON parse loop | Passed |
| malformed copied conformance case check | Failed as expected with exit 1 |
| `PYTHONPATH=backend python -m pytest tests/conformance/test_conformance_runner.py -q` | Passed, 2 tests |
| `PYTHONPATH=backend python -m pytest -q` | Passed, 657 passed and 7 skipped |
| `npm --prefix frontend run build` | Passed |

## Repo-Wide Searches

The required repository searches were run for:

- stale legacy deployment URL patterns
- prohibited client-name and overclaim patterns
- public-sensitive future-value patterns in the new conformance suite
- em dash characters in new or edited conformance files

Findings:

- No unsafe matches were introduced in the conformance suite.
- Existing archived deployment notes and a legacy build blueprint still contain historical deployment references. They were classified as existing stale deployment references, not Phase 2 additions.
- Existing public-safety tests still contain prohibited phrases as guardrail test inputs. They were classified as harmless test fixtures.
- Local phase prompt files contain instruction text and are untracked. They were not staged for commit.

## Public Safety Status

Pass.

- No private future month-length vectors were added.
- No corrected future month values were added.
- No client-specific data was added.
- No broad future accuracy claim was added.
- Future-risk cases test shape only.
- All future-risk shape cases use `computed_prediction_not_official`.
- Public conformance examples use historical, current, or synthetic inputs.

## Known Gaps

- Optional API mode was implemented but not exercised against a running backend service in this phase. The required local conformance runner path was exercised.
- The conformance suite is a compatibility surface, not a complete statistical validation corpus.
- Existing archived deployment docs still contain old deployment references. They were not changed because Phase 2 scope is the conformance suite, and the references are not used by the new suite.

## Next Recommended Phase

- Add SDK conformance adapters that consume the same JSON cases.
- Add CI wiring so the conformance runner executes on pull requests.
- Add public OpenAPI shape checks once the public and private schema split is finalized.
