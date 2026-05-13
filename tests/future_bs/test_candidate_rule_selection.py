from __future__ import annotations

from app.future_bs.program_synthesis.program_search import run_program_synthesis


def test_candidate_rule_selection_reports_bounded_search_not_open_ended_synthesis():
    payload = run_program_synthesis(
        {
            "features": [
                {"month_length": 31, "manual_review_required": False},
                {"month_length": 30, "manual_review_required": True},
            ]
        }
    )

    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["synthesis_mode"] == "bounded_candidate_rule_selection_v1"
    assert payload["algorithm_claim"] == "scored_candidate_dsl_search_not_open_ended_program_synthesis"
    assert payload["selected_program"]
    assert payload["programs"]
