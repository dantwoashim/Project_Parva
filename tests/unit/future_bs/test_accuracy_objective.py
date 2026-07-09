from app.research.future_bs.accuracy_objective import objective_from_counts


def test_objective_heavily_penalizes_wrong_green():
    safe = objective_from_counts(total_cases=12, top1_correct=11, green_cases=10, green_correct=10)
    unsafe = objective_from_counts(total_cases=12, top1_correct=11, green_cases=11, green_correct=10)
    assert safe["objective_score"] > unsafe["objective_score"]
    assert unsafe["wrong_green_count"] == 1


def test_objective_claim_ready_requires_valid_future_totals():
    payload = objective_from_counts(
        total_cases=72,
        top1_correct=72,
        green_cases=66,
        green_correct=66,
        invalid_future_years=1,
        future_years=117,
    )
    assert payload["claim_ready"] is False
