# Secret And Sensitive Audit

This audit combines:

- a regex-based scan of tracked source files
- targeted review of deployment config, docs, tests, and example files
- manual review of archive-style data directories that can contain third-party embedded tokens

## Summary

- No confirmed first-party production secrets were found in tracked source, docs, CI config, or examples.
- `render.yaml` keeps sensitive values operator-supplied with `sync: false`.
- `.env.example` contains placeholders only.
- The main public-repo risk is not a Parva credential leak. It is raw third-party archived HTML under `data/source_archive/secondary/`, which contains embedded page-level tokens and copied site markup from external sources.

## Findings

| Path or area | Finding type | Status | Action taken | Notes |
| --- | --- | --- | --- | --- |
| `render.yaml` | Deployment config review | Clean | Kept public | Admin token and API keys are not hard-coded |
| `.env.example` | Example config review | Clean | Added safe placeholders | No live credentials included |
| `scripts/telegram/bot_poc.py` | Environment-driven token use | Clean | Kept public | Uses `TELEGRAM_BOT_TOKEN` from env only |
| `tests/` and `backend/app/bootstrap/settings.py` | Test/demo credentials | Acceptable | Kept | Uses obvious non-production placeholder values |
| `data/source_archive/secondary/` | Third-party embedded page tokens and copied HTML | Sensitive public material | Documented as migration candidate | Not a confirmed Parva secret leak, but not a good long-term public-repo fit |
| `scripts/release/generate_partner_api_key.py` | Secret-generation utility | Clean | Kept | Generates credentials at runtime; does not embed one |

## Automation added

- `scripts/security/scan_repo_secrets.py`
- CI secret scan step in `.github/workflows/ci.yml`

## Rotation or history rewrite

- No confirmed first-party secret rotation was triggered by this audit.
- No confirmed git history rewrite is required for Parva-owned credentials based on the tracked files reviewed here.
- The raw archived third-party HTML should still be considered for migration or scrubbing before heavier public promotion.
