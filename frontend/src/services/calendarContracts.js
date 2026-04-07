import {
  buildContractError,
  ensureApiEnvelope,
  ensureLocation,
  ensureNumber,
  ensureObject,
  ensureObjectArray,
  ensureOptionalObject,
  ensureOptionalString,
  ensureString,
  ensureTimeRange,
  ensureTimeReference,
  withContractRequestId,
} from './apiContractCore';

export function normalizeCalendarTodayPayload(payload) {
  const normalized = ensureObject(payload, '/calendar/today');
  for (const field of ['gregorian', 'bikram_sambat', 'tithi']) {
    if (!(field in normalized)) {
      throw buildContractError('/calendar/today', `Missing required field: ${field}`, normalized);
    }
  }
  return normalized;
}

export function normalizeTemporalCompassEnvelope(envelope) {
  const normalized = ensureApiEnvelope('/temporal/compass', envelope);
  return withContractRequestId(normalized, () => {
    const data = normalized.data;
    ensureString(data.date, '/temporal/compass', 'Temporal compass payload must include a date string.');
    ensureLocation(data.location, '/temporal/compass');

    const bsDate = ensureObject(
      data.bikram_sambat,
      '/temporal/compass',
      'Temporal compass payload must include a bikram_sambat object.',
    );
    for (const field of ['year', 'month', 'day']) {
      ensureNumber(
        bsDate[field],
        '/temporal/compass',
        `Temporal compass bikram_sambat.${field} must be a finite number.`,
      );
    }
    ensureString(
      bsDate.month_name,
      '/temporal/compass',
      'Temporal compass bikram_sambat.month_name must be a non-empty string.',
    );

    const primaryReadout = ensureObject(
      data.primary_readout,
      '/temporal/compass',
      'Temporal compass payload must include a primary_readout object.',
    );
    ensureString(
      primaryReadout.tithi_name,
      '/temporal/compass',
      'Temporal compass primary_readout.tithi_name must be a non-empty string.',
    );
    ensureString(
      primaryReadout.paksha,
      '/temporal/compass',
      'Temporal compass primary_readout.paksha must be a non-empty string.',
    );

    const horizon = ensureObject(
      data.horizon,
      '/temporal/compass',
      'Temporal compass payload must include a horizon object.',
    );
    ensureTimeReference(horizon.sunrise, '/temporal/compass', 'horizon.sunrise');
    if (horizon.sunset !== undefined && horizon.sunset !== null) {
      ensureTimeReference(horizon.sunset, '/temporal/compass', 'horizon.sunset');
    }
    if (horizon.current_muhurta !== undefined && horizon.current_muhurta !== null) {
      const currentMuhurta = ensureObject(
        horizon.current_muhurta,
        '/temporal/compass',
        'Temporal compass horizon.current_muhurta must be an object.',
      );
      ensureOptionalString(
        currentMuhurta.name,
        '/temporal/compass',
        'Temporal compass horizon.current_muhurta.name must be a non-empty string when present.',
      );
      ensureTimeReference(currentMuhurta.start, '/temporal/compass', 'horizon.current_muhurta.start');
      ensureTimeReference(currentMuhurta.end, '/temporal/compass', 'horizon.current_muhurta.end');
    }
    if (horizon.rahu_kalam !== undefined && horizon.rahu_kalam !== null) {
      ensureTimeRange(horizon.rahu_kalam, '/temporal/compass', 'horizon.rahu_kalam');
    }

    const today = ensureObject(
      data.today,
      '/temporal/compass',
      'Temporal compass payload must include a today object.',
    );
    ensureObjectArray(
      today.festivals,
      '/temporal/compass',
      'Temporal compass today.festivals must be an array of festival objects.',
    );
    ensureNumber(
      today.count,
      '/temporal/compass',
      'Temporal compass today.count must be a finite number.',
    );

    const signals = ensureObject(
      data.signals,
      '/temporal/compass',
      'Temporal compass payload must include a signals object.',
    );
    for (const field of ['nakshatra', 'yoga', 'karana', 'vaara']) {
      ensureOptionalObject(
        signals[field],
        '/temporal/compass',
        `Temporal compass signals.${field} must be an object when present.`,
      );
    }

    ensureString(
      data.quality_band_filter,
      '/temporal/compass',
      'Temporal compass payload must include a quality_band_filter string.',
    );
    const engine = ensureObject(
      data.engine,
      '/temporal/compass',
      'Temporal compass payload must include an engine object.',
    );
    ensureString(
      engine.method,
      '/temporal/compass',
      'Temporal compass engine.method must be a non-empty string.',
    );
    ensureString(
      engine.method_profile,
      '/temporal/compass',
      'Temporal compass engine.method_profile must be a non-empty string.',
    );
    return normalized;
  });
}
