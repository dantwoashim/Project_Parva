from __future__ import annotations

import argparse
import json
import os
from typing import Any

from .client import DEFAULT_API_BASE, ParvaClient


def _client(args: argparse.Namespace) -> ParvaClient:
    return ParvaClient(base_url=args.base_url)


def _print(payload: dict[str, Any]) -> int:
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def _split_bs_date(value: str) -> tuple[int, int, int]:
    parts = value.split("-")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError("BS date must be YYYY-MM-DD")
    try:
        year, month, day = (int(part) for part in parts)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("BS date must use numeric YYYY-MM-DD parts") from exc
    return year, month, day


def _today(args: argparse.Namespace) -> int:
    return _print(_client(args).get_today())


def _convert(args: argparse.Namespace) -> int:
    client = _client(args)
    if args.from_calendar == "ad":
        return _print(client.ad_to_bs(args.date))
    year, month, day = _split_bs_date(args.date)
    return _print(client.bs_to_ad(year, month, day))


def _validate(args: argparse.Namespace) -> int:
    year, month, day = _split_bs_date(args.date)
    return _print(_client(args).validate_bs_date(year, month, day))


def _capabilities(args: argparse.Namespace) -> int:
    client = _client(args)
    if args.surface == "future-bs":
        return _print(client.get_future_bs_capabilities())
    if args.surface == "enterprise":
        return _print(client.get_enterprise_capabilities())
    return _print(client.get_trust_capabilities())


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="parva", description="Project Parva public API CLI")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("PARVA_API_BASE", DEFAULT_API_BASE),
        help="Project Parva API base URL. Defaults to PARVA_API_BASE or the public v3 API.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    today = subparsers.add_parser("today", help="Fetch current public calendar context.")
    today.set_defaults(func=_today)

    convert = subparsers.add_parser("convert", help="Convert between AD and BS.")
    convert.add_argument("from_calendar", choices=["ad", "bs"])
    convert.add_argument("date", help="AD or BS date in YYYY-MM-DD form.")
    convert.set_defaults(func=_convert)

    validate = subparsers.add_parser("validate-bs", help="Validate a BS date via public conversion.")
    validate.add_argument("date", help="BS date in YYYY-MM-DD form.")
    validate.set_defaults(func=_validate)

    capabilities = subparsers.add_parser("capabilities", help="Fetch public capability metadata.")
    capabilities.add_argument("surface", choices=["future-bs", "enterprise", "trust"])
    capabilities.set_defaults(func=_capabilities)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
