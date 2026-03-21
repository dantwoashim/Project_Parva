#!/usr/bin/env python3
"""Check the built frontend asset sizes against release-candidate budgets."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = PROJECT_ROOT / "frontend" / "dist" / "assets"
DEFAULT_REPORT_PATH = PROJECT_ROOT / "reports" / "release" / "frontend_bundle_budget.json"

DEFAULT_BUDGETS = {
    "total_js_bytes": 475_000,
    "max_js_bytes": 300_000,
    "total_css_bytes": 110_000,
    "max_css_bytes": 40_000,
}


def _collect_assets(assets_dir: Path) -> list[dict[str, object]]:
    if not assets_dir.exists():
        raise FileNotFoundError(f"Built assets directory not found: {assets_dir}")

    assets = []
    for path in sorted(assets_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix not in {".js", ".css"}:
            continue
        try:
            relative_path = str(path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        except ValueError:
            relative_path = str(path.relative_to(assets_dir.parent)).replace("\\", "/")
        assets.append(
            {
                "path": relative_path,
                "kind": path.suffix.lstrip("."),
                "bytes": path.stat().st_size,
            }
        )
    return assets


def _summarize_assets(assets: list[dict[str, object]]) -> dict[str, int]:
    js_assets = [int(asset["bytes"]) for asset in assets if asset["kind"] == "js"]
    css_assets = [int(asset["bytes"]) for asset in assets if asset["kind"] == "css"]
    return {
        "total_js_bytes": sum(js_assets),
        "max_js_bytes": max(js_assets, default=0),
        "total_css_bytes": sum(css_assets),
        "max_css_bytes": max(css_assets, default=0),
    }


def _evaluate(summary: dict[str, int], budgets: dict[str, int]) -> list[str]:
    violations = []
    for key, limit in budgets.items():
        actual = summary[key]
        if actual > limit:
            violations.append(f"{key} exceeded budget: {actual} > {limit}")
    return violations


def _write_report(
    report_path: Path,
    *,
    budgets: dict[str, int],
    summary: dict[str, int],
    assets: list[dict[str, object]],
    violations: list[str],
) -> None:
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "passed" if not violations else "failed",
        "budgets": budgets,
        "summary": summary,
        "violations": violations,
        "assets": assets,
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets-dir", default=str(ASSETS_DIR))
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH))
    parser.add_argument("--total-js-bytes", type=int, default=DEFAULT_BUDGETS["total_js_bytes"])
    parser.add_argument("--max-js-bytes", type=int, default=DEFAULT_BUDGETS["max_js_bytes"])
    parser.add_argument("--total-css-bytes", type=int, default=DEFAULT_BUDGETS["total_css_bytes"])
    parser.add_argument("--max-css-bytes", type=int, default=DEFAULT_BUDGETS["max_css_bytes"])
    args = parser.parse_args(argv)

    budgets = {
        "total_js_bytes": args.total_js_bytes,
        "max_js_bytes": args.max_js_bytes,
        "total_css_bytes": args.total_css_bytes,
        "max_css_bytes": args.max_css_bytes,
    }

    try:
        assets = _collect_assets(Path(args.assets_dir))
    except FileNotFoundError as exc:
        print(f"[bundle-budget] {exc}")
        return 2

    summary = _summarize_assets(assets)
    violations = _evaluate(summary, budgets)
    report_path = Path(args.report_path)
    _write_report(report_path, budgets=budgets, summary=summary, assets=assets, violations=violations)

    print(
        json.dumps(
            {
                "report": str(report_path),
                "status": "passed" if not violations else "failed",
                "summary": summary,
            },
            indent=2,
        )
    )
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
