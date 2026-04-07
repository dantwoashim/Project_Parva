import {
  ensureApiEnvelope,
  ensureLocation,
  ensureNumber,
  ensureObject,
  ensureObjectArray,
  ensureOptionalArray,
  ensureOptionalObject,
  ensureOptionalString,
  ensureString,
  ensureTimeRange,
  ensureTimeReference,
  withContractRequestId,
} from './apiContractCore';

export function normalizeMuhurtaHeatmapEnvelope(envelope) {
  const normalized = ensureApiEnvelope('/muhurta/heatmap', envelope);
  return withContractRequestId(normalized, () => {
    const data = normalized.data;
    ensureString(data.date, '/muhurta/heatmap', 'Muhurta heatmap payload must include a date string.');
    ensureLocation(data.location, '/muhurta/heatmap');
    ensureString(data.type, '/muhurta/heatmap', 'Muhurta heatmap payload must include a type string.');
    ensureString(
      data.assumption_set_id,
      '/muhurta/heatmap',
      'Muhurta heatmap payload must include an assumption_set_id string.',
    );
    ensureTimeReference(data.sunrise, '/muhurta/heatmap', 'sunrise');
    ensureTimeReference(data.sunset, '/muhurta/heatmap', 'sunset');
    ensureTimeRange(data.rahu_kalam, '/muhurta/heatmap', 'rahu_kalam');
    ensureOptionalObject(
      data.ranking_profile,
      '/muhurta/heatmap',
      'Muhurta heatmap ranking_profile must be an object when present.',
    );
    ensureOptionalObject(
      data.tara_bala,
      '/muhurta/heatmap',
      'Muhurta heatmap tara_bala must be an object when present.',
    );
    if (data.best_window !== undefined && data.best_window !== null) {
      const bestWindow = ensureObject(
        data.best_window,
        '/muhurta/heatmap',
        'Muhurta heatmap best_window must be an object when present.',
      );
      ensureTimeReference(bestWindow.start, '/muhurta/heatmap', 'best_window.start');
      ensureTimeReference(bestWindow.end, '/muhurta/heatmap', 'best_window.end');
    }

    const blocks = ensureObjectArray(
      data.blocks,
      '/muhurta/heatmap',
      'Muhurta heatmap payload must include a blocks array.',
    );
    blocks.forEach((block) => {
      ensureNumber(block.index, '/muhurta/heatmap', 'Muhurta heatmap block.index must be a finite number.');
      ensureTimeReference(block.start, '/muhurta/heatmap', 'blocks[].start');
      ensureTimeReference(block.end, '/muhurta/heatmap', 'blocks[].end');
      ensureString(block.class, '/muhurta/heatmap', 'Muhurta heatmap block.class must be a non-empty string.');
      ensureOptionalArray(
        block.reason_codes,
        '/muhurta/heatmap',
        'Muhurta heatmap block.reason_codes must be an array when present.',
      );
    });
    return normalized;
  });
}

export function normalizeMuhurtaCalendarPayload(payload) {
  const data = ensureObject(payload, '/muhurta/calendar');
  ensureString(data.from, '/muhurta/calendar', 'Muhurta calendar payload must include a from date string.');
  ensureString(data.to, '/muhurta/calendar', 'Muhurta calendar payload must include a to date string.');
  ensureLocation(data.location, '/muhurta/calendar');
  ensureString(data.type, '/muhurta/calendar', 'Muhurta calendar payload must include a type string.');
  ensureString(
    data.assumption_set_id,
    '/muhurta/calendar',
    'Muhurta calendar payload must include an assumption_set_id string.',
  );
  const days = ensureObjectArray(
    data.days,
    '/muhurta/calendar',
    'Muhurta calendar payload must include a days array.',
  );
  days.forEach((day) => {
    ensureString(day.date, '/muhurta/calendar', 'Muhurta calendar day.date must be a non-empty string.');
    ensureOptionalString(day.tone, '/muhurta/calendar', 'Muhurta calendar day.tone must be a string when present.');
    ensureNumber(day.window_count, '/muhurta/calendar', 'Muhurta calendar day.window_count must be a finite number.');
    if (day.best_window !== undefined && day.best_window !== null) {
      const bestWindow = ensureObject(
        day.best_window,
        '/muhurta/calendar',
        'Muhurta calendar day.best_window must be an object when present.',
      );
      ensureOptionalString(bestWindow.name, '/muhurta/calendar', 'Muhurta calendar day.best_window.name must be a string when present.');
      if (bestWindow.start !== undefined && bestWindow.start !== null) {
        ensureTimeReference(bestWindow.start, '/muhurta/calendar', 'day.best_window.start');
      }
      if (bestWindow.end !== undefined && bestWindow.end !== null) {
        ensureTimeReference(bestWindow.end, '/muhurta/calendar', 'day.best_window.end');
      }
      if (bestWindow.reason_codes !== undefined && bestWindow.reason_codes !== null) {
        ensureOptionalArray(bestWindow.reason_codes, '/muhurta/calendar', 'Muhurta calendar day.best_window.reason_codes must be an array when present.');
      }
    }
  });
  return data;
}
