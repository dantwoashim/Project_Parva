export function trustValue(value, fallback = 'Unavailable') {
  if (value === 0) return '0';
  if (value === false) return 'No';
  if (value === true) return 'Yes';
  if (value === undefined || value === null || value === '') return fallback;
  return String(value);
}

export function formatBytes(value) {
  const bytes = Number(value);
  if (!Number.isFinite(bytes) || bytes <= 0) return 'Unavailable';
  if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  if (bytes > 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${bytes} B`;
}

export function formatPercent(value) {
  return `${Number(value || 0).toFixed(2)}%`;
}
