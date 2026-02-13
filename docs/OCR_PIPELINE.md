# OCR Pipeline (MoHA Holiday PDFs)

## Pipeline Stages
1. PDF -> PNG pages (`pdftoppm`, 300 DPI)
2. OCR (`tesseract -l nep+eng`)
3. Text normalization (`normalize_ocr_text`)
4. Line extraction (`extract_entries`)
5. Festival mapping (`map_entries`)
6. Duplicate resolution (`deduplicate_entries`)
7. Override merge (`merge_overrides`)

## Script
- `/Users/rohanbasnet14/Documents/Project Parva/backend/tools/ingest_moha_pdfs.py`

## Second-Pass Corrections
- Nepali month spelling normalization
- Common OCR substitutions in festival names
- Digit cleanup and mixed-script fixes
- Noise cleanup around weekday markers

## Confidence Model
Each extracted row has `parse_confidence`:
- `high`: strict parse + strong digit/month integrity
- `medium`: fuzzy parse or partial cleanup required
- `low`: weak parse or unmatched mapping

Confidence is carried into:
- `data/ingest_reports/holidays_*_parsed.csv`
- `data/ingest_reports/holidays_*_matched.csv`
- override notes (`ocr_confidence=` tag)

## Quality Tracking
- Quality script: `/Users/rohanbasnet14/Documents/Project Parva/backend/tools/ocr_quality_check.py`
- JSON summary: `data/ingest_reports/ocr_quality_summary.json`
- Markdown report: `docs/OCR_QUALITY_REPORT.md`

## Expected Failure Modes
- Low-contrast scans causing month/day confusion
- Multi-event lines where parser extracts only one event
- Regional spelling variants not yet mapped

## Mitigation
- Expand normalization dictionary incrementally
- Maintain canonical name map (`data/festival_name_map.json`)
- Re-run source normalization (`backend/tools/normalize_sources.py`) and inspect disagreements
