---
status: public-beta
audience: maintainer
---

# SDK Publishing Checklist

Do not publish packages from an automation session unless credentials,
maintainer approval, and release identity are explicitly configured.

Before publishing:

- `python -m pytest packages/parva-python/tests -q`
- `python -m build packages/parva-python`
- `npm --prefix packages/parva-js test`
- `npm --prefix packages/parva-js pack`
- `python scripts/check_future_bs_public_leakage.py`
- review package descriptions for authority overclaims,
- verify SDK defaults use `/v3/api`,
- verify Future-BS support is capabilities-only,
- update release notes and version tags.
