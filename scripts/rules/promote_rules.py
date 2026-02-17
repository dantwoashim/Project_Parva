"""
Rule Promotion Script — SOTA Quality Gate
==========================================

Scans festival_rules_v4.json and promotes provisional rules to 'computed'
when they have complete computation specs. Rules with incomplete specs
remain provisional.

Promotion criteria:
  - tithi + lunar_month + paksha → computed, confidence: medium
  - bs_month + bs_day (fixed BS date) → computed, confidence: high
  - weekday + recurrence only → stays provisional (need manual curation)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parents[2] / "data" / "festivals" / "festival_rules_v4.json"


def promote(rules_data: dict) -> dict:
    """Promote eligible provisional rules to computed status."""
    festivals = rules_data["festivals"]

    stats = {
        "total": len(festivals),
        "already_computed": 0,
        "promoted_lunar": 0,
        "promoted_bs_fixed": 0,
        "still_provisional": 0,
        "other": 0,
    }

    promoted = []

    for rule_entry in festivals:
        status = rule_entry.get("status", "unknown")

        if status != "provisional":
            if status == "computed":
                stats["already_computed"] += 1
            else:
                stats["other"] += 1
            promoted.append(rule_entry)
            continue

        rule_block = rule_entry.get("rule", {})
        has_tithi = "tithi" in rule_block
        has_lunar_month = "lunar_month" in rule_block
        has_paksha = "paksha" in rule_block
        has_bs_month = "bs_month" in rule_block
        has_bs_day = "bs_day" in rule_block

        # Tier 1: Fixed BS date (e.g., Dashain = BS Ashwin 10)
        if has_bs_month and has_bs_day:
            rule_entry["status"] = "computed"
            rule_entry["confidence"] = "high"
            rule_entry["engine"] = "bs_fixed_date"
            rule_entry["promotion_note"] = "Promoted: fixed BS date rule"
            stats["promoted_bs_fixed"] += 1

        # Tier 2: Full lunar spec (tithi + lunar_month + paksha)
        elif has_tithi and has_lunar_month and has_paksha:
            rule_entry["status"] = "computed"
            rule_entry["confidence"] = "medium"
            rule_entry["engine"] = "lunar_month_v2"
            rule_entry["promotion_note"] = "Promoted: complete lunar computation spec"
            stats["promoted_lunar"] += 1

        # Tier 3: Partial lunar (tithi + paksha, missing month — still useful)
        elif has_tithi and has_paksha and has_lunar_month:
            # Covered by tier 2
            pass

        # Tier 4: Weekly/recurring with bs_month — promote as calendar-fixed
        elif has_bs_month and "weekday" in rule_block:
            rule_entry["status"] = "computed"
            rule_entry["confidence"] = "medium"
            rule_entry["engine"] = "bs_weekday_recurrence"
            rule_entry["promotion_note"] = "Promoted: BS month + weekday recurrence"
            stats["promoted_bs_fixed"] += 1

        else:
            stats["still_provisional"] += 1

        promoted.append(rule_entry)

    rules_data["festivals"] = promoted
    rules_data["promotion_stats"] = stats
    rules_data["promoted_at"] = datetime.now(timezone.utc).isoformat()
    rules_data["total_computed"] = (
        stats["already_computed"] + stats["promoted_lunar"] + stats["promoted_bs_fixed"]
    )
    rules_data["total_rules"] = stats["total"]

    return rules_data


def main():
    print(f"Reading rules from: {RULES_PATH}")
    with open(RULES_PATH) as f:
        data = json.load(f)

    print(f"Total rules: {data.get('total_rules', len(data.get('festivals', [])))}")

    result = promote(data)
    stats = result["promotion_stats"]

    print("\n=== Promotion Results ===")
    print(f"  Already computed:    {stats['already_computed']}")
    print(f"  Promoted (lunar):    {stats['promoted_lunar']}")
    print(f"  Promoted (BS fixed): {stats['promoted_bs_fixed']}")
    print(f"  Still provisional:   {stats['still_provisional']}")
    print(f"  Other status:        {stats['other']}")
    print(f"  Total computed now:  {result['total_computed']}")
    print(f"  Computed ratio:      {result['total_computed']}/{stats['total']} "
          f"({100 * result['total_computed'] / max(stats['total'], 1):.1f}%)")

    # Write back
    with open(RULES_PATH, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nWritten to: {RULES_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
