from app.future_bs import claim_readiness as module


def test_claim_readiness_default_does_not_call_live_backtest(monkeypatch):
    def fail_backtest(*args, **kwargs):
        raise AssertionError("live backtest should not run by default")

    monkeypatch.setattr(module, "backtest_model", fail_backtest)
    payload = module.claim_readiness_report()
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert "metric_threshold_passed" in payload
    assert payload["claim_ready_99_green_zone"] is False
