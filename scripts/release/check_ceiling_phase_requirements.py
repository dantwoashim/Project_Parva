#!/usr/bin/env python3
"""Check Phase 01-15 prompt requirements against local repository artifacts."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROMPT_DIR = PROJECT_ROOT / "Project_Parva_Phase_Codex_Prompts"
REPORT_DIR = PROJECT_ROOT / "reports" / "ceiling_execution"
CONFIG_PATH = PROJECT_ROOT / "config" / "ceiling-phase-requirements.json"
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@dataclass(frozen=True)
class PhaseCheck:
    phase: str
    prompt: str
    required_paths: list[str]
    reports: list[str]
    missing: list[str]
    special: list[dict[str, str]]

    @property
    def status(self) -> str:
        if self.missing:
            return "fail"
        if any(item["status"] == "fail" for item in self.special):
            return "fail"
        return "pass"

    def as_dict(self) -> dict[str, object]:
        return {
            "phase": self.phase,
            "prompt": self.prompt,
            "status": self.status,
            "required_paths": self.required_paths,
            "reports": self.reports,
            "missing": self.missing,
            "special": self.special,
        }


def _section(text: str, start_heading: str, end_heading: str) -> str:
    start = text.index(start_heading)
    end = text.index(end_heading, start)
    return text[start:end]


def _prompt_paths(text: str) -> list[str]:
    section = _section(text, "## 4. Files and directories to inspect or create", "## 5. Detailed implementation tasks")
    paths: list[str] = []
    for match in re.finditer(r"`([^`]+)`", section):
        value = match.group(1).strip()
        if value.endswith("/"):
            value = value.rstrip("/")
        paths.append(value)
    return paths


def _report_paths(text: str) -> list[str]:
    values = set(re.findall(r"`(reports/phase_[^`]+\.md)`", text))
    return sorted(values)


def _exists(path_text: str) -> bool:
    path = PROJECT_ROOT / path_text
    return path.exists()


def _canonical_corpus_check() -> dict[str, str]:
    corpus_path = PROJECT_ROOT / "tests" / "fixtures" / "canonicalization_equivalence.json"
    if not corpus_path.exists():
        return {"name": "canonicalization_corpus_size", "status": "fail", "detail": "fixture missing"}
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    equivalent = len(corpus.get("equivalent") or [])
    different = len(corpus.get("different") or [])
    status = "pass" if equivalent >= 50 and different >= 50 else "fail"
    return {
        "name": "canonicalization_corpus_size",
        "status": status,
        "detail": f"equivalent={equivalent}, different={different}",
    }


def _source_docket_check() -> dict[str, str]:
    raw = PROJECT_ROOT / "data" / "sources" / "raw" / "official" / "sample_2082_calendar_notice.txt"
    normalized = PROJECT_ROOT / "data" / "sources" / "normalized" / "calendar" / "sample_2082_calendar_rows.json"
    docket = PROJECT_ROOT / "data" / "sources" / "dockets" / "sample_2082_calendar_notice.json"
    receipt = PROJECT_ROOT / "data" / "sources" / "extraction_receipts" / "sample_2082_calendar_notice_receipt.json"
    missing = [str(path.relative_to(PROJECT_ROOT)) for path in (raw, normalized, docket, receipt) if not path.exists()]
    return {
        "name": "complete_source_chain",
        "status": "fail" if missing else "pass",
        "detail": "missing=" + ",".join(missing) if missing else "raw->docket->normalized->receipt present",
    }


def _static_forge_check() -> dict[str, str]:
    manifest = PROJECT_ROOT / "static" / "parva-index" / "manifest.json"
    if not manifest.exists():
        return {"name": "static_forge_manifest", "status": "fail", "detail": "manifest missing"}
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    entries = payload.get("entries") or payload.get("files") or []
    status = "pass" if entries else "fail"
    return {"name": "static_forge_manifest", "status": status, "detail": f"entries={len(entries)}"}


def _transparency_check() -> dict[str, str]:
    log = PROJECT_ROOT / "data" / "transparency" / "log.jsonl"
    if not log.exists():
        return {"name": "transparency_log", "status": "fail", "detail": "log missing"}
    lines = [line for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
    return {"name": "transparency_log", "status": "pass" if lines else "fail", "detail": f"entries={len(lines)}"}


SPECIAL_CHECKS = {
    "03": [_canonical_corpus_check],
    "02": [_source_docket_check],
    "04": [_static_forge_check],
    "11": [_transparency_check],
}


def collect() -> list[PhaseCheck]:
    if not list(PROMPT_DIR.glob("PHASE_*.md")) and CONFIG_PATH.exists():
        payload = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        checks = []
        for item in payload["phases"]:
            required = list(item["required_paths"])
            reports = list(item["reports"])
            missing = [path for path in [*required, *reports] if not _exists(path)]
            special = [check() for check in SPECIAL_CHECKS.get(item["phase"], [])]
            checks.append(
                PhaseCheck(
                    phase=item["phase"],
                    prompt=item["prompt"],
                    required_paths=required,
                    reports=reports,
                    missing=missing,
                    special=special,
                )
            )
        return checks

    checks: list[PhaseCheck] = []
    for prompt in sorted(PROMPT_DIR.glob("PHASE_*.md")):
        phase = prompt.name.split("_", 2)[1]
        if phase == "00":
            continue
        text = prompt.read_text(encoding="utf-8")
        required = _prompt_paths(text)
        reports = _report_paths(text)
        missing = [path for path in [*required, *reports] if not _exists(path)]
        special = [check() for check in SPECIAL_CHECKS.get(phase, [])]
        checks.append(
            PhaseCheck(
                phase=phase,
                prompt=prompt.name,
                required_paths=required,
                reports=reports,
                missing=missing,
                special=special,
            )
        )
    return checks


def write_reports(checks: list[PhaseCheck]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(
            {
                "source": "derived_from_phase_prompts",
                "phases": [
                    {
                        "phase": check.phase,
                        "prompt": check.prompt,
                        "required_paths": check.required_paths,
                        "reports": check.reports,
                    }
                    for check in checks
                ],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    payload = {
        "status": "pass" if all(check.status == "pass" for check in checks) else "fail",
        "phases": [check.as_dict() for check in checks],
    }
    (REPORT_DIR / "phase_requirement_matrix.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = ["# Ceiling Phase Requirement Matrix", ""]
    for check in checks:
        lines.append(f"## Phase {check.phase}: {check.status}")
        lines.append(f"- Prompt: `{check.prompt}`")
        lines.append(f"- Required path count: {len(check.required_paths)}")
        lines.append(f"- Report aliases: {', '.join(f'`{report}`' for report in check.reports)}")
        lines.append(f"- Missing: {', '.join(f'`{path}`' for path in check.missing) if check.missing else 'none'}")
        for item in check.special:
            lines.append(f"- {item['name']}: {item['status']} ({item['detail']})")
        lines.append("")
    (REPORT_DIR / "phase_requirement_matrix.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    checks = collect()
    write_reports(checks)
    failed = [check for check in checks if check.status != "pass"]
    if failed:
        for check in failed:
            print(f"Phase {check.phase} failed: missing={check.missing} special={check.special}")
        return 1
    print("Ceiling phase requirement matrix passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
