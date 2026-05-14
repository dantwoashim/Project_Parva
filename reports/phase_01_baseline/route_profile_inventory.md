# Phase 01 Route Profile Inventory

Import status: `pass`

## `minimal_public`

| Policy | Audience | Access | Path | Private/experimental | Future exact risk | Sensitive mutation | CPU-heavy risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| calendar_public_demo | public | public | /v3/api/calendar | False | False | False | False |
| future_bs_public_demo | public | public | /v4/api/future-bs/capabilities | False | False | False | False |
| trust | trust | trust_read | /api/trust | False | False | False | False |
| timegraph | trust | timegraph_read | /api/timegraph | False | False | False | False |
| rules | trust | rules_read | /api/rules | False | False | False | False |

## `public_demo`

| Policy | Audience | Access | Path | Private/experimental | Future exact risk | Sensitive mutation | CPU-heavy risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| calendar_public_demo | public | public | /v3/api/calendar | False | False | False | False |
| future_bs_public_demo | public | public | /v4/api/future-bs/capabilities | False | False | False | False |
| trust | trust | trust_read | /api/trust | False | False | False | False |
| timegraph | trust | timegraph_read | /api/timegraph | False | False | False | False |
| rules | trust | rules_read | /api/rules | False | False | False | False |

## `public_reference`

| Policy | Audience | Access | Path | Private/experimental | Future exact risk | Sensitive mutation | CPU-heavy risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| festivals_timeline | public | public | /api/festivals | False | False | False | False |
| festivals | public | public | /api/festivals | False | False | False | False |
| calendar | public | public | /api/calendar | False | False | False | False |
| enterprise | public | public | /api/enterprise | False | False | False | False |
| compliance | public | public | /api/compliance | False | False | False | False |
| future_bs | public | public | /v4/api/future-bs/capabilities | False | False | False | False |
| calendar_model_risk | public | public | /v5/api/calendar-model-risk/capabilities | False | False | False | False |
| locations | public | public | /api/temples | False | False | False | False |
| observances | public | public | /api/observances | False | False | False | False |
| places | public | public | /api/places | False | False | False | False |
| policy | public | public | /api/policy | False | False | False | False |
| feeds | public | public | /api/feeds | False | False | False | False |
| engine | public | public | /api/engine | False | False | False | False |
| forecast | public | public | /api/forecast | False | False | False | False |
| muhurta | public | public | /api/muhurta | False | False | False | True |
| muhurta_calendar | public | public | /api/muhurta | False | False | False | False |
| temporal | public | public | /api/temporal | False | False | False | False |
| glossary | public | public | /api/glossary | False | False | False | False |
| reliability | trust | reliability_read | /api/reliability | False | False | False | False |
| spec | trust | spec_read | /api/spec | False | False | False | False |
| public_artifacts | trust | public_artifacts_read | /api/public | False | False | False | False |
| trust | trust | trust_read | /api/trust | False | False | False | False |
| protocol | trust | protocol_read | /api/protocol | False | False | False | False |

## `developer_preview`

| Policy | Audience | Access | Path | Private/experimental | Future exact risk | Sensitive mutation | CPU-heavy risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| festivals_timeline | public | public | /api/festivals | False | False | False | False |
| festivals | public | public | /api/festivals | False | False | False | False |
| calendar | public | public | /api/calendar | False | False | False | False |
| enterprise | public | public | /api/enterprise | False | False | False | False |
| compliance | public | public | /api/compliance | False | False | False | False |
| future_bs | public | public | /v4/api/future-bs/capabilities | False | False | False | False |
| calendar_model_risk | public | public | /v5/api/calendar-model-risk/capabilities | False | False | False | False |
| cache | public | public | /api/cache | False | False | False | False |
| explain | public | public | /api/explain | False | False | False | False |
| locations | public | public | /api/temples | False | False | False | False |
| observances | public | public | /api/observances | False | False | False | False |
| places | public | public | /api/places | False | False | False | False |
| policy | public | public | /api/policy | False | False | False | False |
| feeds | public | public | /api/feeds | False | False | False | False |
| engine | public | public | /api/engine | False | False | False | False |
| forecast | public | public | /api/forecast | False | False | False | False |
| resolve | public | public | /api/resolve | False | False | False | False |
| integrations_feeds | public | public | /api/integrations/feeds | False | False | False | False |
| personal | public | public | /api/personal | False | False | False | False |
| muhurta | public | public | /api/muhurta | False | False | False | True |
| muhurta_calendar | public | public | /api/muhurta | False | False | False | False |
| kundali | public | public | /api/kundali | False | False | False | True |
| temporal | public | public | /api/temporal | False | False | False | False |
| muhurta_heatmap | public | public | /api/muhurta | False | False | False | True |
| kundali_graph | public | public | /api/kundali | False | False | False | False |
| glossary | public | public | /api/glossary | False | False | False | False |
| provenance | trust | provenance | /api/provenance | False | False | True | False |
| reliability | trust | reliability_read | /api/reliability | False | False | False | False |
| spec | trust | spec_read | /api/spec | False | False | False | False |
| public_artifacts | trust | public_artifacts_read | /api/public | False | False | False | False |
| timegraph | trust | timegraph_read | /api/timegraph | False | False | False | False |
| trust | trust | trust_read | /api/trust | False | False | False | False |
| rules | trust | rules_read | /api/rules | False | False | False | False |
| impact | trust | impact_read | /api/impact | False | False | False | True |
| agent | trust | agent_read | /api/agent | False | False | False | False |
| protocol | trust | protocol_read | /api/protocol | False | False | False | False |

## `enterprise_preview`

| Policy | Audience | Access | Path | Private/experimental | Future exact risk | Sensitive mutation | CPU-heavy risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| festivals_timeline | public | public | /api/festivals | False | False | False | False |
| festivals | public | public | /api/festivals | False | False | False | False |
| calendar | public | public | /api/calendar | False | False | False | False |
| enterprise | public | public | /api/enterprise | False | False | False | False |
| compliance | public | public | /api/compliance | False | False | False | False |
| future_bs | public | public | /v4/api/future-bs/capabilities | False | False | False | False |
| calendar_model_risk | public | public | /v5/api/calendar-model-risk/capabilities | False | False | False | False |
| billing | public | public | /api/billing | False | False | True | False |
| cache | public | public | /api/cache | False | False | False | False |
| explain | public | public | /api/explain | False | False | False | False |
| locations | public | public | /api/temples | False | False | False | False |
| observances | public | public | /api/observances | False | False | False | False |
| places | public | public | /api/places | False | False | False | False |
| policy | public | public | /api/policy | False | False | False | False |
| feeds | public | public | /api/feeds | False | False | False | False |
| engine | public | public | /api/engine | False | False | False | False |
| forecast | public | public | /api/forecast | False | False | False | False |
| resolve | public | public | /api/resolve | False | False | False | False |
| integrations_feeds | public | public | /api/integrations/feeds | False | False | False | False |
| personal | public | public | /api/personal | False | False | False | False |
| muhurta | public | public | /api/muhurta | False | False | False | True |
| muhurta_calendar | public | public | /api/muhurta | False | False | False | False |
| kundali | public | public | /api/kundali | False | False | False | True |
| temporal | public | public | /api/temporal | False | False | False | False |
| muhurta_heatmap | public | public | /api/muhurta | False | False | False | True |
| kundali_graph | public | public | /api/kundali | False | False | False | False |
| glossary | public | public | /api/glossary | False | False | False | False |
| provenance | trust | provenance | /api/provenance | False | False | True | False |
| reliability | trust | reliability_read | /api/reliability | False | False | False | False |
| spec | trust | spec_read | /api/spec | False | False | False | False |
| public_artifacts | trust | public_artifacts_read | /api/public | False | False | False | False |
| timegraph | trust | timegraph_read | /api/timegraph | False | False | False | False |
| trust | trust | trust_read | /api/trust | False | False | False | False |
| rules | trust | rules_read | /api/rules | False | False | False | False |
| impact | trust | impact_read | /api/impact | False | False | False | True |
| agent | trust | agent_read | /api/agent | False | False | False | False |
| protocol | trust | protocol_read | /api/protocol | False | False | False | False |

## `full`

| Policy | Audience | Access | Path | Private/experimental | Future exact risk | Sensitive mutation | CPU-heavy risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| festivals_timeline | public | public | /api/festivals | False | False | False | False |
| festivals | public | public | /api/festivals | False | False | False | False |
| calendar | public | public | /api/calendar | False | False | False | False |
| enterprise | public | public | /api/enterprise | False | False | False | False |
| compliance | public | public | /api/compliance | False | False | False | False |
| future_bs | public | public | /v4/api/future-bs/capabilities | False | False | False | False |
| calendar_model_risk | public | public | /v5/api/calendar-model-risk/capabilities | False | False | False | False |
| billing | public | public | /api/billing | False | False | True | False |
| cache | public | public | /api/cache | False | False | False | False |
| explain | public | public | /api/explain | False | False | False | False |
| locations | public | public | /api/temples | False | False | False | False |
| observances | public | public | /api/observances | False | False | False | False |
| places | public | public | /api/places | False | False | False | False |
| policy | public | public | /api/policy | False | False | False | False |
| feeds | public | public | /api/feeds | False | False | False | False |
| engine | public | public | /api/engine | False | False | False | False |
| forecast | public | public | /api/forecast | False | False | False | False |
| resolve | public | public | /api/resolve | False | False | False | False |
| integrations_feeds | public | public | /api/integrations/feeds | False | False | False | False |
| personal | public | public | /api/personal | False | False | False | False |
| muhurta | public | public | /api/muhurta | False | False | False | True |
| muhurta_calendar | public | public | /api/muhurta | False | False | False | False |
| kundali | public | public | /api/kundali | False | False | False | True |
| temporal | public | public | /api/temporal | False | False | False | False |
| muhurta_heatmap | public | public | /api/muhurta | False | False | False | True |
| kundali_graph | public | public | /api/kundali | False | False | False | False |
| glossary | public | public | /api/glossary | False | False | False | False |
| provenance | trust | provenance | /api/provenance | False | False | True | False |
| reliability | trust | reliability_read | /api/reliability | False | False | False | False |
| spec | trust | spec_read | /api/spec | False | False | False | False |
| public_artifacts | trust | public_artifacts_read | /api/public | False | False | False | False |
| timegraph | trust | timegraph_read | /api/timegraph | False | False | False | False |
| trust | trust | trust_read | /api/trust | False | False | False | False |
| rules | trust | rules_read | /api/rules | False | False | False | False |
| impact | trust | impact_read | /api/impact | False | False | False | True |
| agent | trust | agent_read | /api/agent | False | False | False | False |
| protocol | trust | protocol_read | /api/protocol | False | False | False | False |

## `full_experimental`

| Policy | Audience | Access | Path | Private/experimental | Future exact risk | Sensitive mutation | CPU-heavy risk |
| --- | --- | --- | --- | --- | --- | --- | --- |
| festivals_timeline | public | public | /api/festivals | False | False | False | False |
| festivals | public | public | /api/festivals | False | False | False | False |
| calendar | public | public | /api/calendar | False | False | False | False |
| enterprise | public | public | /api/enterprise | False | False | False | False |
| compliance | public | public | /api/compliance | False | False | False | False |
| future_bs | public | public | /v4/api/future-bs/capabilities | False | False | False | False |
| future_bs_private | private | experimental_read | /v4/api/future-bs | True | True | False | False |
| calendar_model_risk | public | public | /v5/api/calendar-model-risk/capabilities | False | False | False | False |
| calendar_model_risk_private | private | experimental_read | /v5/api/calendar-model-risk | True | False | False | False |
| billing | public | public | /api/billing | False | False | True | False |
| cache | public | public | /api/cache | False | False | False | False |
| explain | public | public | /api/explain | False | False | False | False |
| locations | public | public | /api/temples | False | False | False | False |
| observances | public | public | /api/observances | False | False | False | False |
| places | public | public | /api/places | False | False | False | False |
| policy | public | public | /api/policy | False | False | False | False |
| feeds | public | public | /api/feeds | False | False | False | False |
| engine | public | public | /api/engine | False | False | False | False |
| forecast | public | public | /api/forecast | False | False | False | False |
| resolve | public | public | /api/resolve | False | False | False | False |
| integrations_feeds | public | public | /api/integrations/feeds | False | False | False | False |
| personal | public | public | /api/personal | False | False | False | False |
| muhurta | public | public | /api/muhurta | False | False | False | True |
| muhurta_calendar | public | public | /api/muhurta | False | False | False | False |
| kundali | public | public | /api/kundali | False | False | False | True |
| temporal | public | public | /api/temporal | False | False | False | False |
| muhurta_heatmap | public | public | /api/muhurta | False | False | False | True |
| kundali_graph | public | public | /api/kundali | False | False | False | False |
| glossary | public | public | /api/glossary | False | False | False | False |
| provenance | trust | provenance | /api/provenance | False | False | True | False |
| reliability | trust | reliability_read | /api/reliability | False | False | False | False |
| spec | trust | spec_read | /api/spec | False | False | False | False |
| public_artifacts | trust | public_artifacts_read | /api/public | False | False | False | False |
| timegraph | trust | timegraph_read | /api/timegraph | False | False | False | False |
| trust | trust | trust_read | /api/trust | False | False | False | False |
| rules | trust | rules_read | /api/rules | False | False | False | False |
| impact | trust | impact_read | /api/impact | False | False | False | True |
| agent | trust | agent_read | /api/agent | False | False | False | False |
| protocol | trust | protocol_read | /api/protocol | False | False | False | False |
