export type BoundaryVector = {
  claimBoundary: string;
  reviewRequired: boolean;
  notAuthority: true;
  blockedUseCases: string[];
};

export const DEFAULT_BLOCKED_USE_CASES = [
  "legal_final_authority",
  "tax_final_authority",
  "payroll_final_authority",
  "banking_contract_authority",
  "government_calendar_publication",
  "panchanga_final_authority",
] as const;

export function noAuthorityBoundary(claimBoundary: string): BoundaryVector {
  return {
    claimBoundary,
    reviewRequired: true,
    notAuthority: true,
    blockedUseCases: [...DEFAULT_BLOCKED_USE_CASES],
  };
}
