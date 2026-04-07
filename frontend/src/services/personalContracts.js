import {
  buildContractError,
  ensureApiEnvelope,
  ensureLocation,
  ensureObject,
  ensureObjectArray,
  ensureOptionalString,
  ensureString,
  ensureTimeReference,
  withContractRequestId,
} from './apiContractCore';

export function normalizePersonalPanchangaEnvelope(envelope) {
  const normalized = ensureApiEnvelope('/personal/panchanga', envelope);
  return withContractRequestId(normalized, () => {
    const data = normalized.data;
    for (const field of ['date', 'location']) {
      if (!(field in data)) {
        throw buildContractError('/personal/panchanga', `Personal panchanga payload must include ${field}.`, data);
      }
    }
    ensureObject(data.location, '/personal/panchanga', 'Personal panchanga location must be an object.');
    for (const field of ['sunrise', 'local_sunrise', 'local_sunset']) {
      if (field in data && data[field] !== null) {
        ensureTimeReference(data[field], '/personal/panchanga', field);
      }
    }
    return normalized;
  });
}

export function normalizePersonalContextEnvelope(envelope) {
  const normalized = ensureApiEnvelope('/personal/context', envelope);
  return withContractRequestId(normalized, () => {
    const data = normalized.data;
    ensureString(data.date, '/personal/context', 'Personal context payload must include a date string.');
    ensureLocation(data.location, '/personal/context');
    for (const field of ['place_title', 'status_line', 'visit_note', 'context_title', 'context_summary', 'daily_inspiration']) {
      ensureString(
        data[field],
        '/personal/context',
        `Personal context payload must include ${field} as a non-empty string.`,
      );
    }
    ensureOptionalString(
      data.temperature_note,
      '/personal/context',
      'Personal context temperature_note must be a non-empty string when present.',
    );
    const reminders = ensureObjectArray(
      data.upcoming_reminders,
      '/personal/context',
      'Personal context upcoming_reminders must be an array of reminder objects.',
    );
    reminders.forEach((item) => {
      ensureString(
        item.title,
        '/personal/context',
        'Personal context reminder.title must be a non-empty string.',
      );
      ensureOptionalString(
        item.date_label,
        '/personal/context',
        'Personal context reminder.date_label must be a non-empty string when present.',
      );
      ensureOptionalString(
        item.status,
        '/personal/context',
        'Personal context reminder.status must be a non-empty string when present.',
      );
    });
    return normalized;
  });
}
