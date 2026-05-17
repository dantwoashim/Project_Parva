# PARVA_FIELD_PROVENANCE v1

Every enterprise-grade result field must include field provenance containing:

- field_path
- authority
- derivation
- source_docket_id when source-backed
- witness_ids when reviewed
- policy_id
- review_state
- flags

Top-level boundaries are derived from field provenance. A source-backed
authority without a source docket is invalid for public review.
