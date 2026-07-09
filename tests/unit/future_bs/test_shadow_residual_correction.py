import pytest
from app.research.future_bs.corpus import corpus_rows
from app.research.future_bs.shadow_residual_correction import (
    apply_shadow_residual_rules,
    predict_shadow_corrected_year,
    train_shadow_residual_rules,
)

pytestmark = pytest.mark.research_artifact


def test_shadow_residual_rules_are_not_official_claim_usable():
    rules = train_shadow_residual_rules(min_support=4)

    assert rules["publication_status"] == "computed_prediction_not_official"
    assert rules["official_claim_usable"] is False
    assert rules["calibration_scope"] == "all_available_shadow_reference_not_official_claim"
    assert len(rules["rules"]) == 8


def test_shadow_residual_correction_keeps_recent_official_guard_clean():
    rules = train_shadow_residual_rules(min_support=4)
    actuals = {row.bs_year: row.months for row in corpus_rows() if 2078 <= row.bs_year <= 2083}

    for year, actual in actuals.items():
        payload = predict_shadow_corrected_year(year, rules)
        assert payload["official_claim_usable"] is False
        assert payload["months"] == actual


def test_shadow_residual_rules_can_be_trained_without_target_year_leakage():
    rules_2088 = train_shadow_residual_rules(
        residual_start=2084,
        residual_end=2088,
        min_support=3,
        source_policy="all_witness_experimental",
    )
    rules_2089 = train_shadow_residual_rules(
        residual_start=2084,
        residual_end=2089,
        min_support=3,
        source_policy="all_witness_experimental",
    )

    assert rules_2088["calibration_years"] == [2084, 2088]
    assert rules_2089["calibration_years"] == [2084, 2089]
    assert rules_2088["official_claim_usable"] is False
    assert rules_2089["official_claim_usable"] is False


def test_apply_shadow_residual_rules_exposes_invalid_year_total_for_loop_guard():
    base_months = [30] * 12
    rules = {
        "rules": {
            "month=1|year_mod4=0|base=30": {
                "residual": 1,
                "support_count": 3,
                "empirical_precision": 1.0,
            }
        }
    }

    corrected, applied = apply_shadow_residual_rules(2084, base_months, rules)

    assert sum(corrected) == 361
    assert applied
