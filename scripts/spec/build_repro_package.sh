#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT_DIR="$ROOT_DIR/output/spec"
PKG_DIR="$OUT_DIR/parva_spec1_repro_${STAMP}"
ARCHIVE="$OUT_DIR/parva_spec1_repro_${STAMP}.tar.gz"

mkdir -p "$PKG_DIR" "$OUT_DIR"

mkdir -p "$PKG_DIR/docs" "$PKG_DIR/benchmark" "$PKG_DIR/reports" "$PKG_DIR/scripts" "$PKG_DIR/output"

cp "$ROOT_DIR/docs/PARVA_TEMPORAL_SPEC_1_0.md" "$PKG_DIR/docs/"
cp "$ROOT_DIR/docs/spec/PARVA_TEMPORAL_SPEC_V1.md" "$PKG_DIR/docs/" || true
cp "$ROOT_DIR/docs/PARVA_CONFORMANCE_TESTS.md" "$PKG_DIR/docs/" || true
cp "$ROOT_DIR/docs/EXPLAIN_SPEC.md" "$PKG_DIR/docs/" || true
cp "$ROOT_DIR/docs/BENCHMARK_SPEC.md" "$PKG_DIR/docs/" || true
cp "$ROOT_DIR/docs/LTS_POLICY.md" "$PKG_DIR/docs/" || true

cp -R "$ROOT_DIR/benchmark/packs" "$PKG_DIR/benchmark/"
cp -R "$ROOT_DIR/benchmark/results" "$PKG_DIR/benchmark/" || true

cp "$ROOT_DIR/reports/conformance_report.json" "$PKG_DIR/reports/" || true
cp "$ROOT_DIR/reports/offline_parity.json" "$PKG_DIR/reports/" || true
cp "$ROOT_DIR/reports/forecast_2030_2050.json" "$PKG_DIR/reports/" || true

cp "$ROOT_DIR/scripts/spec/run_conformance_tests.py" "$PKG_DIR/scripts/"
cp "$ROOT_DIR/scripts/spec/replay_trace.py" "$PKG_DIR/scripts/" || true
cp "$ROOT_DIR/tests/conformance/conformance_cases.v1.json" "$PKG_DIR/scripts/" || true
cp -R "$ROOT_DIR/docs/spec/schemas" "$PKG_DIR/docs/" || true
cp "$ROOT_DIR/scripts/offline/verify_offline_parity.py" "$PKG_DIR/scripts/" || true
cp "$ROOT_DIR/scripts/release/check_contract_freeze.py" "$PKG_DIR/scripts/" || true

cp -R "$ROOT_DIR/output/offline" "$PKG_DIR/output/" || true

(
  cd "$PKG_DIR"
  find . -type f ! -name "MANIFEST.sha256" | sort | while read -r f; do
    shasum -a 256 "$f"
  done > MANIFEST.sha256
)

tar -czf "$ARCHIVE" -C "$OUT_DIR" "$(basename "$PKG_DIR")"
shasum -a 256 "$ARCHIVE" > "${ARCHIVE}.sha256"

echo "Repro package ready:"
echo "- Directory: $PKG_DIR"
echo "- Archive:   $ARCHIVE"
echo "- Checksum:  ${ARCHIVE}.sha256"
