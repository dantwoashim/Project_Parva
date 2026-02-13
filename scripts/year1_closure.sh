#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

OUT_DIR="reports/year1_closure"
mkdir -p "$OUT_DIR"

TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
SUMMARY="$OUT_DIR/summary.md"

run_and_capture() {
  local label="$1"
  local cmd="$2"
  local log="$3"
  echo "[RUN] $label"
  bash -lc "$cmd" > "$log" 2>&1
  echo "[OK ] $label"
}

run_and_capture "pytest" "python3 -m pytest -q" "$OUT_DIR/pytest.log"
run_and_capture "v2 e2e smoke" "PYTHONPATH=backend python3 backend/tools/e2e_v2_smoke.py" "$OUT_DIR/e2e_smoke.log"
run_and_capture "load test" "PYTHONPATH=backend python3 backend/tools/load_test_inprocess.py" "$OUT_DIR/load_test.log"
run_and_capture "benchmark" "./benchmark/run_benchmark.sh" "$OUT_DIR/benchmark.log"
run_and_capture "frontend build" "cd frontend && npm run build" "$OUT_DIR/frontend_build.log"

python3 - <<'PY' > "$OUT_DIR/metrics.json"
import json
from pathlib import Path

root = Path('.')
ev = json.loads((root / 'reports' / 'evaluation_v4' / 'evaluation_v4.json').read_text())
summary = ev.get('summary', {})
out = {
  'evaluation_total': summary.get('total'),
  'evaluation_passed': summary.get('passed'),
  'evaluation_failed': summary.get('failed'),
  'evaluation_pass_rate': summary.get('pass_rate'),
}
print(json.dumps(out, indent=2))
PY

cat > "$SUMMARY" <<'MD'
# Year 1 Closure Summary

- Generated (UTC):
  - __TS__

## Validation Checklist

- ✅ `python3 -m pytest -q`
- ✅ `PYTHONPATH=backend python3 backend/tools/e2e_v2_smoke.py`
- ✅ `PYTHONPATH=backend python3 backend/tools/load_test_inprocess.py`
- ✅ `./benchmark/run_benchmark.sh`
- ✅ `cd frontend && npm run build`

## Metrics

```json
__METRICS__
```

## Logs

- `reports/year1_closure/pytest.log`
- `reports/year1_closure/e2e_smoke.log`
- `reports/year1_closure/load_test.log`
- `reports/year1_closure/benchmark.log`
- `reports/year1_closure/frontend_build.log`
MD

python3 - <<PY
from pathlib import Path
summary = Path("$SUMMARY")
metrics = Path("$OUT_DIR/metrics.json").read_text(encoding="utf-8").strip()
text = summary.read_text(encoding="utf-8")
text = text.replace("__TS__", "$TS")
text = text.replace("__METRICS__", metrics)
summary.write_text(text, encoding="utf-8")
PY

echo "Wrote $SUMMARY"
