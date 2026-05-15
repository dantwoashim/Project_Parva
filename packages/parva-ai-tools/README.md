# Parva AI Tools

Safety-bound LangChain and LlamaIndex wrappers for Project Parva public temporal
tools.

These wrappers expose only public-safe Parva capabilities:

- `parva_convert_bs_to_ad`
- `parva_convert_ad_to_bs`
- `parva_get_today_nepali_date`
- `parva_check_holiday`
- `parva_get_working_day_status`
- `parva_get_fiscal_year`
- `parva_get_festival_date`
- `parva_get_panchanga_summary`
- `parva_check_temporal_claim`

Every normalized response includes:

- `answer`
- `source_tier`
- `confidence`
- `supported_range`
- `claim_boundary`
- `review_required`
- `not_authority`

The package does not expose exact unsupported Future-BS prediction, loan-impact
prediction, private source audit, research backtest, calendar-var stress test,
mutation/admin/trust routes, billing/admin routes, or private route tokens.

Parva is deterministic decision support. It is not official government, legal,
tax, banking, payroll, future-date, or religious authority.
