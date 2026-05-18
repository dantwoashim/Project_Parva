# Source and Method Coverage Matrix

This report describes public proof coverage. It is not government, legal, tax, payroll, banking, or Panchanga authority.

- Matrix hash: `sha256:9e37d0ffbfcf64750e97fd4338a65b8994c1f161ce2fb323d794b735145e5615`
- Rows: 29

| Operation | Year | Field | Authority | Coverage | Review | Boundary |
| --- | ---: | --- | --- | --- | --- | --- |
| convert_bs_to_ad | 2070 | ad_date | computed_uncertified | no_eligible_source_coverage | True | computed_conversion_not_source_backed_authority |
| ad_to_bs | 2070 | bs_date | computed_uncertified | no_eligible_source_coverage | True | computed_conversion_not_source_backed_authority |
| validate_bs_date | 2070 | validity | computed_uncertified | no_eligible_source_coverage | True | computed_conversion_not_source_backed_authority |
| holiday | 2070 | membership | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_authority |
| working_day | 2070 | working_day | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_legal_tax_payroll_authority |
| fiscal_year | 2070 | fiscal_year | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_legal_tax_payroll_authority |
| bs_months | 2070 | month_lengths | computed_uncertified | no_eligible_source_coverage | True | computed_solar_civil_or_reference_not_authority |
| convert_bs_to_ad | 2082 | ad_date | static_reference | covered_by_reference_source_not_official | True | sample_source_chain_not_authority |
| ad_to_bs | 2082 | bs_date | static_reference | covered_by_reference_source_not_official | True | sample_source_chain_not_authority |
| validate_bs_date | 2082 | validity | static_reference | covered_by_reference_source_not_official | True | sample_source_chain_not_authority |
| holiday | 2082 | membership | static_reference | covered_by_reference_source_not_official | True | decision_support_not_authority |
| working_day | 2082 | working_day | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_legal_tax_payroll_authority |
| fiscal_year | 2082 | fiscal_year | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_legal_tax_payroll_authority |
| bs_months | 2082 | month_lengths | computed_uncertified | covered_by_reference_source_not_official | True | computed_solar_civil_or_reference_not_authority |
| convert_bs_to_ad | 2083 | ad_date | computed_uncertified | no_eligible_source_coverage | True | computed_conversion_not_source_backed_authority |
| ad_to_bs | 2083 | bs_date | computed_uncertified | no_eligible_source_coverage | True | computed_conversion_not_source_backed_authority |
| validate_bs_date | 2083 | validity | computed_uncertified | no_eligible_source_coverage | True | computed_conversion_not_source_backed_authority |
| holiday | 2083 | membership | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_authority |
| working_day | 2083 | working_day | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_legal_tax_payroll_authority |
| fiscal_year | 2083 | fiscal_year | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_legal_tax_payroll_authority |
| bs_months | 2083 | month_lengths | computed_uncertified | no_eligible_source_coverage | True | computed_solar_civil_or_reference_not_authority |
| convert_bs_to_ad | 2099 | ad_date | computed_uncertified | no_eligible_source_coverage | True | computed_conversion_not_source_backed_authority |
| ad_to_bs | 2099 | bs_date | computed_uncertified | no_eligible_source_coverage | True | computed_conversion_not_source_backed_authority |
| validate_bs_date | 2099 | validity | computed_uncertified | no_eligible_source_coverage | True | computed_conversion_not_source_backed_authority |
| holiday | 2099 | membership | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_authority |
| working_day | 2099 | working_day | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_legal_tax_payroll_authority |
| fiscal_year | 2099 | fiscal_year | computed_uncertified | no_eligible_source_coverage | True | decision_support_not_legal_tax_payroll_authority |
| bs_months | 2099 | month_lengths | computed_uncertified | no_eligible_source_coverage | True | computed_solar_civil_or_reference_not_authority |
| panchanga_summary | 2082 | tithi/nakshatra/yoga/karana/sunrise | computed_uncertified | method_backed_with_pinned_fixture | True | computed_ephemeris_not_panchanga_authority |
