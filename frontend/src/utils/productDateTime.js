import { resolveUiLocale } from '../i18n/locale';

function parseProductDateValue(value) {
  if (!value) return null;
  if (value instanceof Date) {
    return Number.isNaN(value.valueOf()) ? null : value;
  }

  if (typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return new Date(`${value}T12:00:00.000Z`);
  }

  const parsed = new Date(value);
  return Number.isNaN(parsed.valueOf()) ? null : parsed;
}

function parseTimeOnlyValue(value) {
  if (typeof value !== 'string') return null;
  const match = value.trim().match(/^(\d{1,2}):(\d{2})(?::(\d{2}))?$/);
  if (!match) return null;

  const hour = Number(match[1]);
  const minute = Number(match[2]);
  const second = Number(match[3] || '0');
  if (
    !Number.isInteger(hour)
    || !Number.isInteger(minute)
    || !Number.isInteger(second)
    || hour < 0
    || hour > 23
    || minute < 0
    || minute > 59
    || second < 0
    || second > 59
  ) {
    return null;
  }

  return new Date(Date.UTC(1970, 0, 1, hour, minute, second));
}

function buildFormatterOptions(options = {}, context = {}) {
  return {
    ...options,
    timeZone: context.timeZone || 'Asia/Kathmandu',
  };
}

export function formatProductDate(value, options = {}, context = {}) {
  const parsed = parseProductDateValue(value);
  if (!parsed) return value ? String(value) : '';

  const locale = resolveUiLocale(context.language);

  try {
    return new Intl.DateTimeFormat(locale, buildFormatterOptions(options, context)).format(parsed);
  } catch {
    return new Intl.DateTimeFormat(locale, options).format(parsed);
  }
}

export function formatProductTime(value, context = {}, options = {}) {
  const timeOnlyDate = parseTimeOnlyValue(value);
  const locale = resolveUiLocale(context.language);
  if (timeOnlyDate) {
    try {
      return new Intl.DateTimeFormat(locale, {
        hour: 'numeric',
        minute: '2-digit',
        ...options,
        timeZone: 'UTC',
      }).format(timeOnlyDate);
    } catch {
      return new Intl.DateTimeFormat(locale, {
        hour: 'numeric',
        minute: '2-digit',
        ...options,
      }).format(timeOnlyDate);
    }
  }

  const parsed = parseProductDateValue(value);
  if (!parsed) return '';
  const formatterOptions = buildFormatterOptions({
    hour: 'numeric',
    minute: '2-digit',
    ...options,
  }, context);

  try {
    return new Intl.DateTimeFormat(locale, formatterOptions).format(parsed);
  } catch {
    return new Intl.DateTimeFormat(locale, {
      hour: 'numeric',
      minute: '2-digit',
      ...options,
    }).format(parsed);
  }
}

export function formatProductTimeRange(start, end, context = {}, options = {}) {
  const formattedStart = formatProductTime(start, context, options);
  const formattedEnd = formatProductTime(end, context, options);

  if (!formattedStart && !formattedEnd) return '';
  if (!formattedEnd) return formattedStart;
  return `${formattedStart} - ${formattedEnd}`;
}
