import { getConsumerFestivalArtKey } from '../consumerAssetRegistry';
import {
  formatProductDate,
  formatProductTime,
  formatProductTimeRange,
} from '../../utils/productDateTime';

export const CONSUMER_FESTIVAL_FILTERS = [
  { value: '', label: 'All observances' },
  { value: 'national', label: 'National' },
  { value: 'newari', label: 'Newari' },
  { value: 'hindu', label: 'Hindu' },
  { value: 'buddhist', label: 'Buddhist' },
  { value: 'regional', label: 'Regional' },
];

export const CONSUMER_BEST_TIME_OPTIONS = [
  { value: 'general', label: 'Everyday rituals' },
  { value: 'creative_focus', label: 'Focused work' },
  { value: 'travel', label: 'Travel' },
  { value: 'vivah', label: 'Wedding' },
  { value: 'griha_pravesh', label: 'Home blessing' },
  { value: 'upanayana', label: 'Study rite' },
];

export function formatDate(value, options = {}, context = {}) {
  return formatProductDate(value, options, {
    language: context.language,
    timeZone: context.timezone,
  });
}

export function formatTime(value, context = {}) {
  return formatProductTime(resolveTimeReferenceValue(value), {
    language: context.language,
    timeZone: context.timezone,
  });
}

export function resolveSunsetReferenceValue(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return resolveTimeReferenceValue(value);
  }
  return resolveTimeReferenceValue(value.local_sunset)
    || resolveTimeReferenceValue(value.sunset)
    || null;
}

export function formatTimeRange(start, end, context = {}) {
  return formatProductTimeRange(resolveTimeReferenceValue(start), resolveTimeReferenceValue(end), {
    language: context.language,
    timeZone: context.timezone,
  });
}

export function formatDateRange(startDate, endDate, context = {}) {
  if (!startDate) return 'Date pending';
  if (!endDate || endDate === startDate) {
    return formatDate(startDate, { month: 'long', day: 'numeric', year: 'numeric' }, context);
  }

  const start = new Date(startDate);
  const end = new Date(endDate);
  if (Number.isNaN(start.valueOf()) || Number.isNaN(end.valueOf())) {
    return `${startDate} - ${endDate}`;
  }

  const sameYear = start.getFullYear() === end.getFullYear();
  const sameMonth = sameYear && start.getMonth() === end.getMonth();

  if (sameMonth) {
    return `${formatDate(startDate, { month: 'long', day: 'numeric' }, context)} - ${formatDate(endDate, { day: 'numeric', year: 'numeric' }, context)}`;
  }

  return `${formatDate(startDate, { month: 'long', day: 'numeric' }, context)} - ${formatDate(endDate, { month: 'long', day: 'numeric', year: 'numeric' }, context)}`;
}

export function startOfSentence(value, fallback) {
  if (!value) return fallback;
  const cleaned = String(value).trim();
  return cleaned || fallback;
}

export function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

export function humanizeToken(value) {
  return String(value || '')
    .replace(/[_:]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

export function resolveTimeReferenceValue(value) {
  if (!value) return null;
  if (typeof value === 'string' || value instanceof Date) return value;
  if (typeof value !== 'object' || Array.isArray(value)) return null;

  for (const key of ['local', 'utc', 'local_time']) {
    const candidate = value[key];
    if (typeof candidate === 'string' && candidate.trim()) {
      return candidate;
    }
  }

  return null;
}

function parseTimeReference(value) {
  const resolved = resolveTimeReferenceValue(value);
  if (!resolved) return null;

  const parsed = new Date(resolved);
  return Number.isNaN(parsed.valueOf()) ? null : parsed;
}

export function timePercent(value, startHour = 6, endHour = 22) {
  if (!value) return 0;
  const parsed = new Date(value);
  if (Number.isNaN(parsed.valueOf())) return 0;
  const hours = parsed.getHours() + (parsed.getMinutes() / 60);
  return clamp(((hours - startHour) / (endHour - startHour)) * 100, 0, 100);
}

export function toneFromBlock(block) {
  if (!block) return 'mixed';
  if (block.class === 'avoid' || (Number(block.score) || 0) <= -25) return 'avoid';
  if (block.class === 'auspicious' || (Number(block.score) || 0) >= 65) return 'strong';
  if ((Number(block.score) || 0) >= 35) return 'good';
  return 'mixed';
}

export function buildSupportingCopy(block, fallback) {
  if (!block) return fallback;
  if (block.rank_explanation) return block.rank_explanation;
  if (block.quality) {
    const quality = humanizeToken(block.quality).toLowerCase();
    if (quality.includes('auspicious')) return 'This window carries a cleaner, more supportive tone.';
    if (quality.includes('neutral')) return 'This window is workable, but not as strong as the lead answer.';
    if (quality.includes('mixed')) return 'Signals are mixed here, so use this only if needed.';
  }
  if (block.class) {
    const blockClass = humanizeToken(block.class).toLowerCase();
    if (blockClass.includes('avoid')) return 'This stretch is better for routine or lower-stakes work.';
    if (blockClass.includes('auspicious')) return 'This window is part of the stronger live ranking.';
  }
  if (Array.isArray(block.reason_codes) && block.reason_codes.length) {
    return block.reason_codes.map((item) => humanizeToken(item)).join(', ');
  }
  return fallback;
}

export function bestTimeWindowLabel(block, state) {
  if (!block?.start) return 'Window pending';
  return formatTimeRange(block.start, block.end, state);
}

export function bestTimeConsumerNote(block, fallback) {
  const tone = toneFromBlock(block);
  if (tone === 'strong') return buildSupportingCopy(block, 'This is the clearest opening in the current timing profile.');
  if (tone === 'good') return buildSupportingCopy(block, 'A reliable backup if you miss the main answer.');
  if (tone === 'avoid') return buildSupportingCopy(block, 'Keep routine or lower-stakes tasks here.');
  return buildSupportingCopy(block, fallback);
}

export function sortedBlocks(payload) {
  return [...(payload?.blocks || [])].sort((left, right) => (Number(right?.score) || 0) - (Number(left?.score) || 0));
}

export function uniqueFestivals(primary = [], secondary = []) {
  const seen = new Set();
  return [...primary, ...secondary].filter((festival) => {
    if (!festival?.id) return false;
    if (seen.has(festival.id)) return false;
    seen.add(festival.id);
    return true;
  });
}

export function normalizeRitualSteps(festival) {
  if (festival?.ritual_sequence?.days?.length) {
    return festival.ritual_sequence.days.flatMap((day, dayIndex) => (
      (day.events || []).map((event, eventIndex) => ({
        id: `${day.name || 'step'}-${eventIndex}`,
        phase: day.name || `Observance ${dayIndex + 1}`,
        title: event.title || day.name || 'Observance step',
        description: event.description || day.significance || 'Part of the observance sequence.',
      }))
    ));
  }

  return [];
}

export function countdownLabel(startDate) {
  if (!startDate) return 'Date pending';

  const target = new Date(`${String(startDate).slice(0, 10)}T00:00:00`);
  if (Number.isNaN(target.valueOf())) return 'Date pending';

  const now = new Date(Date.now());
  const diffDays = Math.floor((target.getTime() - now.getTime()) / 86400000);

  if (diffDays < 0) return 'Observed recently';
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return 'Tomorrow';
  return `${diffDays} days away`;
}

export function sunriseShiftLabel(panchanga) {
  const localSunrise = parseTimeReference(panchanga?.local_sunrise);
  const kathmanduSunrise = parseTimeReference(panchanga?.sunrise);

  if (!localSunrise || !kathmanduSunrise) {
    return 'Shift pending';
  }

  const delta = Math.round((localSunrise.getTime() - kathmanduSunrise.getTime()) / 60000);
  if (delta === 0) return 'Same sunrise rhythm as Kathmandu';
  return `${delta > 0 ? '+' : '-'}${Math.abs(delta)} minutes vs Kathmandu`;
}

export { getConsumerFestivalArtKey };
