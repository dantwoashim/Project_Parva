from app.future_bs import data_acquisition as da


def test_untrusted_sources_are_never_official_claim_sources():
    for source_type in ["publisher_reference", "software_table_reference", "third_party_reference", "needs_review"]:
        row = da.make_witness(
            source_id=source_type,
            source_type=source_type,
            source_name=source_type,
            extraction_method="unit",
            extraction_confidence=1.0,
            ad_date="2025-04-14",
            bs_year=2082,
            bs_month=1,
        )
        assert row["usable_for_official_claim"] == "false"
