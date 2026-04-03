"""Benchmark reproducibility helpers."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.engine.manifest import build_engine_manifest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPORT_PATH = PROJECT_ROOT / "reports" / "evaluation_v4" / "evaluation_v4.json"
DOCS_DIR = PROJECT_ROOT / "docs"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        return {}


def _sha256_path(path: Path) -> str | None:
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sha256_json(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def get_benchmark_manifest() -> dict[str, Any]:
    report = _read_json(REPORT_PATH)
    run = report.get("run", {}) if isinstance(report.get("run"), dict) else {}
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    engine_manifest = build_engine_manifest()

    docs = {
        "support_matrix": "docs/SUPPORT_MATRIX.md",
        "accuracy_method": "docs/ACCURACY_METHOD.md",
        "known_limits": "docs/KNOWN_LIMITS.md",
        "engine_architecture": "docs/ENGINE_ARCHITECTURE.md",
    }

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "report_generated_at": report.get("generated_at") or run.get("generated_at"),
        "evaluation_track": run.get("evaluation_track", "override_assisted_practical"),
        "case_count": run.get("case_count", 0),
        "pass_rate": summary.get("pass_rate", 0.0),
        "conflict_policy": run.get("conflict_policy", "public_default_selection_with_visible_alternates"),
        "abstention_policy": run.get("abstention_policy", "strict_mode_abstains_on_high_disagreement_risk"),
        "run_filters": run.get("filters", {}),
        "run_options": run.get("options", {}),
        "source_hashes": run.get("source_hashes", {}),
        "report_hash": _sha256_path(REPORT_PATH),
        "engine_manifest_hash": _sha256_json(engine_manifest),
        "engine_manifest": {
            "canonical_engine_id": engine_manifest.get("canonical_engine_id"),
            "manifest_version": engine_manifest.get("manifest_version"),
            "public_route_families": engine_manifest.get("public_route_families", []),
        },
        "docs": {
            key: {
                "path": value,
                "sha256": _sha256_path(PROJECT_ROOT / value),
            }
            for key, value in docs.items()
        },
        "known_limits": [
            "Regional/tradition variants remain profile-based rather than universal doctrinal truth.",
            "Boundary-sensitive observances can still show one-day disagreement near sunrise and lunar transitions.",
            "Strict risk mode may abstain when authority disagreement is too sharp to flatten safely.",
            "Benchmark reports are strongest for source-supported festival subsets, not every personal or ritual surface.",
        ],
    }


__all__ = ["get_benchmark_manifest"]
