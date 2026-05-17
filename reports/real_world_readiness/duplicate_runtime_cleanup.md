# Duplicate Runtime Cleanup

Status: compatibility-only legacy paths are retained where existing imports still
need them, while canonical runtime checks guard the active path.

Tracked duplicate concerns:

- `calculator.py` / `calculator_v2.py`: canonical runtime policy identifies the
  supported calculation path; legacy usage remains compatibility-only until the
  next removal window.
- `tithi.py` / `tithi/`: package path is treated as canonical for new imports;
  legacy direct usage must remain warning-backed where retained.
- `festival_rules.json` / `festival_rules_v3.json`: newer rule data is the
  canonical source; older data should be treated as compatibility mirror only.

Verification:

```bash
py -3.11 scripts/check_canonical_runtime.py
py -3.11 -m pytest tests/runtime -q
```

Boundary: this report documents runtime hygiene only. It does not make official
calendar, legal, banking, payroll, tax, religious, or future-date authority
claims.

