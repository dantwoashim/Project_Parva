"""Causal-bitplane-backed working-day solver."""

from __future__ import annotations

from app.forge.bitplanes import build_month_bitplanes
from app.membranes.unsat import unsat_membrane
from app.sources.hashing import canonical_json_hash


def _explain_day(day: int, planes: dict) -> list[str]:
    reasons: list[str] = []
    if planes["holiday"].bits[day - 1]:
        reasons.append("holiday")
    if planes["saturday"].bits[day - 1]:
        reasons.append("weekend")
    if not reasons and not planes["working_day"].bits[day - 1]:
        reasons.append("not_working_day")
    return reasons


def solve_working_days(
    *,
    bs_year: int,
    bs_month: int,
    count: int,
    holidays: set[int] | None = None,
    weekend_offsets: set[int] | None = None,
) -> dict:
    """Select working days by replaying causal bitplanes.

    ``weekend_offsets`` remains a compatibility input, but it no longer drives
    the solver. Weekends are derived from the BS-to-AD conversion weekday plane.
    """

    del weekend_offsets
    planes = build_month_bitplanes(bs_year=bs_year, bs_month=bs_month, holidays=holidays or set())
    expression = {
        "op": "and",
        "planes": ["working_day"],
        "excludes": ["holiday", "saturday"],
    }
    accepted: list[int] = []
    rejected: list[dict] = []

    for day, is_candidate in enumerate(planes["working_day"].bits, start=1):
        reasons = _explain_day(day, planes)
        if reasons:
            rejected.append(
                {
                    "day": day,
                    "reasons": reasons,
                    "causal_stamps": [
                        plane.cause_stamps[day - 1]
                        for plane in (planes["working_day"], planes["holiday"], planes["saturday"])
                    ],
                }
            )
            continue
        if is_candidate:
            accepted.append(day)
            if len(accepted) == count:
                break

    bitplane_hashes = {name: plane.hash for name, plane in planes.items()}
    candidate_payload = {"selected_days": accepted, "bitplane_hashes": bitplane_hashes, "expression": expression}
    if len(accepted) < count:
        unsat = unsat_membrane(
            {"bs_year": bs_year, "bs_month": bs_month, "count": count, "bitplane_hashes": bitplane_hashes},
            ["not_enough_working_days"],
            ["reduce_count", "relax_holiday_filter", "relax_weekend_filter"],
        )
        unsat["input_bitplane_hashes"] = bitplane_hashes
        unsat["compiled_bit_expression"] = expression
        unsat["candidate_mask_hash"] = f"sha256:{canonical_json_hash(candidate_payload)}"
        unsat["rejected_dates"] = rejected
        return unsat

    return {
        "kind": "constraint_solution",
        "input_constraints": {"bs_year": bs_year, "bs_month": bs_month, "count": count, "holidays": sorted(holidays or [])},
        "compiled_bit_expression": expression,
        "input_bitplane_hashes": bitplane_hashes,
        "candidate_mask_hash": f"sha256:{canonical_json_hash(candidate_payload)}",
        "selected_days": accepted,
        "rejected_dates": rejected,
        "unsat_core": [],
        "suggested_relaxations": [],
        "bitplane_witness_refs": list(bitplane_hashes.values()),
        "claim_boundary": "solver_decision_support_not_authority",
        "proof_pack": {
            "level": "replay",
            "planes": {name: plane.as_dict() for name, plane in planes.items()},
            "expression": expression,
            "candidate_mask_hash": f"sha256:{canonical_json_hash(candidate_payload)}",
        },
    }
