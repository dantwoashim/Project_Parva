export type ClaimBoundary =
  | 'computed_prediction_not_official'
  | 'not_legal_tax_or_banking_contract_authority'
  | 'parva_protocol_preview_not_legal_authority'
  | string;

export interface SourceRef {
  id: string;
  label?: string;
  tier?: string;
  authority?: string;
  version?: string;
  url?: string | null;
}

export interface SourceAwareMeta {
  source?: SourceRef;
  confidence?: string;
  data_version?: string;
  release_id?: string;
  claim_boundary?: ClaimBoundary;
  warnings?: string[];
  trace_id?: string | null;
  result_class?: string;
}

export interface CalendarTodayResponse {
  ad_date?: string;
  bs_date?: {
    year?: number;
    month?: number;
    day?: number;
    formatted?: string;
    month_name?: string;
  };
  meta?: SourceAwareMeta;
}

export interface TrustCapabilitiesResponse {
  surface: string;
  status: string;
  release_id?: string;
  claim_boundary?: ClaimBoundary;
  warnings?: string[];
}

export interface AgentCapabilitiesResponse {
  surface: string;
  status: string;
  tools?: string[];
  claim_boundary?: ClaimBoundary;
}

export interface ProtocolVersionResponse {
  protocol_version: string;
  semver: string;
  claim_boundary: ClaimBoundary;
  status?: string;
}

export interface ImpactCapabilitiesResponse {
  surface: string;
  status: string;
  supported_simulations?: string[];
  claim_boundary?: ClaimBoundary;
}

export interface ApiErrorPayload {
  detail?: string;
  code?: string;
  request_id?: string;
  meta?: SourceAwareMeta;
}
