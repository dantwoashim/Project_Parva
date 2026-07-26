/* eslint-disable react-refresh/only-export-components */
import {
  useEffect,
  useRef,
  useState,
  todayIso,
  apiHref,
  categoryVisualMeta,
  defaultFestivalFilters,
  festivalVisualMeta,
  sourceDots,
  readableCategory,
} from '../ExperienceCommon.jsx';

export function FestivalIllustration({ art }) {
  if (art === 'diya') {
    return (
      <svg viewBox="0 0 120 120" role="img" aria-label="Diya lamp illustration">
        <path className="festival-svg-fill" d="M22 70c11 21 65 21 76 0-9 8-67 8-76 0Z" />
        <path d="M22 70c11 21 65 21 76 0M28 70c11 8 53 8 64 0" />
        <path d="M59 62c-8-13 5-25 8-36 15 19 6 32-8 36Z" />
        <path d="M43 86h34M35 94h50" />
      </svg>
    );
  }

  if (art === 'buddha') {
    return (
      <svg viewBox="0 0 120 120" role="img" aria-label="Buddha lotus illustration">
        <circle className="festival-svg-fill" cx="60" cy="46" r="18" />
        <path d="M43 46c0-12 7-23 17-23s17 11 17 23" />
        <path d="M47 54c5 8 21 8 26 0" />
        <path d="M60 64v16" />
        <path d="M28 82c14-18 28-16 32 4 4-20 18-22 32-4" />
        <path d="M20 93c18 9 62 9 80 0" />
      </svg>
    );
  }

  if (art === 'sun') {
    return (
      <svg viewBox="0 0 120 120" role="img" aria-label="Sun and river illustration">
        <circle className="festival-svg-fill" cx="60" cy="44" r="19" />
        <path d="M60 14v12M60 62v12M30 44H18M102 44H90M39 23l-8-8M81 23l8-8M39 65l-8 8M81 65l8 8" />
        <path d="M19 87c12-10 22-10 34 0s22 10 34 0 18-8 24-2" />
        <path d="M24 100c12-8 20-8 32 0s22 8 34 0" />
      </svg>
    );
  }

  if (art === 'holi') {
    return (
      <svg viewBox="0 0 120 120" role="img" aria-label="Holi color bowl illustration">
        <path className="festival-svg-fill" d="M28 72c5 20 59 20 64 0H28Z" />
        <path d="M28 72c5 20 59 20 64 0H28Z" />
        <path d="M39 61c8-12 36-12 44 0" />
        <path d="M35 31l11 11M84 29l-10 13M62 18v17M24 45l14 5M96 45l-14 5" />
        <circle cx="47" cy="50" r="4" /><circle cx="61" cy="45" r="4" /><circle cx="75" cy="51" r="4" />
      </svg>
    );
  }

  if (art === 'leaf') {
    return (
      <svg viewBox="0 0 120 120" role="img" aria-label="Fasting leaf illustration">
        <path className="festival-svg-fill" d="M33 70c16-35 46-42 64-34-2 34-25 55-58 50" />
        <path d="M33 70c16-35 46-42 64-34-2 34-25 55-58 50" />
        <path d="M33 70c19-3 38-13 56-31" />
        <path d="M38 86c-10 4-17 11-20 21" />
        <path d="M55 59l-2-15M67 51l7-15M48 72l-14-5M64 69l15 6" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 120 120" role="img" aria-label="Durga flower illustration">
      <path className="festival-svg-fill" d="M60 20c10 15 10 28 0 40-10-12-10-25 0-40Z" />
      <path d="M60 20c10 15 10 28 0 40-10-12-10-25 0-40Z" />
      <path d="M27 48c18-6 31-2 39 12-15 5-28 1-39-12Z" />
      <path d="M93 48c-18-6-31-2-39 12 15 5 28 1 39-12Z" />
      <path d="M34 88c10-17 23-24 39-20-7 17-20 24-39 20Z" />
      <path d="M86 88c-10-17-23-24-39-20 7 17 20 24 39 20Z" />
      <circle cx="60" cy="62" r="9" />
    </svg>
  );
}

export function FestivalArtwork({ festival, compact = false, priority = false }) {
  const visual = resolveFestivalVisual(festival);
  const image = festivalImageSrc(festival);
  const fallbackImage = festivalFallbackImageSrc(festival, image);
  const artworkRef = useRef(null);
  const [shouldLoadImage, setShouldLoadImage] = useState(
    () => priority || typeof IntersectionObserver === 'undefined',
  );
  const [imageStatus, setImageStatus] = useState({ primary: '', fallback: false, failed: false, loadedSrc: '' });
  const activeStatus = imageStatus.primary === image ? imageStatus : null;
  const currentImage = shouldLoadImage
    ? activeStatus?.failed
      ? ''
      : activeStatus?.fallback
        ? fallbackImage
        : image
    : '';
  const imageLoaded = Boolean(currentImage && activeStatus?.loadedSrc === currentImage);

  useEffect(() => {
    if (shouldLoadImage || !image || !artworkRef.current) return undefined;

    const observer = new IntersectionObserver((entries) => {
      if (!entries.some((entry) => entry.isIntersecting)) return;
      setShouldLoadImage(true);
      observer.disconnect();
    }, { rootMargin: '240px 0px' });

    observer.observe(artworkRef.current);
    return () => observer.disconnect();
  }, [image, shouldLoadImage]);

  return (
    <span
      ref={artworkRef}
      className={`festival-art festival-art--${visual.art} ${imageLoaded ? 'has-image' : ''} ${compact ? 'is-compact' : ''}`}
      aria-hidden="true"
    >
      <span className="festival-art__halo" />
      {currentImage ? (
        <img
          src={currentImage}
          alt=""
          decoding="async"
          fetchPriority={priority ? 'high' : 'auto'}
          loading={priority ? 'eager' : 'lazy'}
          onLoad={() => setImageStatus({ primary: image, fallback: currentImage === fallbackImage, failed: false, loadedSrc: currentImage })}
          onError={() => {
            if (fallbackImage && currentImage !== fallbackImage) {
              setImageStatus({ primary: image, fallback: true, failed: false, loadedSrc: '' });
              return;
            }
            setImageStatus({ primary: image, fallback: false, failed: true, loadedSrc: '' });
          }}
        />
      ) : null}
      <span className="festival-art__glyph"><FestivalIllustration art={visual.art} /></span>
      <span className="festival-art__line one" />
      <span className="festival-art__line two" />
    </span>
  );
}

export function QualityDots({ value }) {
  const activeDots = Math.max(1, Math.round(value / 20));

  return (
    <span className="quality-dots" aria-label={`${value}% confidence`}>
      {sourceDots.slice(0, 5).map((dot) => (
        <i key={dot} className={dot <= activeDots ? 'is-active' : ''} />
      ))}
    </span>
  );
}

export function resolveFestivalVisual(festival = {}) {
  const id = String(festival.id || '').toLowerCase();
  const category = String(festival.category || festival.kind || '').toLowerCase();
  return festivalVisualMeta[id] || categoryVisualMeta[category] || { tone: 'orange', art: 'durga', icon: '✣' };
}

export function festivalImageSrc(festival = {}) {
  if (Array.isArray(festival.images) && festival.images[0]) return normalizeFestivalImagePath(festival.images[0]);
  if (festival.image) return normalizeFestivalImagePath(festival.image);
  if (festival.id) return `/festival-images/${festival.id}.webp`;
  return '';
}

export function festivalFallbackImageSrc(festival = {}, primary = '') {
  if (!festival.id) return '';
  const id = String(festival.id);
  const primaryString = String(primary || '');
  if (!primaryString.includes(`/festival-images/${id}.webp`)) return '';
  return `/festival-images/${id}.svg`;
}

export function normalizeFestivalImagePath(src = '') {
  return String(src || '').replace(/^\/festival-images\/([^/]+)\.png$/i, '/festival-images/$1.webp');
}

export function addDaysIso(baseIso, days) {
  const date = new Date(`${baseIso}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

export function formatFestivalDate(value, options = {}) {
  if (!value) return 'Date pending';
  try {
    return new Intl.DateTimeFormat('en', {
      month: options.month || 'short',
      day: 'numeric',
      year: options.year || 'numeric',
    }).format(new Date(`${value}T00:00:00`));
  } catch {
    return value;
  }
}

export function formatFestivalDateRange(startDate, endDate) {
  if (!startDate) return 'Date pending';
  if (!endDate || endDate === startDate) return formatFestivalDate(startDate);
  return `${formatFestivalDate(startDate, { year: undefined })} - ${formatFestivalDate(endDate)}`;
}

export function formatBsDateRange(item = {}) {
  const start = item.bs_start?.formatted;
  const end = item.bs_end?.formatted;
  if (!start) return 'BS date pending';
  if (!end || end === start) return start;
  return `${start} - ${end}`;
}

export function daysUntil(startDate) {
  if (!startDate) return null;
  const start = new Date(`${startDate}T00:00:00`);
  const today = new Date(`${todayIso('Asia/Kathmandu')}T00:00:00`);
  const diff = Math.ceil((start.getTime() - today.getTime()) / 86400000);
  return Number.isFinite(diff) ? diff : null;
}

export function countdownText(startDate) {
  const days = daysUntil(startDate);
  if (days === null) return 'Date pending';
  if (days < 0) return 'Recently observed';
  if (days === 0) return 'Today';
  if (days === 1) return 'Tomorrow';
  return `In ${days} days`;
}

export function readableReason(value) {
  const normalized = String(value || '')
    .replace(/^quality[:_-]/i, '')
    .replace(/[:_-]+/g, ' ')
    .trim();
  return readableCategory(normalized || 'Recommended');
}

export function sourceStrength(item = {}) {
  const band = String(item.quality_band || '').toLowerCase();
  const status = String(item.rule_status || '').toLowerCase();
  if (band === 'computed' || status === 'active') {
    return { label: 'Computed', tone: 'high', score: 88 };
  }
  if (band === 'provisional') {
    return { label: 'Provisional', tone: 'medium', score: 68 };
  }
  if (band === 'inventory') {
    return { label: 'Inventory', tone: 'low', score: 42 };
  }
  return { label: readableCategory(band || status || 'Documented'), tone: 'medium', score: 62 };
}

export function normalizeFestivalTimelineRows(groups = []) {
  return groups.flatMap((group) => (group.items || []).map((item) => ({
    ...item,
    monthKey: group.month_key || item.start_date?.slice(0, 7) || '',
    monthLabel: group.month_label || item.start_date?.slice(0, 7) || 'Upcoming',
    displayName: item.display_name || item.name || 'Festival',
    bsLabel: formatBsDateRange(item),
    adLabel: formatFestivalDateRange(item.start_date, item.end_date),
    durationLabel: item.duration_days && item.duration_days > 1 ? `${item.duration_days} days` : 'Single day',
    countdownLabel: countdownText(item.start_date),
    categoryLabel: readableCategory(item.category),
    summary: item.summary || item.ritual_preview || 'Festival details are available from the public Parva calendar.',
    regions: item.regional_focus || [],
    visual: resolveFestivalVisual(item),
    source: sourceStrength(item),
  })));
}

export function groupFestivalRowsByMonth(rows = []) {
  return rows.reduce((groups, festival) => {
    const key = festival.monthKey || monthFilterValue(festival);
    const label = festival.monthLabel || monthFilterValue(festival);
    const existing = groups.find((group) => group.key === key);
    if (existing) {
      existing.items.push(festival);
    } else {
      groups.push({ key, label, items: [festival] });
    }
    return groups;
  }, []);
}

export function festivalDateRail(item = {}) {
  const bs = item.bs_start || {};
  const day = bs.day ? String(bs.day).padStart(2, '0') : item.start_date ? item.start_date.slice(8, 10) : '--';
  const month = bs.month_name ? String(bs.month_name).slice(0, 3) : item.monthLabel ? String(item.monthLabel).slice(0, 3) : 'Date';
  return { day, month };
}

export function monthFilterValue(item = {}) {
  return item.bs_start?.month_name || item.monthLabel || 'Other';
}

export function activeFestivalFilterCount(filters, search) {
  return [
    filters.month !== defaultFestivalFilters.month,
    filters.category !== defaultFestivalFilters.category,
    filters.region !== defaultFestivalFilters.region,
    filters.qualityBand !== defaultFestivalFilters.qualityBand,
    filters.sort !== defaultFestivalFilters.sort,
    Boolean(search.trim()),
  ].filter(Boolean).length;
}

export function normalizeFacetOptions(options = [], fallback = []) {
  const normalized = options.map((item) => ({
    value: item.value || item.label,
    label: item.label || readableCategory(item.value),
    count: item.count,
  })).filter((item) => item.value && item.label);
  return normalized.length ? normalized : fallback;
}

export function compactParagraph(value, fallback = '') {
  const text = String(value || fallback || '').replace(/\s+/g, ' ').trim();
  if (text.length <= 520) return text;
  const sentenceBreak = text.slice(0, 520).lastIndexOf('.');
  return `${text.slice(0, sentenceBreak > 260 ? sentenceBreak + 1 : 520).trim()}...`;
}

export function getDetailRituals(detailData = {}, fallbackFestival = {}) {
  const sequence = detailData.festival?.ritual_sequence
    || detailData.festival?.ritual_preview
    || detailData.ritual_preview
    || fallbackFestival.ritual_sequence
    || fallbackFestival.ritual_preview;
  const days = sequence?.days;
  if (!Array.isArray(days)) return [];
  return days.flatMap((day, dayIndex) => {
    const events = Array.isArray(day.events) && day.events.length ? day.events : [day];
    return events.map((event, eventIndex) => ({
      id: `${day.name || dayIndex}-${event.title || event.name || eventIndex}`,
      day: day.name || `Step ${dayIndex + 1}`,
      title: event.title || event.name || day.name || 'Ritual step',
      body: event.description || event.detail || day.description || 'Practice details are being normalized for this observance.',
    }));
  }).slice(0, 5);
}

export function buildExpandedFestivalStory(festival = {}, detailData = {}) {
  const detailFestival = detailData.festival || {};
  const mythology = detailFestival.mythology || {};
  const displayName = detailFestival.name || festival.displayName || festival.name || 'Festival';
  const description = detailFestival.description || festival.summary;
  const origin = mythology.origin_story || mythology.summary || description;
  const history = mythology.historical_context || festival.date_status_note;
  const regions = detailFestival.regional_focus || festival.regions || [];
  const deities = detailFestival.connected_deities || festival.connected_deities || [];
  const who = detailFestival.who_celebrates || 'Families and devotees who keep this observance in their community calendar.';
  const rituals = getDetailRituals(detailData, festival);
  const ritualNames = rituals.map((ritual) => ritual.title).filter(Boolean).slice(0, 4);
  const ritualBody = ritualNames.length
    ? `${displayName} is best understood through its sequence: ${ritualNames.join(', ')}. The details below preserve the order returned by the backend profile.`
    : `${displayName} is observed through household preparation, offerings, prayer, food, and community gathering, with local practice varying by lineage and region.`;

  return {
    title: detailFestival.tagline || festival.summary || displayName,
    lead: compactParagraph(description, mythology.summary || festival.summary),
    sections: [
      {
        title: 'Mythology and Meaning',
        body: compactParagraph(origin, description),
      },
      {
        title: 'Ritual Structure',
        body: compactParagraph(ritualBody),
      },
      {
        title: 'Living Practice',
        body: compactParagraph(history || `${who} ${regions.length ? `Regional focus: ${regions.join(', ')}.` : ''}`),
      },
    ],
    facts: [
      ['Who observes', who],
      ['Associated deities', deities.length ? deities.join(', ') : 'Community and household deities'],
      ['Regional focus', regions.length ? regions.join(', ') : 'Nepal-focused'],
      ['Catalog depth', readableCategory(detailFestival.content_status || festival.content_status || 'Documented profile')],
    ],
    rituals,
  };
}

export function buildCalendarFeedUrl(festivalId) {
  return apiHref(`/feeds/custom.ics?festivals=${encodeURIComponent(festivalId)}&years=1&download=1`);
}

const savedFestivalStorageKey = 'parva.savedFestivalIds.v1';

export function readSavedFestivalIds() {
  if (typeof window === 'undefined') return [];
  try {
    const parsed = JSON.parse(window.localStorage.getItem(savedFestivalStorageKey) || '[]');
    return Array.isArray(parsed) ? parsed.filter(Boolean) : [];
  } catch {
    return [];
  }
}

export function writeSavedFestivalIds(ids) {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(savedFestivalStorageKey, JSON.stringify([...new Set(ids)].sort()));
}

export function buildFestivalEvidenceUrl(festival = {}) {
  const year = festival.start_date ? new Date(`${festival.start_date}T00:00:00`).getFullYear() : new Date().getFullYear();
  return apiHref(`/festivals/${encodeURIComponent(festival.id || 'dashain')}/proof-capsule?year=${year}&authority_mode=authority_compare&risk_mode=strict`);
}

export function festivalOccurrenceKey(festival = {}) {
  return [
    festival.id || 'festival',
    festival.start_date || festival.bs_start?.formatted || festival.monthKey || 'catalog',
    festival.end_date || 'single',
  ].join(':');
}

