"""Command line.

parva today
parva convert 2026-04-14              parva convert 2083-01-01
parva month 2083 6
parva holidays 2083 [--scope all]
parva festival dashain [--year 2026]
parva audit 2026
parva check payroll.csv [--bs]        # flag rows that are invalid, holidays, Saturdays or ungazetted
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import date, datetime, timedelta, timezone
from typing import Any

from . import VERSION, bs, holidays, review


def _print(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2, default=str))


def cmd_today(_: argparse.Namespace) -> None:
    b = bs.to_bs(datetime.now(timezone(timedelta(hours=5, minutes=45))).date())
    print(f"{b.ad.isoformat()}  {b}  {b.nepali()}")


def cmd_convert(a: argparse.Namespace) -> None:
    b = bs.parse_either(a.date, a.bs)
    print(f"{b.ad.isoformat()} {b.ad:%A}  =  {b} ({b.month_name} {b.day}, {b.year})  =  {b.nepali()}")
    print(f"sources: {', '.join(b.sources)}")


def cmd_month(a: argparse.Namespace) -> None:
    n = bs.month_days(a.year, a.month)
    first, last = bs.to_ad(a.year, a.month, 1), bs.to_ad(a.year, a.month, n)
    print(f"{bs.NAMES[a.month - 1]} {a.year}  ({n} days, {first.isoformat()} to {last.isoformat()})")
    print("Su Mo Tu We Th Fr Sa")
    print("   " * ((first.weekday() + 1) % 7), end="")
    for day in range(1, n + 1):
        d = bs.to_ad(a.year, a.month, day)
        mark = "*" if holidays.on(d) else " "
        print(f"{day:2d}{mark}", end="\n" if d.weekday() == 5 else "")
    print("\n* gazetted national holiday" if holidays.source(a.year) else "\n(no gazette for this year)")


def cmd_holidays(a: argparse.Namespace) -> None:
    for h in holidays.of_year(a.year, a.scope):
        span = f" (+{h['days'] - 1}d)" if h["days"] > 1 else ""
        print(f"{h['ad']}  {h['bs']}  {h['id']:22s} {h['scope']:20s} {h['name']}{span}")


def cmd_festival(a: argparse.Namespace) -> None:
    from . import festivals

    o = festivals.occurrence(a.id, a.year or date.today().year)
    _print({**o.as_dict(), "name": festivals.INFO.get(a.id, {}).get("name")})


def cmd_audit(a: argparse.Namespace) -> None:
    from . import festivals

    rows = festivals.audit(a.year)
    both = sum(1 for o in festivals.in_year(a.year) if o.gazette and o.engine)
    print(f"{a.year}: gazette and engine agree on {both - len(rows)}/{both}")
    for r in rows:
        print(f"  {r['id']:22s} gazette {r['gazette']}  engine {r['engine']}  ({r['delta_days']:+d} d)")


def cmd_check(a: argparse.Namespace) -> None:
    """Read a CSV with a date column and report everything a payroll run should look at."""
    with open(a.csv, encoding="utf-8", newline="") as f:
        rows = review.review(review.read_dates(f.read(), a.column), a.bs)
    problems = 0
    for i, r in enumerate(rows, start=2):
        if r["error"]:
            problems += 1
            print(f"line {i}: {r['input']!r}: INVALID - {r['error']}")
        elif r["flags"]:
            problems += 1
            print(f"line {i}: {r['input']} = {r['ad']} / {r['bs']}: {', '.join(r['flags'])}")
    print(f"{len(rows)} rows, {problems} to review")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="parva", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", action="version", version=VERSION)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("today").set_defaults(fn=cmd_today)

    convert = sub.add_parser("convert")
    convert.add_argument("date")
    convert.add_argument("--bs", action="store_true", help="read the date as BS")
    convert.set_defaults(fn=cmd_convert)

    month = sub.add_parser("month")
    month.add_argument("year", type=int)
    month.add_argument("month", type=int)
    month.set_defaults(fn=cmd_month)

    hol = sub.add_parser("holidays")
    hol.add_argument("year", type=int)
    hol.add_argument("--scope", default="national")
    hol.set_defaults(fn=cmd_holidays)

    fest = sub.add_parser("festival")
    fest.add_argument("id")
    fest.add_argument("--year", type=int)
    fest.set_defaults(fn=cmd_festival)

    audit = sub.add_parser("audit")
    audit.add_argument("year", type=int)
    audit.set_defaults(fn=cmd_audit)

    check = sub.add_parser("check")
    check.add_argument("csv")
    check.add_argument("--column")
    check.add_argument("--bs", action="store_true", help="dates are BS")
    check.set_defaults(fn=cmd_check)
    return p


def main(argv: Sequence[str] | None = None) -> None:
    a = build_parser().parse_args(argv)
    try:
        a.fn(a)
    except (ValueError, KeyError, OSError) as exc:
        sys.exit(f"error: {exc}")


if __name__ == "__main__":
    main()
