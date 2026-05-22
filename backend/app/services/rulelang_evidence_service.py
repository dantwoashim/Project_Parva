"""RuleLang evidence packet builder kept outside the trust core."""

from __future__ import annotations

from typing import Any

from app.services.rulelang_service import RuleLangError, evaluate_rule_payload
from app.services.trust_infrastructure_service import (
    TrustInfrastructureError,
    build_evidence_packet,
    resolve_release_id,
)


def build_rule_execution_evidence_packet(
    *,
    release_id: str | None = None,
    rule_id: str,
    input_payload: dict[str, Any],
    trace_id: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    selected = resolve_release_id(release_id)
    try:
        result = evaluate_rule_payload(
            rule_id,
            input_payload,
            release_id=selected,
            trace_id=trace_id,
            include_evidence=False,
        )
    except RuleLangError as exc:
        raise TrustInfrastructureError(str(exc), status_code=exc.status_code) from exc
    return build_evidence_packet(
        packet_type="rule_execution",
        input_payload={
            "rule_id": rule_id,
            "input": input_payload,
        },
        result=result,
        release_id=selected,
        trace_id=trace_id,
        generated_at=generated_at,
    )
