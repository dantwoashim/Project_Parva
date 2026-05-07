import subprocess


def test_calendar_var_report_script(tmp_path):
    pdf = tmp_path / "var.pdf"
    json_path = tmp_path / "var.json"
    subprocess.run(
        [
            "py",
            "-3.11",
            "scripts/future_bs/generate_calendar_var_report.py",
            "--sample",
            "--out",
            str(pdf),
            "--json",
            str(json_path),
        ],
        check=True,
    )
    assert pdf.exists() and pdf.stat().st_size > 100
    assert json_path.exists()
