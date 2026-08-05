from __future__ import annotations

from app.research.future_bs import data_acquisition
from app.research.future_bs.high_trust_acquisition import _collect_family, _discover_links


def test_acquisition_orchestrator_reexports_storage_helpers() -> None:
    assert callable(data_acquisition.ensure_dirs)
    assert callable(data_acquisition.write_jsonl)


def test_family_collector_can_run_without_network_attempts() -> None:
    family = {
        "family": "contract-test",
        "name": "Contract test",
        "tier": "needs_review",
        "cache_dir": "contract-test",
        "urls": [],
    }

    rows, attempts, failures, cached = _collect_family(
        family,
        set(),
        max_urls=1,
        timeout_seconds=1,
    )

    assert rows == []
    assert attempts == []
    assert failures == []
    assert cached == []


def test_link_discovery_finds_javascript_pdf_without_viewer_sample() -> None:
    page = """
    <a href="/notice/annual-calendar">notice</a>
    <object data="https://pdfobject.com/pdf/sample.pdf"></object>
    <script>var pdf = 'https://files.gov.np/calendar-2084.pdf';</script>
    """

    links = _discover_links("https://agency.gov.np/page", page)

    assert "https://files.gov.np/calendar-2084.pdf" in links
    assert all("pdfobject.com/pdf/sample.pdf" not in link for link in links)
