#!/usr/bin/env python3
"""Generate a deterministic 200+ case public conformance fixture corpus."""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = PROJECT_ROOT / "conformance" / "corpus" / "core" / "generated_public_conversion_220_cases.json"


def main() -> int:
    valid_cases = []
    for year in range(2080, 2085):
        for month in range(1, 13):
            for day in (1, 15, 28):
                valid_cases.append(
                    {
                        "case_id": f"generated.valid.bs_{year}_{month:02d}_{day:02d}",
                        "input": {"bs_date": f"{year:04d}-{month:02d}-{day:02d}"},
                        "expected": {
                            "status": "pass",
                            "result_shape": "conversion_payload",
                            "publication_status": "source_backed_public_reference",
                        },
                    }
                )
    invalid_cases = []
    for year in range(2080, 2085):
        for month in (0, 13, 99):
            for day in (0, 32, 99):
                invalid_cases.append(
                    {
                        "case_id": f"generated.invalid.bs_{year}_{month:02d}_{day:02d}",
                        "input": {"bs_date": f"{year:04d}-{month:02d}-{day:02d}"},
                        "expected": {
                            "status": "fail",
                            "reason": "invalid_bs_date_must_not_pass_conformance",
                        },
                    }
                )
    payload = {
        "corpus_id": "generated_public_conversion_220_cases",
        "generated_at": "2026-05-14",
        "description": "Deterministic public conformance fixture expansion for source-backed conversion and invalid-date behavior.",
        "valid_cases": valid_cases[:175],
        "invalid_cases": invalid_cases[:45],
        "case_count": 220,
    }
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {payload['case_count']} cases to {OUTPUT.relative_to(PROJECT_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
