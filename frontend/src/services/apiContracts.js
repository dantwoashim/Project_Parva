let activeContractRequestId = null;

function normalizeRequestId(value) {
  if (typeof value === 'string' && value.trim()) {
    return value.trim();
  }
  return null;
}

function extractRequestId(value) {
  return normalizeRequestId(value?.requestId)
    || normalizeRequestId(value?.request_id)
    || normalizeRequestId(value?.meta?.request_id)
    || normalizeRequestId(value?.meta?.requestId)
    || null;
}

function withContractRequestId(value, callback) {
  const previousRequestId = activeContractRequestId;
  activeContractRequestId = extractRequestId(value) || previousRequestId;
  try {
    return callback();
  } finally {
    activeContractRequestId = previousRequestId;
  }
}

function buildContractError(endpoint, detail, payload) {
  const error = new Error(`Unexpected response shape for ${endpoint}`);
  error.name = 'ParvaApiError';
  error.status = 502;
  error.detail = detail;
  error.requestId = extractRequestId(payload) || activeContractRequestId || null;
  error.payload = payload;
  return error;
}

function ensureObject(value, endpoint, detail = 'Upstream response did not match the expected JSON object contract.') {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value;
  }
  throw buildContractError(endpoint, detail, value);
}

function ensureOptionalObject(value, endpoint, detail) {
  if (value === undefined || value === null) {
    return value;
  }
  return ensureObject(value, endpoint, detail);
}

function ensureOptionalArray(value, endpoint, detail) {
  if (value === undefined || value === null) {
    return value;
  }
  if (Array.isArray(value)) {
    return value;
  }
  throw buildContractError(endpoint, detail, value);
}

function ensureArray(value, endpoint, detail) {
  if (Array.isArray(value)) {
    return value;
  }
  throw buildContractError(endpoint, detail, value);
}

function ensureString(value, endpoint, detail) {
  if (typeof value === 'string' && value.trim()) {
    return value;
  }
  throw buildContractError(endpoint, detail, value);
}

function ensureOptionalString(value, endpoint, detail) {
  if (value === undefined || value === null) {
    return value;
  }
  return ensureString(value, endpoint, detail);
}

function ensureNumber(value, endpoint, detail) {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  throw buildContractError(endpoint, detail, value);
}

function ensureObjectArray(value, endpoint, detail) {
  const normalized = ensureArray(value, endpoint, detail);
  normalized.forEach((item) => ensureObject(item, endpoint, detail));
  return normalized;
}

function ensureLocation(value, endpoint) {
  const location = ensureObject(value, endpoint, 'Response location must be an object.');
  ensureNumber(location.latitude, endpoint, 'Response location.latitude must be a finite number.');
  ensureNumber(location.longitude, endpoint, 'Response location.longitude must be a finite number.');
  ensureString(location.timezone, endpoint, 'Response location.timezone must be a non-empty string.');
  return location;
}

function ensureTimeRange(value, endpoint, fieldName) {
  const range = ensureObject(
    value,
    endpoint,
    `${fieldName} must be an object with start and end time references.`,
  );
  ensureTimeReference(range.start, endpoint, `${fieldName}.start`);
  ensureTimeReference(range.end, endpoint, `${fieldName}.end`);
  return range;
}

function ensureTimeReference(value, endpoint, fieldName) {
  if (typeof value === 'string') {
    return value;
  }
  const candidate = ensureObject(
    value,
    endpoint,
    `${fieldName} must be a string or an object with local/utc/local_time fields.`,
  );
  const hasSupportedField = ['local', 'utc', 'local_time'].some((key) => (
    typeof candidate[key] === 'string' && candidate[key].trim()
  ));
  if (!hasSupportedField) {
    throw buildContractError(
      endpoint,
      `${fieldName} must include at least one of local, utc, or local_time.`,
      candidate,
    );
  }
  return candidate;
}

export function ensureApiEnvelope(endpoint, envelope) {
  const normalized = ensureObject(envelope, endpoint);
  if (!('data' in normalized)) {
    throw buildContractError(endpoint, 'Envelope data must be present.', normalized);
  }
  const data = normalized.data;
  const meta = ensureObject(normalized.meta, endpoint, 'Envelope meta must be a JSON object.');
  return {
    ...normalized,
    data,
    meta,
  };
}

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

export function normalizeKundaliGraphEnvelope(envelope) {
  const normalized = ensureApiEnvelope('/kundali/graph', envelope);
  return withContractRequestId(normalized, () => {
    const data = normalized.data;
    ensureString(data.datetime, '/kundali/graph', 'Kundali graph payload must include a datetime string.');
    ensureLocation(data.location, '/kundali/graph');
    ensureOptionalObject(data.lagna, '/kundali/graph', 'Kundali graph lagna must be an object when present.');

    const layout = ensureObject(
      data.layout,
      '/kundali/graph',
      'Kundali graph payload must include a layout object.',
    );
    ensureString(
      layout.viewbox,
      '/kundali/graph',
      'Kundali graph layout.viewbox must be a non-empty string.',
    );

    const houseNodes = ensureObjectArray(
      layout.house_nodes,
      '/kundali/graph',
      'Kundali graph layout.house_nodes must be an array of house nodes.',
    );
    if (!houseNodes.length) {
      throw buildContractError(
        '/kundali/graph',
        'Kundali graph layout.house_nodes must contain at least one house node.',
        layout.house_nodes,
      );
    }
    houseNodes.forEach((node) => {
      ensureString(node.id, '/kundali/graph', 'Kundali graph house node id must be a non-empty string.');
      ensureNumber(node.x, '/kundali/graph', 'Kundali graph house node x must be a finite number.');
      ensureNumber(node.y, '/kundali/graph', 'Kundali graph house node y must be a finite number.');
    });

    const grahaNodes = ensureObjectArray(
      layout.graha_nodes,
      '/kundali/graph',
      'Kundali graph layout.graha_nodes must be an array of graha nodes.',
    );
    grahaNodes.forEach((node) => {
      ensureString(node.id, '/kundali/graph', 'Kundali graph graha node id must be a non-empty string.');
      ensureNumber(node.x, '/kundali/graph', 'Kundali graph graha node x must be a finite number.');
      ensureNumber(node.y, '/kundali/graph', 'Kundali graph graha node y must be a finite number.');
    });

    const aspectEdges = ensureObjectArray(
      layout.aspect_edges,
      '/kundali/graph',
      'Kundali graph layout.aspect_edges must be an array of aspect edges.',
    );
    aspectEdges.forEach((edge) => {
      ensureString(edge.source, '/kundali/graph', 'Kundali graph aspect edge source must be a non-empty string.');
      ensureString(edge.target, '/kundali/graph', 'Kundali graph aspect edge target must be a non-empty string.');
    });

    const insights = ensureObjectArray(
      data.insight_blocks,
      '/kundali/graph',
      'Kundali graph insight_blocks must be an array of insight objects.',
    );
    insights.forEach((item) => {
      ensureString(item.id, '/kundali/graph', 'Kundali graph insight block id must be a non-empty string.');
      ensureString(item.title, '/kundali/graph', 'Kundali graph insight block title must be a non-empty string.');
      ensureString(item.summary, '/kundali/graph', 'Kundali graph insight block summary must be a non-empty string.');
    });
    return normalized;
  });
}
