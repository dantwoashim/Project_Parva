from __future__ import annotations

import csv
import subprocess
import sys

import pytest

from scripts import audit_verified_corpus


def _write_corpus(path):
    row = {
        "bs_year": "2082",
        "baishakh": "31",
        "jestha": "31",
        "ashadh": "32",
        "shrawan": "31",
        "bhadra": "31",
        "ashwin": "31",
        "kartik": "30",
        "mangsir": "29",
        "poush": "30",
        "magh": "29",
        "falgun": "30",
        "chaitra": "30",
        "source_type": "official_verified",
        "source_name": "test official fixture",
        "source_url_or_scan": "fixture",
        "verification_status": "verified",
        "entered_by": "test",
        "reviewed_by": "test",
        "checksum": "",
        "notes": "",
    }
    row["checksum"] = audit_verified_corpus.row_checksum(row)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=audit_verified_corpus.EXTENDED_FIELDS)
        writer.writeheader()
        writer.writerow(row)


def test_audit_verified_corpus_reports_missing_private_input(tmp_path) -> None:
    missing = tmp_path / "verified_month_lengths.csv"

    with pytest.raises(audit_verified_corpus.MissingPrivateCorpusError) as exc:
        audit_verified_corpus.audit(missing)

    assert str(missing) in str(exc.value)
    assert "private/wide-corpus input" in str(exc.value)


def test_audit_verified_corpus_cli_has_no_traceback_for_missing_input(tmp_path) -> None:
    missing = tmp_path / "verified_month_lengths.csv"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/audit_verified_corpus.py",
            "--corpus",
            str(missing),
            "--audit-log",
            str(tmp_path / "audit.jsonl"),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "private/wide-corpus input" in result.stderr
    assert "Traceback" not in result.stderr


def test_audit_verified_corpus_accepts_small_valid_fixture(tmp_path) -> None:
    corpus = tmp_path / "verified_month_lengths.csv"
    _write_corpus(corpus)

    summary, rows = audit_verified_corpus.audit(corpus)

    assert len(rows) == 1
    assert summary["ok"] is True
    assert summary["official_verified_month_cases"] == 12
