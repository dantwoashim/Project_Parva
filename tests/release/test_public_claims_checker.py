from __future__ import annotations

from scripts.release.check_public_claims import _is_negated, check_public_claims


def test_public_claims_checker_passes_repo() -> None:
    assert check_public_claims() == []


def test_negation_allows_boundary_language() -> None:
    text = "Parva is not legal authority for payroll decisions."
    assert _is_negated(text, text.index("legal authority"))


def test_negation_allows_multiline_boundary_list() -> None:
    previous = "They are not:"
    text = "- legal authority"
    assert _is_negated(text, text.index("legal authority"), previous)


def test_negation_allows_disallowed_claim_list() -> None:
    previous = "## Disallowed Public Claims"
    text = "- Parva publishes the official future BS calendar."
    assert _is_negated(text, text.index("official future BS"), previous)


def test_non_negated_claim_is_not_allowed() -> None:
    text = "Parva is legal authority for payroll decisions."
    assert not _is_negated(text, text.index("legal authority"))
