---
status: public-beta
tier: 1
lane: core
last_verified: 2026-05-14
owner: platform-team
---

# Enterprise Validation Runner

Run a CSV of known conversion cases against a local or hosted Parva API.

```bash
python scripts/parva_validate.py \
  --input docs/enterprise/external_validation_cases.csv \
  --base-url http://localhost:8000 \
  --out-dir validation_reports/external
```

Outputs:

- `summary.json`
- `results.csv`
- `report.md`

CSV columns:

```csv
id,type,input,expected,category,notes
```

Supported `type` values:

- `ad_to_bs`
- `bs_to_ad`

Expected value rules:

- blank `expected`: generated reference case
- `ERROR`: case passes only if conversion fails
- any date value: exact match required

This runner is for technical evaluation and regression comparison, not final production certification.
