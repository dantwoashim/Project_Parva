from app.festivals.validation import validate_festival_catalog_rows


def test_validate_festival_catalog_rows_rejects_duplicate_ids():
    errors = validate_festival_catalog_rows(
        [
            {"id": "dashain", "name": "Dashain"},
            {"id": "dashain", "name": "Dashain Copy"},
        ]
    )

    assert errors == ["Duplicate festival ids: dashain"]


def test_validate_festival_catalog_rows_accepts_unique_ids():
    errors = validate_festival_catalog_rows(
        [
            {"id": "dashain", "name": "Dashain"},
            {"id": "tihar", "name": "Tihar"},
        ]
    )

    assert errors == []
