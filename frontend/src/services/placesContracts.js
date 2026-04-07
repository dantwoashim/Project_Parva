import {
  ensureNumber,
  ensureObject,
  ensureObjectArray,
  ensureString,
} from './apiContractCore';

export function normalizePlaceSearchPayload(payload) {
  const data = ensureObject(payload, '/places/search');
  ensureString(data.query, '/places/search', 'Place search payload must include the submitted query string.');
  const items = ensureObjectArray(
    data.items,
    '/places/search',
    'Place search payload must include an items array.',
  );
  items.forEach((item) => {
    ensureString(item.label, '/places/search', 'Place search item.label must be a non-empty string.');
    ensureNumber(item.latitude, '/places/search', 'Place search item.latitude must be a finite number.');
    ensureNumber(item.longitude, '/places/search', 'Place search item.longitude must be a finite number.');
    ensureString(item.timezone, '/places/search', 'Place search item.timezone must be a non-empty string.');
    ensureString(item.source, '/places/search', 'Place search item.source must be a non-empty string.');
  });
  return data;
}
