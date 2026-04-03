export const GREGORIAN_MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

export const BS_MONTHS = [
  'Baisakh',
  'Jestha',
  'Ashadh',
  'Shrawan',
  'Bhadra',
  'Ashwin',
  'Kartik',
  'Mangsir',
  'Poush',
  'Magh',
  'Falgun',
  'Chaitra',
];

export const CHRONOLOGY_HORIZONS = {
  authoritative: {
    band: 'authoritative',
    label: 'Authoritative window',
    note: 'Parva can ask the live engine for a source-backed answer in this band.',
  },
  estimated: {
    band: 'estimated',
    label: 'Estimated window',
    note: 'Parva can still query the live engine here, but the backend may fall back to estimated conversion.',
  },
  experimental: {
    band: 'experimental',
    label: 'Experimental horizon',
    note: 'Outside the live engine window, the frontend keeps conversion alive with a synthetic projected calendar model.',
  },
  deep_time: {
    band: 'deep_time',
    label: 'Deep time',
    note: 'This query sits far beyond the lived table. Treat it as speculative chronology, not published calendar truth.',
  },
};

const ANCHOR_GREGORIAN = { astronomicalYear: 2026, month: 4, day: 14 };
const ANCHOR_BS = { astronomicalYear: 2083, month: 1, day: 1 };
const BS_CYCLE_ANCHOR_YEAR = 2093;
const BS_CYCLE_TEMPLATES = [
  [31, 31, 32, 32, 31, 30, 30, 29, 30, 29, 30, 30],
  [31, 32, 31, 32, 31, 30, 30, 30, 29, 29, 30, 31],
  [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
];
const ANCHOR_JDN = gregorianToJdn(
  ANCHOR_GREGORIAN.astronomicalYear,
  ANCHOR_GREGORIAN.month,
  ANCHOR_GREGORIAN.day,
);

const OFFICIAL_GREGORIAN_MIN_YEAR = 2013;
const OFFICIAL_GREGORIAN_MAX_YEAR = 2039;
const ESTIMATED_GREGORIAN_MIN_YEAR = 1813;
const ESTIMATED_GREGORIAN_MAX_YEAR = 2239;
const OFFICIAL_BS_MIN_YEAR = 2070;
const OFFICIAL_BS_MAX_YEAR = 2095;
const ESTIMATED_BS_MIN_YEAR = 1870;
const ESTIMATED_BS_MAX_YEAR = 2295;

function modulo(value, divisor) {
  return ((value % divisor) + divisor) % divisor;
}

export function historicalYearToAstronomical(yearMagnitude, era) {
  const parsed = Number(yearMagnitude);
  if (!Number.isInteger(parsed) || parsed < 1) {
    throw new Error('Year must be a whole number greater than 0.');
  }
  if (era === 'BC' || era === 'PRE_BS') {
    return -(parsed - 1);
  }
  return parsed;
}

export function astronomicalYearToHistorical(astronomicalYear, positiveEra = 'AD', negativeEra = 'BC') {
  if (astronomicalYear > 0) {
    return { year: astronomicalYear, era: positiveEra };
  }
  return { year: 1 - astronomicalYear, era: negativeEra };
}

export function isGregorianLeapYear(astronomicalYear) {
  return astronomicalYear % 4 === 0
    && (astronomicalYear % 100 !== 0 || astronomicalYear % 400 === 0);
}

export function daysInGregorianMonth(astronomicalYear, month) {
  if (!Number.isInteger(month) || month < 1 || month > 12) {
    throw new Error('Gregorian month must be between 1 and 12.');
  }

  if (month === 2) {
    return isGregorianLeapYear(astronomicalYear) ? 29 : 28;
  }

  if ([4, 6, 9, 11].includes(month)) {
    return 30;
  }

  return 31;
}

export function gregorianToJdn(astronomicalYear, month, day) {
  const a = Math.floor((14 - month) / 12);
  const y = astronomicalYear + 4800 - a;
  const m = month + (12 * a) - 3;
  return day
    + Math.floor(((153 * m) + 2) / 5)
    + (365 * y)
    + Math.floor(y / 4)
    - Math.floor(y / 100)
    + Math.floor(y / 400)
    - 32045;
}

export function jdnToGregorian(jdn) {
  const a = jdn + 32044;
  const b = Math.floor(((4 * a) + 3) / 146097);
  const c = a - Math.floor((146097 * b) / 4);
  const d = Math.floor(((4 * c) + 3) / 1461);
  const e = c - Math.floor((1461 * d) / 4);
  const m = Math.floor(((5 * e) + 2) / 153);

  const day = e - Math.floor(((153 * m) + 2) / 5) + 1;
  const month = m + 3 - (12 * Math.floor(m / 10));
  const astronomicalYear = (100 * b) + d - 4800 + Math.floor(m / 10);

  return {
    astronomicalYear,
    month,
    day,
    monthName: GREGORIAN_MONTHS[month - 1],
    ...astronomicalYearToHistorical(astronomicalYear, 'AD', 'BC'),
  };
}

export function getProjectedBsMonthPattern(astronomicalYear) {
  return BS_CYCLE_TEMPLATES[modulo(astronomicalYear - BS_CYCLE_ANCHOR_YEAR, BS_CYCLE_TEMPLATES.length)];
}

export function daysInProjectedBsMonth(astronomicalYear, month) {
  if (!Number.isInteger(month) || month < 1 || month > 12) {
    throw new Error('BS month must be between 1 and 12.');
  }
  return getProjectedBsMonthPattern(astronomicalYear)[month - 1];
}

export function daysInProjectedBsYear(astronomicalYear) {
  return getProjectedBsMonthPattern(astronomicalYear).reduce((total, days) => total + days, 0);
}

export function projectedBsToJdn(astronomicalYear, month, day) {
  const monthLength = daysInProjectedBsMonth(astronomicalYear, month);
  if (!Number.isInteger(day) || day < 1 || day > monthLength) {
    throw new Error(`BS day must be between 1 and ${monthLength} for that month.`);
  }

  let dayOffset = 0;
  if (astronomicalYear >= ANCHOR_BS.astronomicalYear) {
    for (let year = ANCHOR_BS.astronomicalYear; year < astronomicalYear; year += 1) {
      dayOffset += daysInProjectedBsYear(year);
    }
  } else {
    for (let year = astronomicalYear; year < ANCHOR_BS.astronomicalYear; year += 1) {
      dayOffset -= daysInProjectedBsYear(year);
    }
  }

  const monthPattern = getProjectedBsMonthPattern(astronomicalYear);
  for (let index = 0; index < month - 1; index += 1) {
    dayOffset += monthPattern[index];
  }
  dayOffset += day - 1;

  return ANCHOR_JDN + dayOffset;
}

export function jdnToProjectedBs(jdn) {
  let offset = jdn - ANCHOR_JDN;
  let astronomicalYear = ANCHOR_BS.astronomicalYear;

  if (offset >= 0) {
    while (offset >= daysInProjectedBsYear(astronomicalYear)) {
      offset -= daysInProjectedBsYear(astronomicalYear);
      astronomicalYear += 1;
    }
  } else {
    while (offset < 0) {
      astronomicalYear -= 1;
      offset += daysInProjectedBsYear(astronomicalYear);
    }
  }

  const monthPattern = getProjectedBsMonthPattern(astronomicalYear);
  let month = 1;
  while (offset >= monthPattern[month - 1]) {
    offset -= monthPattern[month - 1];
    month += 1;
  }

  return {
    astronomicalYear,
    month,
    day: offset + 1,
    monthName: BS_MONTHS[month - 1],
    ...astronomicalYearToHistorical(astronomicalYear, 'BS', 'PRE_BS'),
  };
}

export function projectGregorianToBs({ year, era = 'AD', month, day }) {
  const astronomicalYear = historicalYearToAstronomical(year, era);
  const monthLength = daysInGregorianMonth(astronomicalYear, month);
  if (!Number.isInteger(day) || day < 1 || day > monthLength) {
    throw new Error(`Gregorian day must be between 1 and ${monthLength} for that month.`);
  }

  const jdn = gregorianToJdn(astronomicalYear, month, day);
  return {
    input: {
      calendar: 'gregorian',
      astronomicalYear,
      month,
      day,
      monthName: GREGORIAN_MONTHS[month - 1],
      ...astronomicalYearToHistorical(astronomicalYear, 'AD', 'BC'),
    },
    output: {
      calendar: 'bs',
      ...jdnToProjectedBs(jdn),
    },
    model: 'synthetic_bs_cycle',
  };
}

export function projectBsToGregorian({ year, era = 'BS', month, day }) {
  const astronomicalYear = historicalYearToAstronomical(year, era);
  const jdn = projectedBsToJdn(astronomicalYear, month, day);
  return {
    input: {
      calendar: 'bs',
      astronomicalYear,
      month,
      day,
      monthName: BS_MONTHS[month - 1],
      ...astronomicalYearToHistorical(astronomicalYear, 'BS', 'PRE_BS'),
    },
    output: {
      calendar: 'gregorian',
      ...jdnToGregorian(jdn),
    },
    model: 'synthetic_bs_cycle',
  };
}

export function buildExperimentalConversion(query) {
  if (query.system === 'gregorian') {
    return projectGregorianToBs(query);
  }
  return projectBsToGregorian(query);
}

export function buildHorizonDescriptor(query) {
  const magnitude = Number(query?.year) || 0;
  if (query?.system === 'gregorian' && query?.era === 'AD') {
    if (magnitude >= OFFICIAL_GREGORIAN_MIN_YEAR && magnitude <= OFFICIAL_GREGORIAN_MAX_YEAR) {
      return CHRONOLOGY_HORIZONS.authoritative;
    }
    if (magnitude >= ESTIMATED_GREGORIAN_MIN_YEAR && magnitude <= ESTIMATED_GREGORIAN_MAX_YEAR) {
      return CHRONOLOGY_HORIZONS.estimated;
    }
  }
  if (query?.system === 'bs' && query?.era === 'BS') {
    if (magnitude >= OFFICIAL_BS_MIN_YEAR && magnitude <= OFFICIAL_BS_MAX_YEAR) {
      return CHRONOLOGY_HORIZONS.authoritative;
    }
    if (magnitude >= ESTIMATED_BS_MIN_YEAR && magnitude <= ESTIMATED_BS_MAX_YEAR) {
      return CHRONOLOGY_HORIZONS.estimated;
    }
  }
  if (magnitude <= 20000) {
    return CHRONOLOGY_HORIZONS.experimental;
  }
  return CHRONOLOGY_HORIZONS.deep_time;
}

export function formatHistoricalYear(year, era) {
  return `${new Intl.NumberFormat('en-US').format(year)} ${era === 'PRE_BS' ? 'Pre-BS' : era}`;
}

export function formatGregorianCoordinate(result) {
  return `${result.monthName} ${result.day}, ${formatHistoricalYear(result.year, result.era)}`;
}

export function formatBsCoordinate(result) {
  return `${result.monthName} ${result.day}, ${formatHistoricalYear(result.year, result.era)}`;
}

export function parseGregorianIso(isoValue) {
  const match = String(isoValue || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) {
    throw new Error('The live Gregorian result was not a valid ISO date.');
  }
  const astronomicalYear = Number(match[1]);
  const month = Number(match[2]);
  const day = Number(match[3]);
  return {
    astronomicalYear,
    month,
    day,
    monthName: GREGORIAN_MONTHS[month - 1],
    ...astronomicalYearToHistorical(astronomicalYear, 'AD', 'BC'),
  };
}

export function formatInputSignature(query) {
  if (query.system === 'gregorian') {
    return `${query.month}/${query.day}/${query.year} ${query.era}`;
  }
  return `${query.year} ${query.era} · ${BS_MONTHS[query.month - 1]} ${query.day}`;
}
