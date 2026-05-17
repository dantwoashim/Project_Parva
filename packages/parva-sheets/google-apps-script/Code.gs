const DEFAULT_PARVA_API_BASE_URL = 'https://api.prabinghimire1.com.np';

function getParvaApiBaseUrl_() {
  const configured = PropertiesService.getScriptProperties().getProperty('PARVA_API_BASE_URL');
  return (configured || DEFAULT_PARVA_API_BASE_URL).replace(/\/+$/, '');
}

function parvaFetch_(path, options) {
  const response = UrlFetchApp.fetch(getParvaApiBaseUrl_() + path, {
    muteHttpExceptions: true,
    headers: { Accept: 'application/json' },
    ...options,
  });
  const status = response.getResponseCode();
  const payload = JSON.parse(response.getContentText() || '{}');
  if (status >= 400) {
    return {
      answer: 'review_required',
      source_tier: 'source_unavailable',
      confidence: 'unsupported',
      review_required: true,
      claim_boundary: 'not_authority',
      not_authority: true,
      error: payload.detail || payload.error || `HTTP ${status}`,
    };
  }
  return payload;
}

function parvaAnswer_(payload, key) {
  if (payload[key] !== undefined) return payload[key];
  if (payload.answer !== undefined) return payload.answer;
  if (payload.gregorian !== undefined) return payload.gregorian;
  if (payload.ad_date !== undefined) return payload.ad_date;
  if (payload.is_holiday !== undefined) return payload.is_holiday;
  if (payload.working_day !== undefined) return payload.working_day;
  if (payload.fiscal_year !== undefined) return payload.fiscal_year;
  return JSON.stringify(payload);
}

function parvaSheetResult_(payload, key, includeMetadata) {
  const answer = parvaAnswer_(payload, key);
  if (!includeMetadata) return answer;
  return [
    ['answer', 'source_tier', 'confidence', 'review_required', 'claim_boundary', 'not_authority'],
    [
      answer,
      payload.source_tier || payload.source_status || payload.provenance?.source_status || 'source_metadata_available',
      payload.confidence || payload.provenance?.confidence || 'confidence_metadata_available',
      payload.review_required === true || payload.human_review_required === true,
      payload.claim_boundary || payload.policy?.claim_boundary || 'not_authority',
      payload.not_authority !== false,
    ],
  ];
}

function parseBsDate_(bsDate) {
  const parts = String(bsDate).split('-').map((part) => Number(part));
  if (parts.length !== 3 || parts.some((part) => !Number.isInteger(part))) {
    throw new Error('BS date must use YYYY-MM-DD.');
  }
  return { year: parts[0], month: parts[1], day: parts[2] };
}

function BS_TO_AD(bsDate, includeMetadata) {
  const body = JSON.stringify(parseBsDate_(bsDate));
  const payload = parvaFetch_('/v3/api/calendar/bs-to-gregorian', {
    method: 'post',
    contentType: 'application/json',
    payload: body,
  });
  return parvaSheetResult_(payload, 'gregorian', includeMetadata === true);
}

function AD_TO_BS(adDate, includeMetadata) {
  const payload = parvaFetch_(`/v3/api/calendar/convert?date=${encodeURIComponent(adDate)}`);
  const bs = payload.bikram_sambat;
  const value = bs ? `${bs.year}-${String(bs.month).padStart(2, '0')}-${String(bs.day).padStart(2, '0')}` : undefined;
  return parvaSheetResult_({ ...payload, answer: value }, 'answer', includeMetadata === true);
}

function IS_NEPALI_HOLIDAY(bsDate, includeMetadata) {
  const payload = parvaFetch_('/v3/api/compliance/evaluate-date', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({
      profile_id: 'nepal_private_company_default',
      bs_date: bsDate,
      decision_intent: 'general',
    }),
  });
  return parvaSheetResult_({ ...payload, answer: payload.is_holiday === true }, 'answer', includeMetadata === true);
}

function NEPALI_FISCAL_YEAR(bsDate, includeMetadata) {
  const year = String(bsDate).split('-')[0];
  const payload = parvaFetch_(`/v3/api/enterprise/fiscal-year/${encodeURIComponent(year)}`);
  return parvaSheetResult_(payload, 'fiscal_year', includeMetadata === true);
}

function WORKING_DAY_NP(bsDate, includeMetadata) {
  const payload = parvaFetch_('/v3/api/compliance/evaluate-date', {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify({
      profile_id: 'nepal_private_company_default',
      bs_date: bsDate,
      decision_intent: 'working_day',
    }),
  });
  return parvaSheetResult_({ ...payload, answer: payload.working_day !== false }, 'answer', includeMetadata === true);
}

