from app.future_bs.sequence_decoder import decode_year_sequence


def test_sequence_decoder_selects_valid_total_with_supported_adjustment():
    details = [
        {"final_days": 30, "probability": {"30_days": 0.7, "31_days": 0.3}, "confidence_score": 0.7}
        for _ in range(12)
    ]
    payload = decode_year_sequence(2091, details)
    assert payload["valid"] is True
    assert payload["decoded_total"] in {365, 366}
    assert payload["adjustments"]
