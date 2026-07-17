from __future__ import annotations

from app.calendar.source_reconciliation import (
    RenderedMonthEvidence,
    extract_rendered_month_evidence,
    reconcile_rendered_evidence,
)


def test_rendered_calendar_rows_override_stale_embedded_month_lengths() -> None:
    html = """
    <li onclick="openPopUp('2025-7-16')" id="2025-7-16">
      <span id="2082-3-32-usn" style="display: none"></span>
    </li>
    <li onclick="openPopUp('2025-7-17')" id="2025-7-17">
      <span id="2082-4-1-usn" style="display: none"></span>
    </li>
    <li onclick="openPopUp('2025-7-18')" id="2025-7-18">
      <span id="2082-4-2-usn" style="display: none"></span>
    </li>
    """
    evidence = extract_rendered_month_evidence(
        html,
        bs_year=2082,
        bs_month=4,
        source_url="https://example.test/calendar/2082/4",
    )
    assert evidence.days == 2
    assert evidence.start_ad == "2025-07-17"
    assert evidence.end_ad == "2025-07-18"

    embedded = {2082: [31, 31, 31, 32, 31, 31, 30, 29, 30, 29, 30, 30]}
    rendered = [
        RenderedMonthEvidence(2082, 3, 32, "2025-06-15", "2025-07-16", "asar"),
        RenderedMonthEvidence(2082, 4, 31, "2025-07-17", "2025-08-16", "shrawan"),
    ]
    reconciled, drift = reconcile_rendered_evidence(embedded, rendered)

    assert reconciled[2082] == [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30]
    assert [(row["bs_month"], row["rendered_days"]) for row in drift] == [(3, 32), (4, 31)]
    assert embedded[2082][2:4] == [31, 32]
