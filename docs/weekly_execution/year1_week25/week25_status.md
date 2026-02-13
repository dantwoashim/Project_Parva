# Year 1 Week 25 Status (OCR Pipeline Hardening)

## Completed
- Upgraded OCR ingest pipeline:
  - `/Users/rohanbasnet14/Documents/Project Parva/backend/tools/ingest_moha_pdfs.py`
- Added second-pass correction expansion (month/festival substitutions + digit cleanup).
- Added parse confidence scoring (`high|medium|low`).
- Added duplicate resolution pipeline (`deduplicate_entries`).
- Added confidence-aware override merge notes (`ocr_confidence=` tag).
- Converted ingest script defaults to workspace-relative paths (removed stale absolute paths).
- Added unit tests:
  - `/Users/rohanbasnet14/Documents/Project Parva/tests/unit/tools/test_ingest_moha_pipeline.py`

## Outcome
- OCR ingestion is now safer, more explainable, and less noisy for downstream ground-truth merges.
