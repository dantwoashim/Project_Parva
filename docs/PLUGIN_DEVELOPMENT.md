# Plugin Development Guide

## Calendar Plugin Contract
Implement methods in `backend/app/engine/plugins/base.py`:
- `metadata()`
- `convert_from_gregorian(date)`
- `convert_to_gregorian(year, month, day)`
- `month_lengths(year)`
- `validate(year, month, day)`

## Steps to Add a Plugin
1. Copy `backend/app/engine/plugins/_template/`.
2. Implement conversion and validation logic.
3. Add fixture cases in `tests/fixtures/plugins/plugin_validation_cases.json`.
4. Register plugin in `backend/app/engine/plugins/registry.py`.
5. Run validation:
   - `PYTHONPATH=backend python3 backend/tools/validate_plugins.py`

## Acceptance
- Plugin must pass validation suite.
- Plugin metadata must include confidence notes and reverse conversion capability.
