#!/usr/bin/env python3
"""Build a GitHub Pages static site for Parva public artifacts."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SITE_DIR = PROJECT_ROOT / "output" / "deploy" / "site"
PRECOMPUTED_DIR = PROJECT_ROOT / "output" / "precomputed"
REPORTS_DIR = PROJECT_ROOT / "reports"
DOCS_PUBLIC_BETA = PROJECT_ROOT / "docs" / "public_beta"
CONTRACTS_DIR = PROJECT_ROOT / "docs" / "contracts"


def _copy_if_exists(src: Path, dst: Path) -> bool:
    if not src.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _list_files(directory: Path, pattern: str = "*.json") -> List[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob(pattern))


def _write_json(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _render_index(payload: Dict) -> str:
    precomputed_links = "\n".join(
        f'<li><a href="precomputed/{item["name"]}">{item["name"]}</a> ({item["size_bytes"]} bytes)</li>'
        for item in payload.get("precomputed", [])
    ) or "<li>No precomputed artifacts found.</li>"

    report_links = "\n".join(
        f'<li><a href="{item["href"]}">{item["label"]}</a></li>'
        for item in payload.get("reports", [])
    ) or "<li>No report artifacts found.</li>"

    contract_links = "\n".join(
        f'<li><a href="contracts/{name}">{name}</a></li>'
        for name in payload.get("contracts", [])
    ) or "<li>No OpenAPI snapshots found.</li>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Parva Public Artifacts</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 2rem; background: #f9f7f2; color: #232323; }}
    main {{ max-width: 980px; margin: 0 auto; }}
    .card {{ background: #fff; border: 1px solid #e5dfd4; border-radius: 12px; padding: 1rem 1.25rem; margin-bottom: 1rem; }}
    h1 {{ margin-top: 0; }}
    code {{ background: #f1eee8; padding: 0.12rem 0.35rem; border-radius: 4px; }}
    ul {{ line-height: 1.8; }}
  </style>
</head>
<body>
<main>
  <h1>Project Parva — Public Artifacts</h1>
  <p>Generated at <code>{payload.get("generated_at")}</code></p>

  <div class="card">
    <h2>Precomputed Static Data</h2>
    <ul>{precomputed_links}</ul>
  </div>

  <div class="card">
    <h2>Authority Reports</h2>
    <ul>{report_links}</ul>
  </div>

  <div class="card">
    <h2>OpenAPI Contract Snapshots</h2>
    <ul>{contract_links}</ul>
  </div>

  <div class="card">
    <h2>API Endpoint Exposure</h2>
    <p>When API is deployed, key endpoints:</p>
    <ul>
      <li><code>/v5/api/public/artifacts/manifest</code></li>
      <li><code>/v5/api/public/artifacts/precomputed/{{filename}}</code></li>
      <li><code>/v5/api/public/artifacts/dashboard</code></li>
    </ul>
  </div>
</main>
</body>
</html>
"""


def main() -> int:
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True, exist_ok=True)

    precomputed_rows = []
    for src in _list_files(PRECOMPUTED_DIR):
        dst = SITE_DIR / "precomputed" / src.name
        _copy_if_exists(src, dst)
        precomputed_rows.append({"name": src.name, "size_bytes": src.stat().st_size})

    reports = []
    report_map = [
        ("authority_dashboard.json", REPORTS_DIR / "authority_dashboard.json"),
        ("conformance_report.json", REPORTS_DIR / "conformance_report.json"),
        ("rule_ingestion_summary.json", REPORTS_DIR / "rule_ingestion_summary.json"),
        ("authority_dashboard.md", DOCS_PUBLIC_BETA / "authority_dashboard.md"),
    ]
    for label, src in report_map:
        if _copy_if_exists(src, SITE_DIR / "reports" / src.name):
            reports.append({"label": label, "href": f"reports/{src.name}"})

    contracts = []
    for src in _list_files(CONTRACTS_DIR):
        if _copy_if_exists(src, SITE_DIR / "contracts" / src.name):
            contracts.append(src.name)

    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "precomputed": precomputed_rows,
        "reports": reports,
        "contracts": contracts,
    }
    _write_json(SITE_DIR / "manifest.json", manifest)
    (SITE_DIR / "index.html").write_text(_render_index(manifest), encoding="utf-8")
    (SITE_DIR / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Built static site at {SITE_DIR}")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
