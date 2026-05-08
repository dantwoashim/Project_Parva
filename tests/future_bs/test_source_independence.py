from app.future_bs.truth_fusion.source_independence import build_source_independence_graph


def test_source_independence_graph_has_nodes():
    payload = build_source_independence_graph()
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["source_count"] > 0
    assert "edges" in payload
