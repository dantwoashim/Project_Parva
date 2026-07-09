from app.research.future_bs.truth_fusion.source_independence import build_source_independence_graph


def test_source_independence_graph_has_nodes():
    payload = build_source_independence_graph(
        [
            {
                "source_id": "official_sample",
                "source_type": "official_verified",
                "bs_year": "2080",
                "bs_month": "1",
                "ad_date": "2023-04-14",
            },
            {
                "source_id": "printed_sample",
                "source_type": "printed_verified",
                "bs_year": "2080",
                "bs_month": "1",
                "ad_date": "2023-04-14",
            },
        ]
    )
    assert payload["publication_status"] == "computed_prediction_not_official"
    assert payload["source_count"] > 0
    assert "edges" in payload
