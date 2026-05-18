from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
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


def _read_artifact(path: str) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _verify_proofpack(args: argparse.Namespace) -> int:
    from app.membranes.proofpack import verify_proof_pack

    ok, reason = verify_proof_pack(_read_artifact(args.path))
    print(json.dumps({"verified": ok, "reason": reason}, indent=2, sort_keys=True))
    return 0 if ok else 1


def _verify_timepack(args: argparse.Namespace) -> int:
    from app.membranes.timepack import verify_timepack

    ok, reason = verify_timepack(_read_artifact(args.path))
    print(json.dumps({"verified": ok, "reason": reason}, indent=2, sort_keys=True))
    return 0 if ok else 1


def _markdown_audit_report(report: dict[str, Any]) -> str:
    lines = [
        "# Parva payroll date-risk audit",
        "",
        "This report is decision support only. It is not legal, tax, payroll, banking, government, or official calendar authority.",
        "",
        f"- Rows: {report['summary']['rows']}",
        f"- Review required: {report['summary']['review_required']}",
        f"- Pass: {report['summary']['pass']}",
        f"- Conformance score: {report['summary']['conformance_score']}",
        "",
        "## Findings",
    ]
    for item in report["findings"]:
        issues = ", ".join(item["issues"]) if item["issues"] else "none"
        heading = item.get("bs_date") or f"row {item.get('row_number', '?')}"
        lines.extend(
            [
                "",
                f"### {heading}",
                f"- Status: {item['status']}",
                f"- AD date: {item.get('ad_date') or 'unresolved'}",
                f"- Issues: {issues}",
                f"- Risk score: {item['risk_score']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Forbidden claims",
            "",
            "- No government authority.",
            "- No legal, tax, payroll, or banking authority.",
            "- No official future-date authority.",
            "- No official Panchanga or ritual authority.",
        ]
    )
    return "\n".join(lines) + "\n"


def _audit_payroll(args: argparse.Namespace) -> int:
    from app.workflows.date_risk_audit import audit_date_rows, build_date_risk_timepack

    input_path = Path(args.input)
    rows = list(csv.DictReader(input_path.read_text(encoding="utf-8").splitlines()))
    findings = audit_date_rows(rows, include_proofs=True)
    review_required = sum(1 for item in findings if item["status"] == "review_required")
    passed = len(findings) - review_required
    report = {
        "kind": "parva_payroll_date_risk_audit",
        "version": "v1",
        "input": {"path": str(input_path), "rows": len(rows)},
        "summary": {
            "rows": len(findings),
            "pass": passed,
            "review_required": review_required,
            "conformance_score": round((passed / len(findings)) * 100, 2) if findings else 0.0,
        },
        "claim_boundary": "payroll_date_risk_not_authority",
        "not_authority": True,
        "findings": findings,
    }
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown:
        Path(args.markdown).write_text(_markdown_audit_report(report), encoding="utf-8")
    if args.timepack:
        Path(args.timepack).write_text(
            json.dumps(build_date_risk_timepack(rows), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return _print(report)


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

    proofpack = subparsers.add_parser("verify-proofpack", help="Verify a standalone Parva proof pack.")
    proofpack.add_argument("path")
    proofpack.set_defaults(func=_verify_proofpack)

    timepack = subparsers.add_parser("verify-timepack", help="Verify a standalone Parva Timepack.")
    timepack.add_argument("path")
    timepack.set_defaults(func=_verify_timepack)

    audit = subparsers.add_parser("audit", help="Run offline decision-support audits.")
    audit_subparsers = audit.add_subparsers(dest="audit_command", required=True)
    payroll = audit_subparsers.add_parser("payroll", help="Run a payroll/date-risk CSV audit.")
    payroll.add_argument("--input", required=True, help="CSV input with bs_date/workflow_type columns.")
    payroll.add_argument("--output", help="Write machine-readable JSON report.")
    payroll.add_argument("--markdown", help="Write human-readable Markdown report.")
    payroll.add_argument("--timepack", help="Write replayable Timepack artifact.")
    payroll.set_defaults(func=_audit_payroll)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
