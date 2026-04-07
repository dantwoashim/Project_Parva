import {
  buildContractError,
  ensureApiEnvelope,
  ensureObject,
  ensureOptionalArray,
  ensureOptionalObject,
  withContractRequestId,
} from './apiContractCore';

export function normalizeFestivalTimelineEnvelope(envelope) {
  const normalized = ensureApiEnvelope('/festivals/timeline', envelope);
  return withContractRequestId(normalized, () => {
    if (!Array.isArray(normalized.data.groups)) {
      throw buildContractError('/festivals/timeline', 'Festival timeline payload must include a groups array.', normalized.data);
    }
    if ('facets' in normalized.data && normalized.data.facets !== undefined) {
      ensureObject(normalized.data.facets, '/festivals/timeline', 'Festival timeline facets must be an object.');
    }
    return normalized;
  });
}

export function normalizeFestivalDetailEnvelope(envelope) {
  const normalized = ensureApiEnvelope('/festivals/:id', envelope);
  return withContractRequestId(normalized, () => {
    const data = ensureObject(normalized.data, '/festivals/:id');
    if (!data.festival) {
      throw buildContractError('/festivals/:id', 'Festival detail payload must include a festival object.', normalized.data);
    }
    ensureObject(data.festival, '/festivals/:id', 'Festival detail payload must include a festival object.');
    ensureOptionalObject(data.dates, '/festivals/:id', 'Festival detail dates must be an object when present.');
    ensureOptionalArray(data.nearby_festivals, '/festivals/:id', 'Festival detail nearby_festivals must be an array when present.');
    ensureOptionalObject(data.completeness, '/festivals/:id', 'Festival detail completeness must be an object when present.');
    return normalized;
  });
}
