# Verification Dossier 2027

## Scope
This dossier consolidates Year-1 verification artifacts from engine migration through Nepal Gold hardening.

## Artifacts

- Evaluation outputs:
  - `reports/evaluation_v4/evaluation_v4.json`
  - `reports/evaluation_v4/evaluation_v4.csv`
  - `reports/evaluation_v4/evaluation_v4.md`
- Scorecard history:
  - `reports/evaluation_history.jsonl`
  - `reports/evaluation_scorecard.md`
- Mismatch triage:
  - `data/ground_truth/discrepancies.json`
  - `docs/DISCREPANCY_TRIAGE.md`
- OCR/source quality:
  - `docs/OCR_QUALITY_REPORT.md`
  - `docs/SOURCE_COMPARISON.md`

## Current Accuracy Snapshot

From latest `evaluation_v4.json`:
- Total cases: 40
- Passed: 40
- Failed: 0
- Pass rate: 100%

## Mismatch Register Status

- Open discrepancies: 0
- Classified causes: all current rows marked as `match`

## Contract Integrity

- v2 contract tests pass:
  - `tests/contract/test_v2_routing_contract.py`
- Explain endpoint integration tests pass:
  - `tests/integration/test_festival_explain.py`

## Provenance Integrity

- Snapshot creation and verification available via:
  - `POST /v2/api/provenance/snapshot/create`
  - `GET /v2/api/provenance/snapshot/{snapshot_id}/verify`
- Inclusion proof endpoint:
  - `GET /v2/api/provenance/proof?festival={id}&year={year}&snapshot={snapshot_id}`

## Pending/Forward Items

- Expand official overlap years as additional verified government calendars become available.
- Continue monthly rerun and scorecard publication through Year 2.
