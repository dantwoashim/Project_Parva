# Engine Layer

`backend/app/engine/` is the pure computation boundary for Project Parva.

Rules:
- No HTTP/FastAPI imports.
- No file I/O side effects in calculators.
- All date-time math is UTC-aware internally.
- Public return types must use models in `types.py`.

This layer wraps the existing calendar implementation while giving us a stable interface for future engine plugins.
