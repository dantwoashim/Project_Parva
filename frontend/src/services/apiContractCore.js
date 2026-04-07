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

export function withContractRequestId(value, callback) {
  const previousRequestId = activeContractRequestId;
  activeContractRequestId = extractRequestId(value) || previousRequestId;
  try {
    return callback();
  } finally {
    activeContractRequestId = previousRequestId;
  }
}

export function buildContractError(endpoint, detail, payload) {
  const error = new Error(`Unexpected response shape for ${endpoint}`);
  error.name = 'ParvaApiError';
  error.status = 502;
  error.detail = detail;
  error.requestId = extractRequestId(payload) || activeContractRequestId || null;
  error.payload = payload;
  return error;
}

export function ensureObject(value, endpoint, detail = 'Upstream response did not match the expected JSON object contract.') {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value;
  }
  throw buildContractError(endpoint, detail, value);
}

export function ensureOptionalObject(value, endpoint, detail) {
  if (value === undefined || value === null) {
    return value;
  }
  return ensureObject(value, endpoint, detail);
}

export function ensureOptionalArray(value, endpoint, detail) {
  if (value === undefined || value === null) {
    return value;
  }
  if (Array.isArray(value)) {
    return value;
  }
  throw buildContractError(endpoint, detail, value);
}

export function ensureArray(value, endpoint, detail) {
  if (Array.isArray(value)) {
    return value;
  }
  throw buildContractError(endpoint, detail, value);
}

export function ensureString(value, endpoint, detail) {
  if (typeof value === 'string' && value.trim()) {
    return value;
  }
  throw buildContractError(endpoint, detail, value);
}

export function ensureOptionalString(value, endpoint, detail) {
  if (value === undefined || value === null) {
    return value;
  }
  return ensureString(value, endpoint, detail);
}

export function ensureNumber(value, endpoint, detail) {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return value;
  }
  throw buildContractError(endpoint, detail, value);
}

export function ensureObjectArray(value, endpoint, detail) {
  const normalized = ensureArray(value, endpoint, detail);
  normalized.forEach((item) => ensureObject(item, endpoint, detail));
  return normalized;
}

export function ensureLocation(value, endpoint) {
  const location = ensureObject(value, endpoint, 'Response location must be an object.');
  ensureNumber(location.latitude, endpoint, 'Response location.latitude must be a finite number.');
  ensureNumber(location.longitude, endpoint, 'Response location.longitude must be a finite number.');
  ensureString(location.timezone, endpoint, 'Response location.timezone must be a non-empty string.');
  return location;
}

export function ensureTimeRange(value, endpoint, fieldName) {
  const range = ensureObject(
    value,
    endpoint,
    `${fieldName} must be an object with start and end time references.`,
  );
  ensureTimeReference(range.start, endpoint, `${fieldName}.start`);
  ensureTimeReference(range.end, endpoint, `${fieldName}.end`);
  return range;
}

export function ensureTimeReference(value, endpoint, fieldName) {
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
