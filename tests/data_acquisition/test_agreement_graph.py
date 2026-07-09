from app.research.future_bs import data_acquisition as da


def test_agreement_graph_prefers_higher_trust_candidate(tmp_path, monkeypatch):
    monkeypatch.setattr(da, "CORPUS_DIR", tmp_path)
    witnesses = [
        da.make_witness(
            source_id="official",
            source_type="official_verified",
            source_name="Official",
            extraction_method="unit",
            extraction_confidence=0.95,
            ad_date="2025-04-14",
            bs_year=2082,
            bs_month=1,
        ),
        da.make_witness(
            source_id="weak",
            source_type="third_party_reference",
            source_name="Weak",
            extraction_method="unit",
            extraction_confidence=0.99,
            ad_date="2025-04-15",
            bs_year=2082,
            bs_month=1,
        ),
    ]

    graph = da.build_agreement_graph(witnesses)
    node = graph["nodes"]["2082-01"]

    assert node["chosen_month_start_ad"] == "2025-04-14"
    assert node["conflict"] is True
