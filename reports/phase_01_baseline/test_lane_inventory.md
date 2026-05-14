# Phase 01 Test Lane Inventory



| Test path | Public-safe? | Marker needed | Current marker | Data dependency | Recommended lane |
| --- | --- | --- | --- | --- | --- |
| backend/tests/test_api_calendar.py | True | none | none | public fixtures | public_ci |
| backend/tests/test_desktop_reference_api.py | True | none | none | public fixtures | public_ci |
| backend/tests/test_ephemeris.py | True | none | none | public fixtures | public_ci |
| tests/__init__.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_2083_ashwin_replay.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_disagreement_increases_risk.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_false_green_rate.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_future_bs_official_holdout.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/accuracy/test_future_bs_performance.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/accuracy/test_future_risk_map_no_invalid_year_totals.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_future_year_total_gate.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_green_zone_accuracy.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_hamropatro_shadow_experimental.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_invalid_reconstructed_rows_excluded.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_invalid_years_non_claimable.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_model_regression.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_no_tier5_6_in_official_claims.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_no_wrong_green_on_official_time_travel.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_official_claim_readiness_gate.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_prediction_artifact_validity.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_prediction_run_immutability.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_prediction_set_wide_not_green.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_regime_ensemble_green_certification.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_regime_ensemble_no_future_shadow_leakage.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_regime_ensemble_no_tier5_6_official_contamination.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_regime_ensemble_preserves_official_2078_2083.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_regime_loop_acceptance_gate.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_source_policy_metrics_exist.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_source_policy_separation.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_wide_prediction_set_not_green.py | True | none | none | public fixtures | public_ci |
| tests/accuracy/test_wrong_green_count_zero_or_claim_false.py | True | none | none | public fixtures | public_ci |
| tests/architecture/test_import_boundaries.py | True | none | none | public fixtures | public_ci |
| tests/artifacts/test_final_artifacts_exist.py | True | none | none | public fixtures | public_ci |
| tests/conformance/test_conformance_runner.py | True | none | none | public fixtures | protocol_ci |
| tests/contract/test_explainability_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_forecast_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_frontend_routes_vs_backend_profile.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_launch_profile_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_layer10_protocol_contract.py | True | none | none | public fixtures | protocol_ci |
| tests/contract/test_layer2_public_api_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_layer3_source_metadata_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_layer4_compliance_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_layer5_trust_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_layer6_timegraph_contract.py | False | private_source | none | private source archive | private_source_ci |
| tests/contract/test_layer7_rulelang_contract.py | False | private_source | none | private source archive | private_source_ci |
| tests/contract/test_layer8_impact_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_layer9_agent_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_reliability_policy_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_response_shapes.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_tithi_response.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_uncertainty_contract.py | True | none | none | public fixtures | public_ci |
| tests/contract/test_v3_routing_contract.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_30_year_past_reconstruction.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_agreement_graph.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_data_target_checker.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_high_trust_source_manifest.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_high_trust_witness_schema.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_human_review_queue.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_merge_high_trust_witnesses.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_month_start_reconstruction.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_no_duplicate_weak_sources_as_progress.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_no_untrusted_source_as_official.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_source_trust_scoring.py | True | none | none | public fixtures | public_ci |
| tests/data_acquisition/test_witness_schema.py | True | none | none | public fixtures | public_ci |
| tests/future_bs/test_ayanamsha_calibration_candidates.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/future_bs/test_candidate_rule_selection.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/future_bs/test_green_certification.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/future_bs/test_human_review_promotion_plan.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/future_bs/test_latent_truth_model.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/future_bs/test_month_start_inversion_workbench.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/future_bs/test_month_start_lattice_decoder.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/future_bs/test_regime_change_detection.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/future_bs/test_rule_inversion_effective_cutoff.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/future_bs/test_source_independence.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/future_bs/test_weak_label_fusion.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/helpers.py | True | none | none | public fixtures | public_ci |
| tests/integration/__init__.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_accuracy_lab_scripts.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_billing_async_offload.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_billing_monetization.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_boundary_suite_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_bs_extended_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_cache_precompute.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_calendar_dual_month_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_calendar_model_risk_routes.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_calendar_proof_capsule_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_calendar_var_report.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_engine_e2e.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_enterprise_routes.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_external_sheet_audit.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_feed_integrations_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_festival_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_festival_authority_conflicts_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_festival_coverage_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_festival_explain.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_festival_override_authority_merge.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_festival_timeline_search_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_festival_truth_lab_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_future_bs_routes.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/integration/test_panchanga_degraded_mode.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_personal_stack_v3.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_places_and_muhurta_calendar_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_policy_routes_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_private_surface_proof_capsules.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_provenance_dashboard_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_public_artifacts_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_request_guards.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_resolve_and_spec_endpoints.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_source_precedence.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_temples_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_temporal_compass_api.py | True | none | none | public fixtures | public_ci |
| tests/integration/test_v3_envelope_opt_in.py | True | none | none | public fixtures | public_ci |
| tests/performance/test_calendar_model_risk_latency.py | True | none | none | performance environment | performance_ci |
| tests/performance/test_festival_upcoming_cache.py | True | none | none | performance environment | performance_ci |
| tests/public_safety/test_public_release_safety.py | True | none | none | public fixtures | public_ci |
| tests/regression/test_existing_calendar_platform_routes.py | True | none | none | public fixtures | public_ci |
| tests/unit/__init__.py | True | none | none | public fixtures | public_ci |
| tests/unit/benchmark/test_benchmark_tools.py | True | none | none | public fixtures | public_ci |
| tests/unit/billing/test_api_key_hashing.py | True | none | none | public fixtures | security_ci |
| tests/unit/bootstrap/test_access_control.py | True | none | none | public fixtures | public_ci |
| tests/unit/bootstrap/test_app_prewarm.py | True | none | none | public fixtures | public_ci |
| tests/unit/bootstrap/test_middleware.py | True | none | none | public fixtures | public_ci |
| tests/unit/bootstrap/test_rate_limit.py | True | none | none | public fixtures | public_ci |
| tests/unit/bootstrap/test_security_hardening.py | True | none | none | public fixtures | security_ci |
| tests/unit/bootstrap/test_settings.py | True | none | none | public fixtures | security_ci |
| tests/unit/cache/test_precomputed_cache_report.py | True | none | none | public fixtures | public_ci |
| tests/unit/calendar/__init__.py | True | none | none | public fixtures | public_ci |
| tests/unit/calendar/test_bikram_sambat.py | True | none | none | public fixtures | public_ci |
| tests/unit/calendar/test_bs_lookup_boundaries.py | True | none | none | public fixtures | public_ci |
| tests/unit/calendar/test_bs_official_range_exhaustive.py | False | private_source | none | private source archive | private_source_ci |
| tests/unit/calendar/test_bs_year_mapping.py | True | none | none | public fixtures | public_ci |
| tests/unit/calendar/test_calculator.py | True | none | none | public fixtures | public_ci |
| tests/unit/calendar/test_kundali_v2_regression.py | True | none | none | public fixtures | public_ci |
| tests/unit/calendar/test_muhurta_v2_regression.py | True | none | none | public fixtures | public_ci |
| tests/unit/calendar/test_nepal_sambat.py | True | none | none | public fixtures | public_ci |
| tests/unit/calendar/test_tithi.py | True | none | none | public fixtures | public_ci |
| tests/unit/calendar/test_tithi_core_lunar_month.py | True | none | none | public fixtures | public_ci |
| tests/unit/core/test_paths.py | True | none | none | public fixtures | public_ci |
| tests/unit/core/test_public_calculation_trace.py | True | none | none | public fixtures | public_ci |
| tests/unit/differential/test_framework.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_adhik_maas_reference.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_ayanamsa.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_bs_confidence_modes.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_bs_extended_samples.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_bs_future_calibration.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_bs_overlap_fixture.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_ephemeris_500.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_lunar_boundaries.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_sankranti_24.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_sunrise_kathmandu.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_timezone.py | True | none | parametrize | public fixtures | public_ci |
| tests/unit/engine/test_tithi_boundaries_30.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine/test_visible_sun_times.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine_plugins/test_islamic_hebrew_plugins.py | True | none | none | public fixtures | public_ci |
| tests/unit/engine_plugins/test_registry_and_validation.py | True | none | none | public fixtures | public_ci |
| tests/unit/explainability/test_store.py | True | none | none | public fixtures | public_ci |
| tests/unit/festivals/test_validation.py | True | none | none | public fixtures | public_ci |
| tests/unit/future_bs/test_accuracy_objective.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_calendar_var.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_civil_rules.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_claim_readiness.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_claim_readiness_artifact_first.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_committee_rule_posterior.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_compare.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_confidence.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_corpus.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_future_bs_risk_alpha.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_loan_impact.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_perturbation_robustness.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_precedent_tower.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_precomputed_store.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_prediction_sets.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_report_store.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_risk_thresholds.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_sequence_decoder.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_shadow_residual_correction.py | True | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_solar_ingress_cache.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_solar_ingress_predictor.py | True | research_artifact | parametrize | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_solar_ingress_solver.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_trusted_jpl_cache_readonly.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/future_bs/test_year_total_gate.py | False | research_artifact | none | generated research artifacts or public-safe future-BS metadata | research_artifact_ci |
| tests/unit/governance/test_verify_approval.py | True | none | none | public fixtures | public_ci |
| tests/unit/provenance/test_attestation_profile.py | True | none | none | public fixtures | security_ci |
| tests/unit/provenance/test_snapshot_hashing.py | True | none | none | public fixtures | public_ci |
| tests/unit/provenance/test_transparency_log.py | True | none | none | public fixtures | public_ci |
| tests/unit/release/test_verify_release.py | True | none | none | public fixtures | public_ci |
| tests/unit/reliability/test_boundary_suite.py | True | none | none | public fixtures | public_ci |
| tests/unit/reliability/test_differential_manifest.py | True | none | none | public fixtures | public_ci |
| tests/unit/reliability/test_runtime_status.py | True | none | none | public fixtures | public_ci |
| tests/unit/rules/test_catalog_v4.py | True | none | none | public fixtures | public_ci |
| tests/unit/rules/test_month2_foundation.py | True | none | none | public fixtures | public_ci |
| tests/unit/rules/test_month8_release_gate.py | True | none | none | public fixtures | public_ci |
| tests/unit/rules/test_rule_service_partial_cache.py | True | none | none | public fixtures | public_ci |
| tests/unit/rules/test_rule_triads.py | True | none | none | public fixtures | public_ci |
| tests/unit/scripts/test_cloudrun_blueprint.py | True | none | none | public fixtures | public_ci |
| tests/unit/scripts/test_documented_routes.py | True | none | none | public fixtures | public_ci |
| tests/unit/scripts/test_frontend_bundle_budget.py | True | none | none | public fixtures | public_ci |
| tests/unit/scripts/test_package_source_archive.py | False | private_source | none | private source archive | private_source_ci |
| tests/unit/scripts/test_package_submission_bundle.py | True | none | none | public fixtures | public_ci |
| tests/unit/scripts/test_partner_access_tooling.py | True | none | none | public fixtures | security_ci |
| tests/unit/scripts/test_production_preflight.py | True | none | none | public fixtures | public_ci |
| tests/unit/scripts/test_release_candidate_dossier.py | True | none | none | public fixtures | public_ci |
| tests/unit/scripts/test_repo_hygiene.py | True | none | none | public fixtures | public_ci |
| tests/unit/scripts/test_route_inventory.py | True | none | none | public fixtures | public_ci |
| tests/unit/sdk/test_python_sdk.py | True | none | none | public fixtures | public_ci |
| tests/unit/services/test_calendar_conversion_owner.py | True | none | none | public fixtures | public_ci |
| tests/unit/services/test_calendar_surface_risk.py | True | none | none | public fixtures | public_ci |
| tests/unit/services/test_place_search_service.py | True | none | none | public fixtures | public_ci |
| tests/unit/services/test_rulelang_safety.py | True | none | none | public fixtures | public_ci |
| tests/unit/services/test_runtime_cache.py | True | none | none | public fixtures | public_ci |
| tests/unit/sources/test_review_queue.py | True | none | none | public fixtures | public_ci |
| tests/unit/sources/test_source_validation.py | True | none | none | public fixtures | public_ci |
| tests/unit/tools/test_blinded_audit.py | True | none | none | public fixtures | public_ci |
| tests/unit/tools/test_ingest_moha_pipeline.py | True | none | none | public fixtures | public_ci |
| tests/unit/trust/test_temporal_trust_tools.py | True | none | none | public fixtures | public_ci |
| tests/unit/uncertainty/test_uncertainty_model.py | True | none | none | public fixtures | public_ci |
