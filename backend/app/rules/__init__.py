"""Rules package exports."""

from .catalog_v4 import (
    get_rule_v4,
    get_rules_coverage,
    get_rules_scoreboard,
    list_rules_v4,
    load_catalog_v4,
    rule_has_algorithm,
    rule_quality_band,
)
from .dsl import is_rule_executable, rule_to_dsl_document
from .execution import (
    RuleExecutionResult,
    calculate_rule_occurrence,
    calculate_rule_occurrence_with_fallback,
    validation_cases_for_rule,
)
from .service import FestivalRuleService, get_rule_service

__all__ = [
    "FestivalRuleService",
    "RuleExecutionResult",
    "get_rule_service",
    "get_rule_v4",
    "get_rules_coverage",
    "get_rules_scoreboard",
    "list_rules_v4",
    "load_catalog_v4",
    "rule_has_algorithm",
    "rule_quality_band",
    "is_rule_executable",
    "rule_to_dsl_document",
    "calculate_rule_occurrence",
    "calculate_rule_occurrence_with_fallback",
    "validation_cases_for_rule",
]
