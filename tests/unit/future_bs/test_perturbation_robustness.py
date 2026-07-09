from app.research.future_bs.perturbation_robustness import perturbation_payload


def test_perturbation_payload_has_scenarios_and_reasons():
    payload = perturbation_payload(
        {
            "probability": {"30_days": 0.48, "31_days": 0.52},
            "model_agreement": "1/2",
            "risk_flags": ["sankranti_near_civil_assignment_boundary"],
        },
        committee={"rule_entropy": 0.7, "method_regime_risk": "medium"},
        scenario_count=20,
    )
    assert payload["tested_scenarios"] == 20
    assert payload["risk_label"] in {"YELLOW", "RED"}
    assert payload["most_common_values"]
    assert "civil_cutoff_sensitive" in payload["sensitivity_reasons"]
