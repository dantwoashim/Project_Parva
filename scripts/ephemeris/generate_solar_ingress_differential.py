#!/usr/bin/env python3
"""Generate an honest JPL-vs-Swiss solar longitude differential report."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT / "backend") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "backend"))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import swisseph as swe  # noqa: E402
from app.future_bs.astronomy_confidence import classify_astronomy_confidence  # noqa: E402
from app.future_bs.ephemeris.jpl_spice_adapter import JPLSpiceAdapter  # noqa: E402
from app.future_bs.ephemeris.swiss_adapter import SwissEphemerisAdapter  # noqa: E402

from scripts.ephemeris.verify_kernel_hashes import verify  # noqa: E402

OUT_JSON = PROJECT_ROOT / "reports" / "ephemeris_accuracy" / "solar_ingress_jpl_vs_swiss.json"
OUT_MD = PROJECT_ROOT / "reports" / "ephemeris_accuracy" / "solar_ingress_jpl_vs_swiss.md"
SAMPLE_UTC_DATES = ("2026-04-14T00:00:00+00:00", "2026-07-16T00:00:00+00:00", "2026-10-17T00:00:00+00:00")


def _jd_tdb(timestamp: str) -> float:
    dt = datetime.fromisoformat(timestamp)
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute / 60 + dt.second / 3600)


def _arcseconds_delta(a: float, b: float) -> float:
    delta = (a - b + 180.0) % 360.0 - 180.0
    return round(delta * 3600.0, 6)


def generate_report() -> dict[str, Any]:
    kernel_status = verify()
    de440_verified = any(row["id"] == "de440" and row["status"] == "pass" for row in kernel_status["results"])
    swiss = SwissEphemerisAdapter()
    jpl = JPLSpiceAdapter()
    samples: list[dict[str, Any]] = []

    if de440_verified and jpl.available:
        status = "computed"
        for timestamp in SAMPLE_UTC_DATES:
            jd = _jd_tdb(timestamp)
            swiss_longitude = swiss.apparent_solar_longitude(jd)
            jpl_longitude = jpl.apparent_solar_longitude(jd)
            samples.append(
                {
                    "utc": timestamp,
                    "jpl_apparent_solar_longitude_deg": round(jpl_longitude, 9),
                    "swiss_apparent_solar_longitude_deg": round(swiss_longitude, 9),
                    "delta_arcseconds_jpl_minus_swiss": _arcseconds_delta(jpl_longitude, swiss_longitude),
                }
            )
    else:
        status = "jpl_unavailable"
        for timestamp in SAMPLE_UTC_DATES:
            jd = _jd_tdb(timestamp)
            samples.append(
                {
                    "utc": timestamp,
                    "jpl_apparent_solar_longitude_deg": None,
                    "swiss_apparent_solar_longitude_deg": round(swiss.apparent_solar_longitude(jd), 9),
                    "delta_arcseconds_jpl_minus_swiss": None,
                    "blocked_reason": "JPL DE440 kernel absent or not hash-verified",
                }
            )

    confidence = classify_astronomy_confidence(
        jpl_available=de440_verified and jpl.available,
        has_official_source=False,
        has_published_source=False,
        minutes_to_boundary=None,
    ).payload()
    report = {
        "generated_at": "2026-05-15T00:00:00+00:00",
        "status": status,
        "kernel_status": {
            "ok": kernel_status["ok"],
            "path_policy": kernel_status["path_policy"],
            "results": kernel_status["results"],
        },
        "samples": samples,
        "confidence": confidence,
        "claim_boundary": "astronomy_evidence_not_civil_authority",
        "not_authority": "This report is astronomy evidence only and is not civil calendar authority.",
    }
    return report


def write_report(report: dict[str, Any]) -> None:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        "# Solar Ingress JPL vs Swiss",
        "",
        f"- Status: `{report['status']}`",
        f"- Claim boundary: `{report['claim_boundary']}`",
        f"- JPL kernel hash verification: `{report['kernel_status']['ok']}`",
        "- Local kernel paths are intentionally omitted.",
        "",
        "## Samples",
        "",
    ]
    for sample in report["samples"]:
        delta = sample["delta_arcseconds_jpl_minus_swiss"]
        lines.append(f"- {sample['utc']}: delta arcseconds = `{delta}`")
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    report = generate_report()
    write_report(report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
