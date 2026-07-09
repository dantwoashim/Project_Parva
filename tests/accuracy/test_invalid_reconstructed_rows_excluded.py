from app.research.future_bs.source_policy import INVALID_RECONSTRUCTED_ROWS, policy_rows


def test_invalid_reconstructed_rows_are_excluded_from_policy_rows():
    for policy in ["official_strict", "medium_high_training", "all_witness_experimental"]:
        keys = {(int(row["bs_year"]), int(row["bs_month"])) for row in policy_rows(policy)}
        assert not (keys & INVALID_RECONSTRUCTED_ROWS)
