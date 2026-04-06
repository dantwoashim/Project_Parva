import {
  BS_MONTHS,
  GREGORIAN_MONTHS,
  buildExperimentalConversion,
  buildHorizonDescriptor,
  daysInGregorianMonth,
  daysInProjectedBsMonth,
  formatBsCoordinate,
  formatGregorianCoordinate,
  formatHistoricalYear,
  formatInputSignature,
  gregorianToJdn,
  historicalYearToAstronomical,
  parseGregorianIso,
  projectedBsToJdn,
} from '../../lib/chronologyProjection';

export { BS_MONTHS, GREGORIAN_MONTHS, formatHistoricalYear, formatInputSignature };

export const DEFAULT_GREGORIAN_ERA = 'AD';
export const DEFAULT_BS_ERA = 'BS';
export const HORIZON_ORDER = ['authoritative', 'estimated', 'experimental', 'deep_time'];

export function buildDefaultQuery(dateIso) {
  const match = String(dateIso || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) {
    return {
      system: 'gregorian',
      era: DEFAULT_GREGORIAN_ERA,
      year: '2026',
      month: 4,
      day: 14,
    };
  }

  return {
    system: 'gregorian',
    era: DEFAULT_GREGORIAN_ERA,
    year: String(Number(match[1])),
    month: Number(match[2]),
    day: Number(match[3]),
  };
}

export function apiGregorianIso(query) {
  return `${String(query.year).padStart(4, '0')}-${String(query.month).padStart(2, '0')}-${String(query.day).padStart(2, '0')}`;
}

export function parseQuery(query) {
  const normalizedYear = String(query.year || '').replace(/,/g, '').trim();
  if (!normalizedYear) {
    throw new Error('Enter a year before running the conversion.');
  }

  const year = Number(normalizedYear);
  if (!Number.isInteger(year) || year < 1) {
    throw new Error('Year must be a whole number greater than 0.');
  }

  const month = Number(query.month);
  const day = Number(query.day);
  if (!Number.isInteger(month) || month < 1 || month > 12) {
    throw new Error('Month must be between 1 and 12.');
  }
  if (!Number.isInteger(day) || day < 1) {
    throw new Error('Day must be a whole number greater than 0.');
  }

  if (query.system === 'gregorian') {
    return {
      system: 'gregorian',
      era: query.era === 'BC' ? 'BC' : 'AD',
      year,
      month,
      day,
    };
  }

  return {
    system: 'bs',
    era: query.era === 'PRE_BS' ? 'PRE_BS' : 'BS',
    year,
    month,
    day,
  };
}

export function dayLimitForQuery(query) {
  try {
    const parsed = parseQuery({ ...query, day: 1 });
    const astronomicalYear = historicalYearToAstronomical(parsed.year, parsed.era);
    if (parsed.system === 'gregorian') {
      return daysInGregorianMonth(astronomicalYear, parsed.month);
    }
    return daysInProjectedBsMonth(astronomicalYear, parsed.month);
  } catch {
    return query.system === 'gregorian' ? 31 : 32;
  }
}

export function formatOutputCoordinate(result) {
  if (!result) return '';
  return result.calendar === 'gregorian'
    ? formatGregorianCoordinate(result)
    : formatBsCoordinate(result);
}

export function buildPresetCatalog(todayQuery) {
  return [
    {
      id: 'today',
      label: 'Parva today',
      detail: 'Current live date from the app context.',
      query: todayQuery,
    },
    {
      id: 'bc10000',
      label: '10,000 BC',
      detail: 'Deep prehistory, projected only.',
      query: { system: 'gregorian', era: 'BC', year: '10000', month: 1, day: 1 },
    },
    {
      id: 'ad10000',
      label: '10,000 AD',
      detail: 'Far future, projected horizon.',
      query: { system: 'gregorian', era: 'AD', year: '10000', month: 1, day: 1 },
    },
    {
      id: 'bs2083',
      label: '2083 BS',
      detail: 'The live BS new year anchor.',
      query: { system: 'bs', era: 'BS', year: '2083', month: 1, day: 1 },
    },
    {
      id: 'bs10000',
      label: '10,000 BS',
      detail: 'Long-range BS projection.',
      query: { system: 'bs', era: 'BS', year: '10000', month: 1, day: 1 },
    },
  ];
}

export async function resolveAnchoredConversion(query, calendarAPI) {
  const horizon = buildHorizonDescriptor(query);
  const liveCapable = horizon.band === 'authoritative' || horizon.band === 'estimated';
  if (!liveCapable) {
    return null;
  }

  if (query.system === 'gregorian' && query.era === 'AD') {
    const iso = apiGregorianIso(query);
    const [convert, compare] = await Promise.all([
      calendarAPI.convertGregorian(iso),
      calendarAPI.compareGregorian(iso).catch(() => null),
    ]);
    return {
      system: 'gregorian_to_bs',
      confidence: convert?.bikram_sambat?.confidence || 'computed',
      sourceRange: convert?.bikram_sambat?.source_range || null,
      estimatedErrorDays: convert?.bikram_sambat?.estimated_error_days || null,
      comparison: compare,
      output: {
        calendar: 'bs',
        year: convert.bikram_sambat.year,
        era: 'BS',
        month: convert.bikram_sambat.month,
        day: convert.bikram_sambat.day,
        monthName: convert.bikram_sambat.month_name,
      },
    };
  }

  if (query.system === 'bs' && query.era === 'BS') {
    const convert = await calendarAPI.convertBsToGregorian({
      year: query.year,
      month: query.month,
      day: query.day,
    });
    return {
      system: 'bs_to_gregorian',
      confidence: convert?.bs?.confidence || 'computed',
      sourceRange: convert?.bs?.source_range || null,
      estimatedErrorDays: convert?.bs?.estimated_error_days || null,
      comparison: null,
      output: {
        calendar: 'gregorian',
        ...parseGregorianIso(convert.gregorian),
      },
    };
  }

  return null;
}

export function computeDriftDays(experimental, anchored) {
  if (!experimental?.output || !anchored?.output) return null;

  if (anchored.output.calendar === 'gregorian') {
    const experimentalYear = historicalYearToAstronomical(experimental.output.year, experimental.output.era);
    const anchoredYear = historicalYearToAstronomical(anchored.output.year, anchored.output.era);
    return Math.abs(
      gregorianToJdn(experimentalYear, experimental.output.month, experimental.output.day)
      - gregorianToJdn(anchoredYear, anchored.output.month, anchored.output.day),
    );
  }

  const experimentalYear = historicalYearToAstronomical(experimental.output.year, experimental.output.era);
  const anchoredYear = historicalYearToAstronomical(anchored.output.year, anchored.output.era);
  return Math.abs(
    projectedBsToJdn(experimentalYear, experimental.output.month, experimental.output.day)
    - projectedBsToJdn(anchoredYear, anchored.output.month, anchored.output.day),
  );
}

export function engineLabel(confidence) {
  if (confidence === 'official' || confidence === 'exact') return 'Live authoritative engine';
  if (confidence === 'estimated') return 'Live estimated engine';
  return 'Experimental horizon engine';
}

export function systemCopy(system) {
  return system === 'gregorian' ? 'Gregorian' : 'Bikram Sambat';
}

export function modeSummary(result) {
  if (!result) return 'Awaiting lock';
  return result.anchored ? 'Blended live + projected mode' : 'Projected deep-time mode';
}

export function supportPosture(horizon) {
  if (!horizon) return 'Unknown';
  if (horizon.band === 'authoritative') return 'Source-backed live window';
  if (horizon.band === 'estimated') return 'Estimated live window';
  if (horizon.band === 'experimental') return 'Frontend projection window';
  return 'Deep-time speculative window';
}

export function buildTimeLabResult(query, anchored) {
  const experimental = buildExperimentalConversion(query);
  return {
    query,
    horizon: buildHorizonDescriptor(query),
    experimental,
    anchored,
    driftDays: computeDriftDays(experimental, anchored),
  };
}
