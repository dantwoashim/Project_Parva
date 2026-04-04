#!/usr/bin/env bash
set -euo pipefail

# Build an institutional offline bundle with reproducible artifacts.

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
VERSION="${1:-v3_offline}"
OUT_ROOT="$ROOT_DIR/output/offline"
BUNDLE_DIR="$OUT_ROOT/parva_offline_${VERSION}_${STAMP}"
ARCHIVE_PATH="$OUT_ROOT/parva_offline_${VERSION}_${STAMP}.tar.gz"

mkdir -p "$BUNDLE_DIR"
mkdir -p "$OUT_ROOT"

echo "Building offline bundle at: $BUNDLE_DIR"

# Copy core runtime + validation assets
mkdir -p "$BUNDLE_DIR/backend" "$BUNDLE_DIR/benchmark" "$BUNDLE_DIR/docs" "$BUNDLE_DIR/output"
cp -R "$ROOT_DIR/backend/app" "$BUNDLE_DIR/backend/"
cp -R "$ROOT_DIR/benchmark/packs" "$BUNDLE_DIR/benchmark/"
cp -R "$ROOT_DIR/benchmark/results" "$BUNDLE_DIR/benchmark/" || true
cp -R "$ROOT_DIR/output/precomputed" "$BUNDLE_DIR/output/" || true

cp "$ROOT_DIR/README.md" "$BUNDLE_DIR/"
cp "$ROOT_DIR/pyproject.toml" "$BUNDLE_DIR/"
cp "$ROOT_DIR/docs/INSTITUTIONAL_USAGE.md" "$BUNDLE_DIR/docs/" || true
cp "$ROOT_DIR/docs/RELIABILITY.md" "$BUNDLE_DIR/docs/" || true
cp "$ROOT_DIR/docs/POLICY.md" "$BUNDLE_DIR/docs/" || true
cp "$ROOT_DIR/docs/EXPLAINABILITY.md" "$BUNDLE_DIR/docs/" || true

# Include helper scripts
mkdir -p "$BUNDLE_DIR/scripts"
cp -R "$ROOT_DIR/scripts/precompute" "$BUNDLE_DIR/scripts/" || true
cp "$ROOT_DIR/scripts/check_differential_gate.py" "$BUNDLE_DIR/scripts/" || true
cp "$ROOT_DIR/scripts/security/run_audit.py" "$BUNDLE_DIR/scripts/" || true
cp "$ROOT_DIR/scripts/offline/verify_offline_parity.py" "$BUNDLE_DIR/scripts/" || true

# Manifest with checksums
(
  cd "$BUNDLE_DIR"
  find . -type f ! -name "MANIFEST.sha256" | sort | while read -r f; do
    shasum -a 256 "$f"
  done > MANIFEST.sha256
)

tar -czf "$ARCHIVE_PATH" -C "$OUT_ROOT" "$(basename "$BUNDLE_DIR")"
shasum -a 256 "$ARCHIVE_PATH" > "${ARCHIVE_PATH}.sha256"

cat <<EOF
Offline bundle ready:
- Directory: $BUNDLE_DIR
- Archive:   $ARCHIVE_PATH
- Checksum:  ${ARCHIVE_PATH}.sha256
EOF
