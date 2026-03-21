function parseIsoDate(value) {
  if (typeof value !== 'string') return null;
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return null;

  const year = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  const date = new Date(Date.UTC(year, month - 1, day));

  if (
    Number.isNaN(date.valueOf())
    || date.getUTCFullYear() !== year
    || date.getUTCMonth() !== month - 1
    || date.getUTCDate() !== day
  ) {
    return null;
  }

  return { year, month, day };
}

function formatUtcDate(date) {
  return [
    String(date.getUTCFullYear()).padStart(4, '0'),
    String(date.getUTCMonth() + 1).padStart(2, '0'),
    String(date.getUTCDate()).padStart(2, '0'),
  ].join('-');
}

export function addIsoDays(value, days) {
  const parsed = parseIsoDate(value);
  if (!parsed) return value;
  const date = new Date(Date.UTC(parsed.year, parsed.month - 1, parsed.day + Number(days || 0)));
  return formatUtcDate(date);
}

export function startOfIsoMonth(value) {
  const parsed = parseIsoDate(value);
  if (!parsed) return value;
  return `${String(parsed.year).padStart(4, '0')}-${String(parsed.month).padStart(2, '0')}-01`;
}

export function endOfIsoMonth(value) {
  const parsed = parseIsoDate(value);
  if (!parsed) return value;
  const date = new Date(Date.UTC(parsed.year, parsed.month, 0));
  return formatUtcDate(date);
}

export function addIsoMonths(value, count) {
  const parsed = parseIsoDate(value);
  if (!parsed) return value;
  const date = new Date(Date.UTC(parsed.year, parsed.month - 1 + Number(count || 0), 1));
  return formatUtcDate(date);
}

export function isoDayOfWeek(value) {
  const parsed = parseIsoDate(value);
  if (!parsed) return 0;
  return new Date(Date.UTC(parsed.year, parsed.month - 1, parsed.day)).getUTCDay();
}

export function daysInIsoMonth(value) {
  const parsed = parseIsoDate(value);
  if (!parsed) return 0;
  return new Date(Date.UTC(parsed.year, parsed.month, 0)).getUTCDate();
}
