"""Comparison report tests."""

from app.future_bs.compare import compare_external_sheet
from app.future_bs.comparison_report import comparison_report_markdown
from app.services.future_bs_service import predict_bs_year


def test_compare_detects_mismatch_and_report_renders():
    parva_months = predict_bs_year(2085)["months"]
    external_months = list(parva_months)
    external_months[1] = 32 if external_months[1] != 32 else 31
    comparison = compare_external_sheet(
        "infodev_excel",
        [{"bs_year": 2085, "months": external_months}],
        predict_fn=predict_bs_year,
    )
    report = comparison_report_markdown(comparison)

    assert comparison["summary"]["mismatches"] == 1
    assert "Future BS Month-Length Comparison Report" in report
