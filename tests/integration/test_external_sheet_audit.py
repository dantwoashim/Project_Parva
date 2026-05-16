import subprocess
import sys

import pytest

pytestmark = pytest.mark.research_artifact


def test_external_sheet_audit_script(tmp_path):
    xlsx = tmp_path / "audit.xlsx"
    pdf = tmp_path / "audit.pdf"
    subprocess.run(
        [
            sys.executable,
            "scripts/future_bs/audit_external_bs_sheet.py",
            "--sample",
            "--start",
            "2084",
            "--end",
            "2085",
            "--out",
            str(xlsx),
            "--pdf",
            str(pdf),
        ],
        check=True,
    )
    assert xlsx.exists() and xlsx.stat().st_size > 100
    assert pdf.exists() and pdf.stat().st_size > 100
