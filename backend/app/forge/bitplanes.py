"""Static bundle bitplane helpers."""

from __future__ import annotations

from app.bitplanes.causal import CausalBitplane
from app.calendar.bikram_sambat import bs_to_gregorian, days_in_bs_month


def build_working_day_plane(days: int, weekend_offsets: set[int]) -> CausalBitplane:
    cause_stamps = tuple(
        {
            "day": index,
            "value": index not in weekend_offsets,
            "reason": "default_working_day" if index not in weekend_offsets else "weekend_offset",
            "source": "static_bundle_manifest",
            "policy": "working_day_bitplane@v1",
        }
        for index in range(1, days + 1)
    )
    return CausalBitplane(
        name="working_day",
        bits=tuple(index not in weekend_offsets for index in range(1, days + 1)),
        witness_refs=("static_bundle_manifest",),
        cause_stamps=cause_stamps,
    )


def build_month_bitplanes(
    *,
    bs_year: int,
    bs_month: int,
    holidays: set[int] | None = None,
    festival_windows: dict[str, set[int]] | None = None,
    overlay_days: set[int] | None = None,
    weekend_weekdays: set[int] | None = None,
) -> dict[str, CausalBitplane]:
    """Build causal month bitplanes from actual BS-to-AD date truth.

    ``weekend_weekdays`` uses Python's ``date.weekday()`` numbering. The public
    default is Saturday only, which is ``5``.
    """

    holidays = holidays or set()
    festival_windows = festival_windows or {}
    overlay_days = overlay_days or set()
    weekend_weekdays = weekend_weekdays or {5}
    days = days_in_bs_month(bs_year, bs_month)
    working_bits: list[bool] = []
    holiday_bits: list[bool] = []
    weekend_bits: list[bool] = []
    review_bits: list[bool] = []
    source_backed_bits: list[bool] = []
    computed_bits: list[bool] = []
    working_causes: list[dict] = []
    holiday_causes: list[dict] = []
    weekend_causes: list[dict] = []
    review_causes: list[dict] = []
    source_backed_causes: list[dict] = []
    computed_causes: list[dict] = []
    month_bits: list[bool] = []
    month_causes: list[dict] = []
    fiscal_bits: list[bool] = []
    fiscal_causes: list[dict] = []
    overlay_bits: list[bool] = []
    overlay_causes: list[dict] = []

    for day in range(1, days + 1):
        ad_date = bs_to_gregorian(bs_year, bs_month, day)
        is_weekend = ad_date.weekday() in weekend_weekdays
        is_holiday = day in holidays
        is_working_day = not is_weekend and not is_holiday
        stamp = {
            "bs_date": f"{bs_year:04d}-{bs_month:02d}-{day:02d}",
            "ad_date": ad_date.isoformat(),
            "day": day,
            "source": "bs_ad_conversion_and_public_policy",
            "policy": "working_day_bitplane@v1",
        }
        working_bits.append(is_working_day)
        holiday_bits.append(is_holiday)
        weekend_bits.append(is_weekend)
        review_bits.append(True)
        source_backed_bits.append(False)
        computed_bits.append(True)
        month_bits.append(True)
        fiscal_bits.append(bs_month >= 4)
        overlay_bits.append(day in overlay_days)
        working_causes.append({**stamp, "value": is_working_day, "reason": "working_day" if is_working_day else "blocked_by_holiday_or_weekend"})
        holiday_causes.append({**stamp, "value": is_holiday, "reason": "holiday_input" if is_holiday else "holiday_non_membership"})
        weekend_causes.append({**stamp, "value": is_weekend, "reason": "weekend_weekday" if is_weekend else "not_weekend"})
        review_causes.append({**stamp, "value": True, "reason": "public_policy_review_required"})
        source_backed_causes.append({**stamp, "value": False, "reason": "no_official_source_docket_bound_to_bit"})
        computed_causes.append({**stamp, "value": True, "reason": "computed_from_bs_ad_conversion"})
        month_causes.append({**stamp, "value": True, "reason": f"within_bs_month_{bs_month}"})
        fiscal_causes.append(
            {
                **stamp,
                "value": bs_month >= 4,
                "reason": "nepal_fiscal_year_month" if bs_month >= 4 else "previous_fiscal_year_month",
            }
        )
        overlay_causes.append(
            {
                **stamp,
                "value": day in overlay_days,
                "reason": "overlay_branch_applied" if day in overlay_days else "baseline_no_overlay",
            }
        )

    refs = ("static_bundle_manifest", "bs_ad_conversion", "public_policy_profile")
    planes = {
        "working_day": CausalBitplane("working_day", tuple(working_bits), refs, tuple(working_causes)),
        "holiday": CausalBitplane("holiday", tuple(holiday_bits), refs, tuple(holiday_causes)),
        "saturday": CausalBitplane("saturday", tuple(weekend_bits), refs, tuple(weekend_causes)),
        "review_required": CausalBitplane("review_required", tuple(review_bits), refs, tuple(review_causes)),
        "source_backed": CausalBitplane("source_backed", tuple(source_backed_bits), refs, tuple(source_backed_causes)),
        "computed": CausalBitplane("computed", tuple(computed_bits), refs, tuple(computed_causes)),
        f"month:{bs_month}": CausalBitplane(f"month:{bs_month}", tuple(month_bits), refs, tuple(month_causes)),
        "fiscal_period": CausalBitplane("fiscal_period", tuple(fiscal_bits), refs, tuple(fiscal_causes)),
        "overlay:branch": CausalBitplane("overlay:branch", tuple(overlay_bits), refs, tuple(overlay_causes)),
    }
    for festival_id, days_set in festival_windows.items():
        bits = tuple(day in days_set for day in range(1, days + 1))
        causes = tuple(
            {
                "bs_date": f"{bs_year:04d}-{bs_month:02d}-{day:02d}",
                "day": day,
                "value": day in days_set,
                "reason": "festival_window" if day in days_set else "outside_festival_window",
                "festival_id": festival_id,
                "source": "festival_rule_profile",
                "policy": "festival_window_bitplane@v1",
            }
            for day in range(1, days + 1)
        )
        planes[f"festival_window:{festival_id}"] = CausalBitplane(
            f"festival_window:{festival_id}",
            bits,
            ("festival_rule_profile",),
            causes,
        )
    return planes
