from app.future_bs.precedent_tower import precedent_tower


def test_precedent_tower_returns_real_cases():
    payload = precedent_tower(2084, 6)
    assert payload["nearest_cases"]
    assert payload["nearest_cases"][0]["bs_year"] < 2084
    assert round(sum(payload["precedent_probabilities"].values()), 4) == 1.0


def test_precedent_tower_respects_time_travel_boundary():
    payload = precedent_tower(2083, 6, train_end=2082)
    assert all(case["bs_year"] <= 2082 for case in payload["nearest_cases"])
