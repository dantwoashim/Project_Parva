#!/usr/bin/env python3
"""Generate the 2083 Ashwin red-team replay artifact."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

if os.getenv("PARVA_SCRIPT_REEXEC") != "1":
    needs_python311 = sys.version_info < (3, 11)
    try:
        import pydantic  # noqa: F401
        import swisseph  # noqa: F401
    except ModuleNotFoundError:
        needs_python311 = True
    if needs_python311:
        env = {**os.environ, "PARVA_SCRIPT_REEXEC": "1"}
        python_executable = os.getenv("PARVA_PYTHON", sys.executable)
        completed = subprocess.run([python_executable, *sys.argv], env=env)
        raise SystemExit(completed.returncode)

from app.research.future_bs.red_team_2083 import replay_2083_ashwin  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("data/future_bs/reports/case_2083_ashwin_replay_v_final.json"))
    parser.add_argument("--md", type=Path, default=Path("data/future_bs/reports/case_2083_ashwin_replay_v_final.md"))
    parser.add_argument("--force-recompute", action="store_true")
    args = parser.parse_args()
    payload = replay_2083_ashwin(force_recompute=args.force_recompute)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.md.parent.mkdir(parents=True, exist_ok=True)
    args.md.write_text(
        "\n".join(
            [
                "# 2083 Ashwin Replay",
                "",
                "Publication status: `computed_prediction_not_official`.",
                "",
                f"- Predicted days: {payload.get('parva_prediction_before_publication', {}).get('predicted_days')}",
                f"- Prediction set 95: {payload.get('parva_prediction_before_publication', {}).get('prediction_set_95')}",
                f"- Risk label: {payload.get('parva_prediction_before_publication', {}).get('risk_label')}",
                f"- Recommended policy: {payload.get('recommended_policy')}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"ok": True, "out": str(args.out), "predicted_days": payload["parva_prediction_before_publication"]["predicted_days"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
