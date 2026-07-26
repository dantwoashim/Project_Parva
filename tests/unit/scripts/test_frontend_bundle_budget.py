from __future__ import annotations

import gzip
import json
from pathlib import Path

from scripts.release.check_frontend_bundle_budget import (
    _collect_assets,
    _evaluate,
    _summarize_assets,
    _write_report,
)


def test_collect_and_summarize_assets(tmp_path: Path):
    assets_dir = tmp_path / "assets"
    assets_dir.mkdir()
    (assets_dir / "main-abc.js").write_text("a" * 120, encoding="utf-8")
    (assets_dir / "vendor-def.js").write_text("b" * 80, encoding="utf-8")
    (assets_dir / "main-ghi.css").write_text("c" * 45, encoding="utf-8")

    assets = _collect_assets(assets_dir)
    summary = _summarize_assets(assets)

    assert [asset["path"] for asset in assets] == [
        f"{assets_dir.name}/main-abc.js",
        f"{assets_dir.name}/main-ghi.css",
        f"{assets_dir.name}/vendor-def.js",
    ]
    assert summary == {
        "total_js_bytes": 200,
        "max_js_bytes": 120,
        "total_js_gzip_bytes": len(gzip.compress(b"a" * 120, mtime=0))
        + len(gzip.compress(b"b" * 80, mtime=0)),
        "max_js_gzip_bytes": max(
            len(gzip.compress(b"a" * 120, mtime=0)),
            len(gzip.compress(b"b" * 80, mtime=0)),
        ),
        "total_css_bytes": 45,
        "max_css_bytes": 45,
        "total_css_gzip_bytes": len(gzip.compress(b"c" * 45, mtime=0)),
        "max_css_gzip_bytes": len(gzip.compress(b"c" * 45, mtime=0)),
    }


def test_evaluate_flags_budget_overages():
    summary = {
        "total_js_bytes": 510,
        "max_js_bytes": 320,
        "total_js_gzip_bytes": 210,
        "max_js_gzip_bytes": 120,
        "total_css_bytes": 90,
        "max_css_bytes": 41,
        "total_css_gzip_bytes": 35,
        "max_css_gzip_bytes": 22,
    }
    budgets = {
        "total_js_bytes": 500,
        "max_js_bytes": 300,
        "total_js_gzip_bytes": 200,
        "max_js_gzip_bytes": 125,
        "total_css_bytes": 100,
        "max_css_bytes": 40,
        "total_css_gzip_bytes": 40,
        "max_css_gzip_bytes": 25,
    }

    violations = _evaluate(summary, budgets)

    assert "total_js_bytes exceeded budget: 510 > 500" in violations
    assert "max_js_bytes exceeded budget: 320 > 300" in violations
    assert "total_js_gzip_bytes exceeded budget: 210 > 200" in violations
    assert "max_css_bytes exceeded budget: 41 > 40" in violations
    assert all("total_css_bytes" not in violation for violation in violations)


def test_write_report_persists_json(tmp_path: Path):
    report_path = tmp_path / "bundle.json"
    budgets = {
        "total_js_bytes": 10,
        "max_js_bytes": 10,
        "total_js_gzip_bytes": 10,
        "max_js_gzip_bytes": 10,
        "total_css_bytes": 5,
        "max_css_bytes": 5,
        "total_css_gzip_bytes": 5,
        "max_css_gzip_bytes": 5,
    }
    summary = {
        "total_js_bytes": 8,
        "max_js_bytes": 8,
        "total_js_gzip_bytes": 8,
        "max_js_gzip_bytes": 8,
        "total_css_bytes": 4,
        "max_css_bytes": 4,
        "total_css_gzip_bytes": 4,
        "max_css_gzip_bytes": 4,
    }
    assets = [
        {
            "path": "frontend/dist/assets/main.js",
            "kind": "js",
            "bytes": 8,
            "gzip_bytes": 8,
        }
    ]

    _write_report(report_path, budgets=budgets, summary=summary, assets=assets, violations=[])

    payload = json.loads(report_path.read_text(encoding="utf-8"))
    assert payload["status"] == "passed"
    assert payload["budgets"] == budgets
    assert payload["summary"] == summary
    assert payload["assets"] == assets
