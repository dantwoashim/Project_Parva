export type PolicyTraceStep = {
  event: string;
  detail?: Record<string, unknown>;
};

export type PolicyDecision = {
  kind: "policy_decision";
  policyId: string;
  selectedMethod: string;
  reviewRequired: boolean;
  notAuthority: true;
  trace: PolicyTraceStep[];
};

export function policyDecision(
  policyId: string,
  selectedMethod: string,
  trace: PolicyTraceStep[] = [],
): PolicyDecision {
  return {
    kind: "policy_decision",
    policyId,
    selectedMethod,
    reviewRequired: true,
    notAuthority: true,
    trace,
  };
}
