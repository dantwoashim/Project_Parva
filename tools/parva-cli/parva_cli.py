#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PYTHON_SDK = ROOT / "packages" / "parva-python"
if str(PYTHON_SDK) not in sys.path:
    sys.path.insert(0, str(PYTHON_SDK))

from parva import (  # noqa: E402
    DEFAULT_API_BASE,
    DEFAULT_FUTURE_BS_CAPABILITIES_URL,
    ParvaAPIError,
    ParvaClient,
    ParvaNetworkError,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="parva",
        description="Public-safe Project Parva CLI alpha.",
    )
    parser.add_argument("--base-url", default=DEFAULT_API_BASE, help="Public v3 API base URL")
    parser.add_argument(
        "--future-bs-capabilities-url",
        default=DEFAULT_FUTURE_BS_CAPABILITIES_URL,
        help="Public future-BS capabilities URL",
    )
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout in seconds")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON")

    subcommands = parser.add_subparsers(dest="command", required=True)

    subcommands.add_parser("today", help="Fetch today's public calendar payload")

    convert = subcommands.add_parser("convert", help="Convert dates")
    convert_subcommands = convert.add_subparsers(dest="direction", required=True)
    convert_ad = convert_subcommands.add_parser("ad", help="Convert Gregorian date to BS")
    convert_ad.add_argument("date", help="Gregorian date in YYYY-MM-DD format")
    convert_bs = convert_subcommands.add_parser("bs", help="Convert BS date to Gregorian")
    convert_bs.add_argument("date", help="BS date in YYYY-MM-DD format")

    validate = subcommands.add_parser("validate", help="Validate dates")
    validate_subcommands = validate.add_subparsers(dest="calendar", required=True)
    validate_bs = validate_subcommands.add_parser("bs", help="Validate a BS date")
    validate_bs.add_argument("date", help="BS date in YYYY-MM-DD format")

    capabilities = subcommands.add_parser("capabilities", help="Fetch public capability metadata")
    capabilities_subcommands = capabilities.add_subparsers(dest="surface", required=True)
    capabilities_subcommands.add_parser("future-bs", help="Fetch public future-BS capabilities")

    return parser


def make_client(args: argparse.Namespace) -> ParvaClient:
    return ParvaClient(
        base_url=args.base_url,
        future_bs_capabilities_url=args.future_bs_capabilities_url,
        timeout=args.timeout,
    )


def parse_bs_date(value: str) -> tuple[int, int, int]:
    try:
        year_raw, month_raw, day_raw = value.split("-")
        if len(year_raw) != 4 or len(month_raw) != 2 or len(day_raw) != 2:
            raise ValueError
        return int(year_raw), int(month_raw), int(day_raw)
    except ValueError as exc:
        raise SystemExit(f"Invalid BS date format: {value}. Use YYYY-MM-DD.") from exc


def dispatch(args: argparse.Namespace) -> dict[str, Any]:
    client = make_client(args)
    if args.command == "today":
        return client.get_today()
    if args.command == "convert" and args.direction == "ad":
        return client.ad_to_bs(args.date)
    if args.command == "convert" and args.direction == "bs":
        year, month, day = parse_bs_date(args.date)
        return client.bs_to_ad(year, month, day)
    if args.command == "validate" and args.calendar == "bs":
        year, month, day = parse_bs_date(args.date)
        return client.validate_bs_date(year, month, day)
    if args.command == "capabilities" and args.surface == "future-bs":
        return client.get_future_bs_capabilities()
    raise SystemExit("Unsupported command")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        payload = dispatch(args)
    except (ParvaAPIError, ParvaNetworkError) as exc:
        print(f"Parva CLI error: {exc}", file=sys.stderr)
        return 1
    indent = None if args.compact else 2
    print(json.dumps(payload, ensure_ascii=False, indent=indent, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
