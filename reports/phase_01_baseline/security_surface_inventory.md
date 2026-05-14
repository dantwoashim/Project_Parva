# Phase 01 Security Surface Inventory



Sensitive surfaces require deeper Phase 05 review. This inventory does not certify them.



| Profile | Policy | Access policy | Path | Mutation risk |
| --- | --- | --- | --- | --- |
| minimal_public | timegraph | timegraph_read | /api/timegraph | False |
| minimal_public | rules | rules_read | /api/rules | False |
| public_demo | timegraph | timegraph_read | /api/timegraph | False |
| public_demo | rules | rules_read | /api/rules | False |
| public_reference | reliability | reliability_read | /api/reliability | False |
| public_reference | spec | spec_read | /api/spec | False |
| public_reference | public_artifacts | public_artifacts_read | /api/public | False |
| public_reference | protocol | protocol_read | /api/protocol | False |
| developer_preview | provenance | provenance | /api/provenance | True |
| developer_preview | reliability | reliability_read | /api/reliability | False |
| developer_preview | spec | spec_read | /api/spec | False |
| developer_preview | public_artifacts | public_artifacts_read | /api/public | False |
| developer_preview | timegraph | timegraph_read | /api/timegraph | False |
| developer_preview | rules | rules_read | /api/rules | False |
| developer_preview | impact | impact_read | /api/impact | False |
| developer_preview | agent | agent_read | /api/agent | False |
| developer_preview | protocol | protocol_read | /api/protocol | False |
| enterprise_preview | billing | public | /api/billing | True |
| enterprise_preview | provenance | provenance | /api/provenance | True |
| enterprise_preview | reliability | reliability_read | /api/reliability | False |
| enterprise_preview | spec | spec_read | /api/spec | False |
| enterprise_preview | public_artifacts | public_artifacts_read | /api/public | False |
| enterprise_preview | timegraph | timegraph_read | /api/timegraph | False |
| enterprise_preview | rules | rules_read | /api/rules | False |
| enterprise_preview | impact | impact_read | /api/impact | False |
| enterprise_preview | agent | agent_read | /api/agent | False |
| enterprise_preview | protocol | protocol_read | /api/protocol | False |
| full | billing | public | /api/billing | True |
| full | provenance | provenance | /api/provenance | True |
| full | reliability | reliability_read | /api/reliability | False |
| full | spec | spec_read | /api/spec | False |
| full | public_artifacts | public_artifacts_read | /api/public | False |
| full | timegraph | timegraph_read | /api/timegraph | False |
| full | rules | rules_read | /api/rules | False |
| full | impact | impact_read | /api/impact | False |
| full | agent | agent_read | /api/agent | False |
| full | protocol | protocol_read | /api/protocol | False |
| full_experimental | future_bs_private | experimental_read | /v4/api/future-bs | False |
| full_experimental | calendar_model_risk_private | experimental_read | /v5/api/calendar-model-risk | False |
| full_experimental | billing | public | /api/billing | True |
| full_experimental | provenance | provenance | /api/provenance | True |
| full_experimental | reliability | reliability_read | /api/reliability | False |
| full_experimental | spec | spec_read | /api/spec | False |
| full_experimental | public_artifacts | public_artifacts_read | /api/public | False |
| full_experimental | timegraph | timegraph_read | /api/timegraph | False |
| full_experimental | rules | rules_read | /api/rules | False |
| full_experimental | impact | impact_read | /api/impact | False |
| full_experimental | agent | agent_read | /api/agent | False |
| full_experimental | protocol | protocol_read | /api/protocol | False |



## Static security references



- `grep failed: 'api_key' is not recognized as an internal or external command,
operable program or batch file.`
