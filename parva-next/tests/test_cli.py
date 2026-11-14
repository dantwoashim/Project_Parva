"""The command line, end to end through capsys."""

from pathlib import Path

import pytest

from parva.cli import main


def test_convert_ad(capsys: pytest.CaptureFixture[str]) -> None:
    main(["convert", "2026-04-14"])
    assert "2083-01-01" in capsys.readouterr().out


def test_convert_bad_bs_exits(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:  # sys.exit's message lands on .code (stderr on a real run)
        main(["convert", "2082-01-32", "--bs"])
    assert "does not exist" in str(exc.value)


def test_month(capsys: pytest.CaptureFixture[str]) -> None:
    main(["month", "2083", "6"])
    out = capsys.readouterr().out
    assert "Ashwin 2083" in out and "31 days" in out


def test_audit(capsys: pytest.CaptureFixture[str]) -> None:
    pytest.importorskip("swisseph")
    main(["audit", "2026"])
    assert "19/20" in capsys.readouterr().out


def test_check(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    csv = tmp_path / "payroll.csv"
    csv.write_text("date\n2026-10-19\n2026-10-24\n2026-10-27\n2083-13-01\n", encoding="utf-8")
    main(["check", str(csv)])
    out = capsys.readouterr().out
    assert "dashain-holidays" in out
    assert "saturday" in out
    assert "INVALID" in out
    assert "4 rows, 4 to review" in out


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["--version"])
    assert "2083.2" in capsys.readouterr().out
