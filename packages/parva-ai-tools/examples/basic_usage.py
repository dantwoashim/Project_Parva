#!/usr/bin/env python3
"""Run a public-safe Parva tool wrapper with a local fake client."""

from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from parva_tools.langchain import call_tool  # noqa: E402


class FakeClient:
    def request(self, method: str, route: str, payload: dict):
        return {
            "method": method,
            "route": route,
            "payload": payload,
            "answer": {"ad_date": "2026-04-14"},
            "source_tier": "public_reference",
            "confidence": "source_backed",
            "supported_range": "public_supported_range",
            "claim_boundary": "decision_support_not_authority",
            "review_required": False,
        }


def main() -> int:
    result = call_tool(
        "parva_convert_bs_to_ad",
        {"year": 2083, "month": 1, "day": 1},
        client=FakeClient(),
    )
    print(result["claim_boundary"])
    print(f"review_required={result['review_required']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
