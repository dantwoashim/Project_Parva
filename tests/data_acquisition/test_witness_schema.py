from app.research.future_bs import data_acquisition as da


def test_witness_row_has_required_fields_and_claim_policy():
    row = da.make_witness(
        source_id="weak_source",
        source_type="third_party_reference",
        source_name="Weak public witness",
        extraction_method="unit_test",
        extraction_confidence=0.7,
        ad_date="2025-04-14",
        bs_year=2082,
        bs_month=1,
        raw_text="unit",
    )

    assert set(da.WITNESS_FIELDS).issubset(row)
    assert row["publication_status"] if "publication_status" in row else da.PUBLICATION_STATUS
    assert row["usable_for_training"] == "true"
    assert row["usable_for_official_claim"] == "false"
    assert row["source_tier"] == 6
