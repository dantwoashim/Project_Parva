#!/usr/bin/env python3
"""Generate a public-safe Project Parva evidence packet."""

# ruff: noqa: E402
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.trust_infrastructure_service import (
    TrustInfrastructureError,
    build_compliance_decision_evidence_packet,
    build_date_conversion_evidence_packet,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a public-safe evidence packet.")
    parser.add_argument("--type", choices=["date_conversion", "compliance_decision"], required=True)
    parser.add_argument("--release-id")
    parser.add_argument("--ad-date")
    parser.add_argument("--bs-date")
    parser.add_argument("--profile-id", default="nepal_private_company_default")
    parser.add_argument("--decision-intent", default="general")
    parser.add_argument("--generated-at", default="2026-05-13T00:00:00Z")
    parser.add_argument("--trace-id", default="cli-trace")
    args = parser.parse_args(argv)

    try:
        if args.type == "date_conversion":
            payload = build_date_conversion_evidence_packet(
                release_id=args.release_id,
                ad_date=args.ad_date,
                bs_date=args.bs_date,
                trace_id=args.trace_id,
                generated_at=args.generated_at,
            )
        else:
            payload = build_compliance_decision_evidence_packet(
                release_id=args.release_id,
                profile_id=args.profile_id,
                bs_date=args.bs_date,
                ad_date=args.ad_date,
                decision_intent=args.decision_intent,
                trace_id=args.trace_id,
                generated_at=args.generated_at,
            )
    except TrustInfrastructureError as exc:
        print(f"evidence packet generation failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
