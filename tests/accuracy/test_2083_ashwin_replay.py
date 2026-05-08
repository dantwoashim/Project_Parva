from app.future_bs.red_team_2083 import replay_2083_ashwin


def test_2083_ashwin_replay_generates_policy_artifact():
    payload = replay_2083_ashwin(force_recompute=True)
    assert payload["case_id"] == "PARVA-REDTEAM-2083-ASHWIN"
    assert payload["target"]["bs_year"] == 2083
    assert payload["parva_prediction_before_publication"]["prediction_set_95"]
    assert payload["publication_status"] == "computed_prediction_not_official"
