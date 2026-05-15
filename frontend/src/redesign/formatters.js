export function readableCategory(value) {
  return String(value || 'observance')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function titleCase(value) {
  return String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

export function formatDateTime(value) {
  if (!value) return 'Unknown';
  try {
    return new Intl.DateTimeFormat('en', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(new Date(value));
  } catch {
    return String(value).slice(0, 10);
  }
}

export function formatIsoDate(value, options = {}) {
  if (!value) return 'Date pending';
  try {
    return new Intl.DateTimeFormat('en', {
      weekday: options.weekday,
      month: options.month || 'short',
      day: 'numeric',
      year: options.year || 'numeric',
      timeZone: options.timeZone,
    }).format(new Date(`${String(value).slice(0, 10)}T00:00:00`));
  } catch {
    return String(value);
  }
}

export function formatTimeReference(value) {
  if (!value) return 'Awaiting calculation';
  const candidate = typeof value === 'object' ? value.local_time || value.local || value.utc : value;
  if (!candidate) return 'Awaiting calculation';
  const localIsoTime = String(candidate).match(/^\d{4}-\d{2}-\d{2}T(\d{2}):(\d{2})/);
  if (localIsoTime) {
    return formatClockParts(localIsoTime[1], localIsoTime[2]);
  }
  if (/^\d{2}:\d{2}/.test(candidate)) return candidate.slice(0, 5);
  try {
    return new Intl.DateTimeFormat('en', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(candidate));
  } catch {
    return String(candidate);
  }
}

export function formatTimeRange(start, end) {
  return `${formatTimeReference(start)} - ${formatTimeReference(end)}`;
}

function formatClockParts(hourText, minuteText) {
  const hour = Number(hourText);
  const minute = Number(minuteText);
  if (!Number.isFinite(hour) || !Number.isFinite(minute)) {
    return `${hourText}:${minuteText}`;
  }
  const period = hour >= 12 ? 'PM' : 'AM';
  const hour12 = hour % 12 || 12;
  return `${String(hour12).padStart(2, '0')}:${String(minute).padStart(2, '0')} ${period}`;
}

export function formatBsDate(bs = {}) {
  if (bs.formatted) return bs.formatted;
  if (bs.year && bs.month_name && bs.day) return `${bs.year} ${bs.month_name} ${bs.day}`;
  if (bs.year && bs.month && bs.day) return `${bs.year}-${String(bs.month).padStart(2, '0')}-${String(bs.day).padStart(2, '0')} BS`;
  return 'BS date pending';
}

export function formatCoordinates(location = {}) {
  const lat = Number(location.latitude);
  const lon = Number(location.longitude);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return 'Coordinates pending';
  return `${lat.toFixed(4)} deg, ${lon.toFixed(4)} deg`;
}

export function placeLabelFromLocation(location = {}) {
  if (location.label || location.place_title || location.name) {
    return location.label || location.place_title || location.name;
  }
  const lat = Number(location.latitude);
  const lon = Number(location.longitude);
  if (Number.isFinite(lat) && Number.isFinite(lon) && Math.abs(lat - 27.7172) < 0.03 && Math.abs(lon - 85.3240) < 0.03) {
    return 'Kathmandu, Nepal';
  }
  return `${formatCoordinates(location)}`;
}

export function humanMethodLabel(value, fallback = 'Verified calculation') {
  const normalized = String(value || '').toLowerCase();
  if (!normalized) return fallback;
  if (normalized.includes('temporal_compass')) return 'Parva daily model';
  if (normalized.includes('rule_ranked_muhurta')) return 'Ranked muhurta model';
  if (normalized.includes('swiss_moshier') || normalized.includes('swiss') || normalized.includes('pyswisseph')) return 'Swiss Ephemeris';
  if (normalized.includes('ephemeris_udaya')) return 'Sunrise-based panchanga';
  if (normalized.includes('np-mainstream')) return 'Nepal mainstream rules';
  if (normalized.includes('official')) return 'Official calendar source';
  if (normalized.includes('astronomical')) return 'Astronomical calculation';
  return readableCategory(value);
}

export function supportReference(value) {
  if (typeof value !== 'string' || !value.trim()) return 'Calculation evidence';
  return 'View evidence';
}

export function addDaysToIsoDate(value, offset, fallbackIso) {
  const date = new Date(`${String(value || fallbackIso).slice(0, 10)}T00:00:00`);
  if (Number.isNaN(date.getTime())) return fallbackIso;
  date.setDate(date.getDate() + offset);
  return date.toISOString().slice(0, 10);
}

export function sourceFreshness(meta = {}, fallback = 'Checked on demand') {
  const safeMeta = meta || {};
  const candidate = safeMeta.generated_at || safeMeta.created_at || safeMeta.updated_at || safeMeta.requested_at || safeMeta.as_of;
  if (!candidate) return fallback;
  return `Checked ${formatDateTime(candidate)}`;
}

export function scoreTone(scoreOrClass) {
  const normalized = String(scoreOrClass || '').toLowerCase();
  if (normalized.includes('avoid') || normalized.includes('inauspicious')) return 'bad';
  if (normalized.includes('neutral') || normalized.includes('mixed')) return 'warm';
  const score = Number(scoreOrClass);
  if (Number.isFinite(score)) {
    if (score < 25) return 'bad';
    if (score < 55) return 'warm';
  }
  return 'good';
}

export function normalizeMuhurtaWindow(block = {}, index = 0) {
  const score = Number(block.score ?? block.top_score ?? 0);
  return {
    id: String(block.id ?? block.index ?? block.name ?? index),
    name: block.name || block.best_window?.name || 'Time window',
    time: block.start && block.end ? formatTimeRange(block.start, block.end) : 'Window pending',
    start: block.start,
    end: block.end,
    score: Number.isFinite(score) ? Math.max(0, Math.min(100, Math.round(score))) : 0,
    kind: readableCategory(block.class || block.quality || block.tone || 'timing'),
    type: scoreTone(block.class || score),
    left: Math.max(0, Math.min(90, index * 8)),
    width: 8,
    reasonCodes: block.reason_codes || [],
  };
}
