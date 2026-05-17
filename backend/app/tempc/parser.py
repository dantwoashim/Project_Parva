"""Tiny TempC parser for payroll-safe date workflows."""

from __future__ import annotations

import re

from app.tempc.ir import TempCProgram

PROGRAM_RE = re.compile(r"program\s+(?P<name>[a-zA-Z_][\w]*)\s*\{(?P<body>.*)\}\s*$", re.DOTALL)
BS_MONTH_RE = re.compile(r"let\s+(?P<name>[a-zA-Z_][\w]*)\s*=\s*bs_month\((?P<year>\d{4}),\s*(?P<month>\d{1,2})\)")
WORKING_DAYS_RE = re.compile(
    r"let\s+(?P<name>[a-zA-Z_][\w]*)\s*=\s*working_days\(in:\s*(?P<range>[a-zA-Z_][\w]*),\s*exclude:\s*holidays\(\)\)"
)
EMIT_RE = re.compile(
    r"emit\s+(?P<kind>payroll_schedule|payroll_safe_dates)"
    r"(?:\((?P<target>[a-zA-Z_][\w]*),\s*policy:\s*\"(?P<policy>[^\"]+)\"\)|\s+count=(?P<count>\d+))"
)


def parse_tempc(source: str) -> TempCProgram:
    match = PROGRAM_RE.search(source.strip())
    if not match:
        raise ValueError("TempC program must use: program <name> { ... }")
    name = match.group("name")
    body = "\n".join(
        line.strip().rstrip(";")
        for line in match.group("body").splitlines()
        if line.strip() and not line.strip().startswith("#")
    )
    statements: list[dict] = []
    bindings: dict[str, dict] = {}
    parameters: dict = {"count": 5}
    operation = "payroll_safe_dates"

    for raw in body.splitlines():
        if bs_match := BS_MONTH_RE.fullmatch(raw):
            statement = {
                "type": "let",
                "name": bs_match.group("name"),
                "value": {
                    "type": "bs_month",
                    "bs_year": int(bs_match.group("year")),
                    "bs_month": int(bs_match.group("month")),
                },
            }
            bindings[statement["name"]] = statement["value"]
            parameters["bs_year"] = statement["value"]["bs_year"]
            parameters["bs_month"] = statement["value"]["bs_month"]
            statements.append(statement)
            continue
        if wd_match := WORKING_DAYS_RE.fullmatch(raw):
            source_range = wd_match.group("range")
            if source_range not in bindings:
                raise ValueError(f"TempC binding not found: {source_range}")
            statement = {
                "type": "let",
                "name": wd_match.group("name"),
                "value": {
                    "type": "working_days",
                    "range": source_range,
                    "exclude": ["holidays"],
                },
            }
            bindings[statement["name"]] = statement["value"]
            statements.append(statement)
            continue
        if emit_match := EMIT_RE.fullmatch(raw):
            emit_kind = emit_match.group("kind")
            if emit_kind == "payroll_safe_dates":
                parameters["count"] = int(emit_match.group("count") or 5)
            else:
                target = emit_match.group("target")
                if target not in bindings:
                    raise ValueError(f"TempC emit target not found: {target}")
                operation = "payroll_schedule"
                parameters["policy"] = emit_match.group("policy")
                parameters["target"] = target
            statements.append({"type": "emit", "kind": emit_kind, "target": emit_match.group("target")})
            continue
        raise ValueError(f"unsupported TempC statement: {raw}")

    if not any(statement.get("type") == "emit" for statement in statements):
        raise ValueError("TempC program must emit a schedule/report")

    return TempCProgram(name, operation, parameters, tuple(statements))
