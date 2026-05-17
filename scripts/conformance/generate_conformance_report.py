#!/usr/bin/env python3
"""Generate a conformance report from a vendor input CSV."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT_ROOT = ROOT / "scripts" / "conformance"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from score_conformance import _load_rows, score_rows  # noqa: E402


def _markdown(report: dict[str, object]) -> str:
    lines = [
        "# Nepali Time Reliability Conformance Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Achieved level: {report['achieved_level']}",
        "",
        "Boundary: technical conformance report, not certification or authority.",
        "",
        "## Levels",
        "",
    ]
    levels = report["levels"]
    assert isinstance(levels, dict)
    for level, result in levels.items():
        assert isinstance(result, dict)
        lines.extend(
            [
                f"### {level.title()}",
                "",
                f"Score: {result['score']}/{result['max_score']} ({result['score_percent']}%)",
                "",
                f"Missing checks: {', '.join(result['missing_checks']) if result['missing_checks'] else 'None'}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--md-out", required=True)
    args = parser.parse_args()
    report = score_rows(_load_rows(Path(args.input)))
    report["generated_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    json_path = Path(args.json_out)
    md_path = Path(args.md_out)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    print(json.dumps({"ok": True, "json": str(json_path), "markdown": str(md_path), "achieved_level": report["achieved_level"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

