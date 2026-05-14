# Deletions And Archives

Generated artifact for Phase 03 canonical runtime consolidation.

## Safe Archives Performed

| Candidate | Evidence | Action |
| --- | --- | --- |
| Public plugin validation inputs in `tests/fixtures/plugins` | Public engine route used these files for quality metrics. | Archived runtime copies into `data/validation/public/plugins` and updated the route to read the public validation copy. |
| Public boundary suite inputs in `tests/fixtures` | Reliability runtime used these files for public boundary metrics. | Archived runtime copies into `data/validation/public/calendar` and updated reliability code plus public artifact metadata. |
| Duplicate tithi file implementation | Python import check showed `app.calendar.tithi` resolves to `backend/app/calendar/tithi/__init__.py`. | Replaced `backend/app/calendar/tithi.py` with a compatibility stub that re-exports the package. |

## No Code Deletions Performed

No public code file was deleted in Phase 03. This follows the phase rule not to
delete compatibility paths before migration tests and public verification prove
the replacement. The old tithi implementation was removed from the file, but the
path remains as a stub.

## Deferred Candidates

| Candidate | Reason deferred |
| --- | --- |
| `backend/app/calendar/calculator.py` | Still used by compatibility facade and `calculator_v2`. |
| `backend/app/calendar/calculator_v2.py` | Still used behind `app.rules.service` and selected observance plugins. |
| `backend/app/calendar/festival_rules.json` | Catalog migration still needs equivalence checks. |
| `backend/app/calendar/festival_rules_v3.json` | Catalog migration still needs equivalence checks. |
| `sdk/python` | Compatibility smoke path still exists in public verification. |

## Verification

`python scripts/check_canonical_runtime.py` passed after these archive and stub
changes.
