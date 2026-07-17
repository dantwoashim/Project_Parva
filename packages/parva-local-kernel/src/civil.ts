import { stableStringify } from './canonicalize.js';
import { sha256Hex } from './hash.js';

type BsYearData = {
  startAd: string;
  months: number[];
};

type HolidayRecord = {
  holiday_id: string;
  label: string;
  source_status: string;
};

const DAY_MS = 24 * 60 * 60 * 1000;

const BS_YEARS: Record<number, BsYearData> = {
  2082: {
    startAd: '2025-04-14',
    months: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
  },
  2083: {
    startAd: '2026-04-14',
    months: [31, 31, 32, 31, 31, 31, 30, 29, 30, 29, 30, 30],
  },
};

const FIXED_HOLIDAYS: Record<string, HolidayRecord> = {
  '01-01': {
    holiday_id: 'bs-new-year',
    label: 'Nepali New Year',
    source_status: 'public_fixed_date_observance',
  },
  '10-01': {
    holiday_id: 'maghe-sankranti',
    label: 'Maghe Sankranti',
    source_status: 'public_fixed_date_observance',
  },
};

const MONTH_NAMES = [
  'Baishakh',
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

function utcDate(value: string): Date {
  return new Date(`${value}T00:00:00.000Z`);
}

function isoDate(date: Date): string {
  return date.toISOString().slice(0, 10);
}

function addDays(value: string, days: number): string {
  return isoDate(new Date(utcDate(value).getTime() + days * DAY_MS));
}

function diffDays(left: string, right: string): number {
  return Math.floor((utcDate(left).getTime() - utcDate(right).getTime()) / DAY_MS);
}

function dateKey(year: number, month: number, day: number): string {
  return `${year.toString().padStart(4, '0')}-${month.toString().padStart(2, '0')}-${day
    .toString()
    .padStart(2, '0')}`;
}

function bsYearData(year: number): BsYearData {
  const data = BS_YEARS[year];
  if (!data) {
    throw new Error(`unsupported_bs_year:${year}`);
  }
  return data;
}

function monthLength(year: number, month: number): number {
  if (month < 1 || month > 12) {
    throw new Error(`invalid_bs_month:${month}`);
  }
  return bsYearData(year).months[month - 1];
}

function bsToAd(year: number, month: number, day: number): string {
  const data = bsYearData(year);
  const maxDay = monthLength(year, month);
  if (day < 1 || day > maxDay) {
    throw new Error(`invalid_bs_day:${day}`);
  }
  const offset = data.months.slice(0, month - 1).reduce((sum, value) => sum + value, 0) + day - 1;
  return addDays(data.startAd, offset);
}

function adToBs(adDate: string): { year: number; month: number; day: number } {
  for (const [yearText, data] of Object.entries(BS_YEARS)) {
    const year = Number(yearText);
    const totalDays = data.months.reduce((sum, value) => sum + value, 0);
    const offset = diffDays(adDate, data.startAd);
    if (offset < 0 || offset >= totalDays) {
      continue;
    }
    let remaining = offset;
    for (let month = 1; month <= 12; month += 1) {
      const length = data.months[month - 1];
      if (remaining < length) {
        return { year, month, day: remaining + 1 };
      }
      remaining -= length;
    }
  }
  throw new Error(`unsupported_ad_date:${adDate}`);
}

function validateBsDate(year: number, month: number, day: number): Record<string, unknown> {
  try {
    const maxDay = monthLength(year, month);
    const valid = day >= 1 && day <= maxDay;
    return {
      bs_date: dateKey(year, month, day),
      day,
      max_day: maxDay,
      month,
      reason: valid ? 'valid' : `day must be between 1 and ${maxDay}`,
      valid,
      year,
    };
  } catch (error) {
    return {
      bs_date: dateKey(year, month, day),
      day,
      max_day: null,
      month,
      reason: error instanceof Error ? error.message.replace(/^unsupported_bs_year:/, 'BS year ') : 'invalid BS date',
      valid: false,
      year,
    };
  }
}

function holidayIndexPayload(): Record<string, unknown> {
  return {
    holidays: Object.entries(FIXED_HOLIDAYS)
      .sort(([left], [right]) => left.localeCompare(right))
      .map(([key, value]) => `${key}:${value.holiday_id}`),
    source_set: 'public_fixed_date_corpus',
  };
}

async function holidayResult(
  year: number,
  month: number,
  day: number,
  profileId: string,
): Promise<Record<string, unknown>> {
  const key = `${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
  const holiday = FIXED_HOLIDAYS[key] ?? null;
  const claimIndexHash = `sha256:${await sha256Hex(stableStringify(holidayIndexPayload()))}`;
  return {
    bs_date: dateKey(year, month, day),
    holiday,
    is_holiday: holiday !== null,
    membership_key: key,
    membership_proof: {
      claim_index_hash: claimIndexHash,
      proof_type: holiday ? 'membership' : 'non_membership',
    },
    profile_id: profileId,
    source_set: 'public_fixed_date_corpus',
  };
}

async function workingDayResult(
  year: number,
  month: number,
  day: number,
  profileId: string,
  decisionIntent: string,
): Promise<Record<string, unknown>> {
  const adDate = bsToAd(year, month, day);
  const holiday = (await holidayResult(year, month, day, 'nepal_public_general')).holiday as HolidayRecord | null;
  const weekday = utcDate(adDate).getUTCDay();
  const isSaturday = weekday === 6;
  const isWorkingDay = !isSaturday && holiday === null;
  const reasonCodes: string[] = [];
  if (isSaturday) {
    reasonCodes.push('WEEKEND', 'SATURDAY_NON_WORKING');
  } else {
    reasonCodes.push('WEEKDAY');
  }
  reasonCodes.push(holiday ? 'PUBLIC_HOLIDAY_MATCH' : 'NO_MATCHING_PUBLIC_HOLIDAY');
  return {
    ad_date: adDate,
    bs_date: dateKey(year, month, day),
    decision_intent: decisionIntent,
    holiday,
    is_business_day: isWorkingDay,
    is_working_day: isWorkingDay,
    profile_id: profileId,
    reason_codes: reasonCodes,
    requires_human_review: false,
  };
}

function fiscalYearResult(bsYear: number): Record<string, unknown> {
  const startAd = bsToAd(bsYear, 4, 1);
  const endDay = monthLength(bsYear + 1, 3);
  const endAd = bsToAd(bsYear + 1, 3, endDay);
  return {
    basis: 'Nepal fiscal year: Shrawan 1 to Ashadh end',
    end: {
      ad: endAd,
      bs: dateKey(bsYear + 1, 3, endDay),
    },
    fiscal_year: `${bsYear}/${String(bsYear + 1).slice(-2)}`,
    start: {
      ad: startAd,
      bs: dateKey(bsYear, 4, 1),
    },
  };
}

function validateBsMonthsResult(result: Record<string, unknown>, mode: string): void {
  const months = result.months;
  if (Array.isArray(months)) {
    let total = 0;
    for (const item of months as Array<Record<string, unknown>>) {
      const days = Number(item.days);
      const month = Number(item.month);
      if (!Number.isFinite(days) || days < 28 || days > 33) {
        throw new Error('bs_month_length_invalid');
      }
      if (MONTH_NAMES[month - 1] && item.name !== MONTH_NAMES[month - 1]) {
        throw new Error('bs_month_name_mismatch');
      }
      if (typeof item.start_ad === 'string' && typeof item.end_ad === 'string') {
        const span = diffDays(item.end_ad, item.start_ad) + 1;
        if (span !== days) {
          throw new Error('bs_month_ad_span_mismatch');
        }
      }
      total += days;
    }
    if (Number(result.total_days) !== total) {
      throw new Error('bs_month_total_mismatch');
    }
  }

  if (mode === 'static_lookup' && result.selected_method !== 'static_lookup') {
    throw new Error('bs_month_static_mode_mismatch');
  }
  if (mode === 'compare') {
    const branchSet = result.branch_set as { branches?: unknown } | null | undefined;
    if (!branchSet || !Array.isArray(branchSet.branches)) {
      throw new Error('bs_month_compare_branch_set_missing');
    }
  }
}

function inputNumbers(query: Record<string, unknown>): { year: number; month: number; day: number } {
  const input = query.input as Record<string, unknown>;
  return { year: Number(input.year), month: Number(input.month), day: Number(input.day) };
}

export async function replayCivilResult(operation: string, query: unknown): Promise<Record<string, unknown> | null> {
  if (!query || typeof query !== 'object') {
    return null;
  }
  const typed = query as Record<string, unknown>;
  const input = typed.input as Record<string, unknown> | undefined;
  if (!input) {
    return null;
  }

  if (operation === 'convert_bs_to_ad') {
    const { year, month, day } = inputNumbers(typed);
    return { ad_date: bsToAd(year, month, day) };
  }
  if (operation === 'ad_to_bs') {
    const adDate = String(input.ad_date);
    const bs = adToBs(adDate);
    return { bs_date: dateKey(bs.year, bs.month, bs.day), day: bs.day, month: bs.month, year: bs.year };
  }
  if (operation === 'validate_bs_date') {
    const { year, month, day } = inputNumbers(typed);
    return validateBsDate(year, month, day);
  }
  if (operation === 'holiday') {
    const { year, month, day } = inputNumbers(typed);
    return holidayResult(year, month, day, String(input.profile_id ?? 'nepal_public_general'));
  }
  if (operation === 'working_day') {
    const { year, month, day } = inputNumbers(typed);
    return workingDayResult(
      year,
      month,
      day,
      String(input.profile_id ?? 'nepal_private_company_default'),
      String(input.decision_intent ?? 'general'),
    );
  }
  if (operation === 'fiscal_year') {
    return fiscalYearResult(Number(input.bs_year));
  }
  return null;
}

export function verifyBsMonthReplay(operation: string, query: unknown, result: unknown): void {
  if (operation !== 'bs_months') {
    return;
  }
  if (!query || typeof query !== 'object' || !result || typeof result !== 'object') {
    throw new Error('bs_month_replay_payload_missing');
  }
  const input = (query as Record<string, Record<string, unknown>>).input;
  const mode = String(input?.mode ?? 'canonical');
  validateBsMonthsResult(result as Record<string, unknown>, mode);
}
