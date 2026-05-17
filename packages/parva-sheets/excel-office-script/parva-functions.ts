type ParvaMetadata = {
  answer: string | boolean | number | null;
  source_tier: string;
  confidence: string;
  review_required: boolean;
  claim_boundary: string;
  not_authority: boolean;
};

const DEFAULT_PARVA_API_BASE_URL = 'https://api.prabinghimire1.com.np';

async function parvaFetch(path: string, init: RequestInit = {}, baseUrl = DEFAULT_PARVA_API_BASE_URL): Promise<Record<string, any>> {
  const response = await fetch(`${baseUrl.replace(/\/+$/, '')}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      ...(init.body ? { 'Content-Type': 'application/json' } : {}),
      ...(init.headers || {}),
    },
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    return {
      answer: 'review_required',
      source_tier: 'source_unavailable',
      confidence: 'unsupported',
      review_required: true,
      claim_boundary: 'not_authority',
      not_authority: true,
      error: payload.detail || payload.error || `HTTP ${response.status}`,
    };
  }
  return payload;
}

function metadata(payload: Record<string, any>, answer: ParvaMetadata['answer']): ParvaMetadata {
  return {
    answer,
    source_tier: payload.source_tier || payload.source_status || payload.provenance?.source_status || 'source_metadata_available',
    confidence: payload.confidence || payload.provenance?.confidence || 'confidence_metadata_available',
    review_required: payload.review_required === true || payload.human_review_required === true,
    claim_boundary: payload.claim_boundary || payload.policy?.claim_boundary || 'not_authority',
    not_authority: payload.not_authority !== false,
  };
}

function parseBsDate(bsDate: string): { year: number; month: number; day: number } {
  const [year, month, day] = bsDate.split('-').map((part) => Number(part));
  if (![year, month, day].every((part) => Number.isInteger(part))) {
    throw new Error('BS date must use YYYY-MM-DD.');
  }
  return { year, month, day };
}

export async function BS_TO_AD(bsDate: string, baseUrl?: string): Promise<ParvaMetadata> {
  const payload = await parvaFetch('/v3/api/calendar/bs-to-gregorian', {
    method: 'POST',
    body: JSON.stringify(parseBsDate(bsDate)),
  }, baseUrl);
  return metadata(payload, payload.gregorian || payload.ad_date || payload.answer || null);
}

export async function AD_TO_BS(adDate: string, baseUrl?: string): Promise<ParvaMetadata> {
  const payload = await parvaFetch(`/v3/api/calendar/convert?date=${encodeURIComponent(adDate)}`, {}, baseUrl);
  const bs = payload.bikram_sambat;
  const answer = bs ? `${bs.year}-${String(bs.month).padStart(2, '0')}-${String(bs.day).padStart(2, '0')}` : null;
  return metadata(payload, answer);
}

export async function IS_NEPALI_HOLIDAY(bsDate: string, baseUrl?: string): Promise<ParvaMetadata> {
  const payload = await parvaFetch('/v3/api/compliance/evaluate-date', {
    method: 'POST',
    body: JSON.stringify({
      profile_id: 'nepal_private_company_default',
      bs_date: bsDate,
      decision_intent: 'general',
    }),
  }, baseUrl);
  return metadata(payload, payload.is_holiday === true);
}

export async function NEPALI_FISCAL_YEAR(bsDate: string, baseUrl?: string): Promise<ParvaMetadata> {
  const year = bsDate.split('-')[0];
  const payload = await parvaFetch(`/v3/api/enterprise/fiscal-year/${encodeURIComponent(year)}`, {}, baseUrl);
  return metadata(payload, payload.fiscal_year || null);
}

export async function WORKING_DAY_NP(bsDate: string, baseUrl?: string): Promise<ParvaMetadata> {
  const payload = await parvaFetch('/v3/api/compliance/evaluate-date', {
    method: 'POST',
    body: JSON.stringify({
      profile_id: 'nepal_private_company_default',
      bs_date: bsDate,
      decision_intent: 'working_day',
    }),
  }, baseUrl);
  return metadata(payload, payload.working_day !== false);
}

