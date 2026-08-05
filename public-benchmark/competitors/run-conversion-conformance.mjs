import ClassicPackage from 'nepali-date-converter';
import * as SonillDates from '@sonill/nepali-dates';
import NepaliDateLibrary from 'nepali-date-library';
import RemoteMergeDateConverter from '@remotemerge/nepali-date-converter';

const ClassicNepaliDate = ClassicPackage.default;

function pad(value) {
  return String(value).padStart(2, '0');
}

function isoBsDate(year, month) {
  return `${year}-${pad(month)}-01`;
}

function nextBsMonth(year, month) {
  return month === 12 ? [year + 1, 1] : [year, month + 1];
}

function utcDate(year, month, day) {
  return new Date(Date.UTC(Number(year), Number(month) - 1, Number(day)));
}

function daysBetween(start, end) {
  return Math.round((end.getTime() - start.getTime()) / 86_400_000);
}

const adapters = [
  {
    id: 'nepali-date-converter',
    version: '3.4.0',
    source: 'https://www.npmjs.com/package/nepali-date-converter',
    firstDay(year, month) {
      const value = new ClassicNepaliDate(year, month - 1, 1).getAD();
      return utcDate(value.year, value.month + 1, value.date);
    },
  },
  {
    id: '@sonill/nepali-dates',
    version: '1.0.7',
    source: 'https://www.npmjs.com/package/@sonill/nepali-dates',
    firstDay(year, month) {
      const value = SonillDates.bsToAd(year, month, 1);
      return utcDate(value.year, value.month, value.day);
    },
  },
  {
    id: 'nepali-date-library',
    version: '1.1.15',
    source: 'https://www.npmjs.com/package/nepali-date-library',
    firstDay(year, month) {
      return new Date(`${NepaliDateLibrary.BStoAD(isoBsDate(year, month))}T00:00:00Z`);
    },
  },
  {
    id: '@remotemerge/nepali-date-converter',
    version: '1.2.1',
    source: 'https://www.npmjs.com/package/@remotemerge/nepali-date-converter',
    firstDay(year, month) {
      const value = new RemoteMergeDateConverter(isoBsDate(year, month)).toAd();
      return utcDate(value.year, value.month, value.date);
    },
  },
];

function extractMonthLengths(adapter, startYear = 2078, endYear = 2083) {
  const years = {};
  const errors = [];

  for (let year = startYear; year <= endYear; year += 1) {
    years[String(year)] = [];
    for (let month = 1; month <= 12; month += 1) {
      try {
        const [nextYear, nextMonth] = nextBsMonth(year, month);
        const start = adapter.firstDay(year, month);
        const end = adapter.firstDay(nextYear, nextMonth);
        const days = daysBetween(start, end);
        if (!Number.isInteger(days) || days < 28 || days > 33) {
          throw new Error(`derived month length ${days} is outside 28-33 days`);
        }
        years[String(year)].push(days);
      } catch (error) {
        years[String(year)].push(null);
        errors.push({
          year,
          month,
          message: error instanceof Error ? error.message : String(error),
        });
      }
    }
  }

  return {
    id: adapter.id,
    version: adapter.version,
    source: adapter.source,
    method: 'difference_between_public_bs_to_ad_month_start_conversions',
    years,
    errors,
  };
}

const report = {
  schema_version: '1.0',
  range: { start_bs_year: 2078, end_bs_year: 2083, month_cases: 72 },
  implementations: adapters.map((adapter) => extractMonthLengths(adapter)),
};

process.stdout.write(`${JSON.stringify(report)}\n`);
