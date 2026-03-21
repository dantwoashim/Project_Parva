from __future__ import annotations

from pathlib import Path

from scripts.governance.verify_approval import check_file


def test_verify_approval_passes_when_all_markers_present(tmp_path: Path):
    md = tmp_path / "rfc.md"
    md.write_text(
        "\n".join(
            [
                "## Evidence",
                "Evidence text",
                "## Sources",
                "Source text",
                "Reviewed-by: Reviewer",
                "Signed-off-by: Author",
            ]
        ),
        encoding="utf-8",
    )

    ok, errors = check_file(md)
    assert ok is True
    assert errors == []


def test_verify_approval_passes_when_required_reviewers_are_present(tmp_path: Path):
    md = tmp_path / "approved.md"
    md.write_text(
        "\n".join(
            [
                "## Evidence",
                "Evidence text",
                "## Sources",
                "Source text",
                "Reviewed-by: Engineering / automated_release_candidate_gates",
                "Reviewed-by: QA / golden_journeys_suite",
                "Signed-off-by: Release preparation / codex",
            ]
        ),
        encoding="utf-8",
    )

    ok, errors = check_file(md, ("Engineering", "QA"))
    assert ok is True
    assert errors == []


def test_verify_approval_fails_when_markers_missing(tmp_path: Path):
    md = tmp_path / "bad.md"
    md.write_text("## Evidence\nOnly one section", encoding="utf-8")

    ok, errors = check_file(md)
    assert ok is False
    assert any("Missing marker" in e for e in errors)


def test_verify_approval_fails_when_required_reviewer_is_missing(tmp_path: Path):
    md = tmp_path / "missing-role.md"
    md.write_text(
        "\n".join(
            [
                "## Evidence",
                "Evidence text",
                "## Sources",
                "Source text",
                "Reviewed-by: Engineering / automated_release_candidate_gates",
                "Signed-off-by: Release preparation / codex",
            ]
        ),
        encoding="utf-8",
    )

    ok, errors = check_file(md, ("Engineering", "Design"))
    assert ok is False
    assert errors == ["Missing required reviewer: Design"]
