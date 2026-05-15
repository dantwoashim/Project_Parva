# Future-BS Lane Fix

## Problem

The leakage checker required
`reports/phase_07_future_bs_governance/module_classification.md`.

## Fix

Created `reports/phase_07_future_bs_governance/module_classification.md` with
classifications for Future-BS routes, backend modules, scripts, docs, SDK
surfaces, tests, and artifacts.

Classification values used include:

- `public_safe_metadata`
- `public_preview_risk`
- `research_private`
- `private_source_required`
- `wide_corpus_required`
- `generated_artifact_required`
- `experimental`
- `deprecated`

## Test Marker Decision

No meaningful assertions were removed or weakened. The current public-safe
pytest lane passes without adding broad blanket markers. Tests that use the
checked-in public official 2078-2083 holdout remain public-safe. Future-BS tests
that later begin requiring private source archives, wide corpus inputs, or
generated research artifacts should be marked with the existing pytest markers:
`private_source`, `wide_corpus`, or `research_artifact`.

## Evidence

- `python scripts/check_future_bs_public_leakage.py`: pass.
- `python -m pytest -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20`: 846 passed, 8 skipped.
- `python -m pytest tests/future_bs tests/accuracy tests/artifacts tests/performance -q -m "not private_source and not wide_corpus and not research_artifact" --maxfail=20`: 56 passed.

Public profiles still expose Future-BS metadata/capabilities only, not exact
unsupported future predictions.

