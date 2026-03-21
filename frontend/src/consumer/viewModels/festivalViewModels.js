import {
  countdownLabel,
  formatDate,
  formatDateRange,
  formatTime,
  getConsumerFestivalArtKey,
  normalizeRitualSteps,
  startOfSentence,
  sunriseShiftLabel,
} from './shared';

function normalizeCompletenessItem(item, fallback) {
  if (item && typeof item === 'object' && !Array.isArray(item)) {
    return {
      status: item.status || fallback.status,
      note: item.note || fallback.note,
    };
  }
  return fallback;
}

function profileStatusLabel(status) {
  switch (status) {
    case 'complete':
      return 'Editorial profile complete';
    case 'partial':
      return 'Editorial profile partial';
    default:
      return 'Editorial profile minimal';
  }
}

function buildRitualEmptyState(ritualStatus) {
  if (ritualStatus.status === 'partial') {
    return {
      kicker: 'Ritual sequence is partial',
      title: 'Some ritual material exists, but the canonical ceremony timeline is still partial.',
      body: ritualStatus.note,
    };
  }

  return {
    kicker: 'Ritual sequence not published',
    title: 'Structured ritual steps are not published for this observance yet.',
    body: ritualStatus.note,
  };
}

function buildRelatedEmptyState(relatedStatus) {
  if (relatedStatus.status === 'partial') {
    return {
      title: 'Related observances are only partially available right now.',
      body: relatedStatus.note,
    };
  }

  return {
    title: 'Nearby observances are not available for this festival window.',
    body: relatedStatus.note,
  };
}

export function buildConsumerFestivalsViewModel({ payload, search, category, savedFestivals = [], temporalState = {} }) {
  const savedIds = new Set(savedFestivals.map((item) => item.id));
  const groups = payload?.groups || [];
  const facets = payload?.facets || {};
  const allItems = groups.flatMap((group) => (group.items || []).map((item) => ({
    id: item.id,
    href: `/festivals/${item.id}`,
    title: item.display_name || item.name,
    summary: startOfSentence(
      item.summary || item.ritual_preview || item.description,
      `${item.display_name || item.name} remains part of the live observance calendar.`,
    ),
    dateLabel: formatDateRange(item.start_date, item.end_date, temporalState),
    artKey: getConsumerFestivalArtKey(item.id, item.category),
    badges: [item.category, ...(item.regional_focus || []).slice(0, 1)].filter(Boolean),
    saved: savedIds.has(item.id),
  })));

  return {
    title: 'Festivals',
    subtitle: 'Keep the next observance in view, then browse deeper only when you need the full seasonal picture.',
    searchValue: search || '',
    activeFilter: category || '',
    facets: {
      categories: Array.isArray(facets.categories) ? facets.categories : [],
      months: Array.isArray(facets.months) ? facets.months : [],
      regions: Array.isArray(facets.regions) ? facets.regions : [],
    },
    resultCount: allItems.length,
    featured: allItems[0] || null,
    supporting: allItems.slice(1, 3),
    chapters: groups.map((group) => ({
      id: group.month_key || group.month_label,
      label: group.month_label || group.month_key || 'Current chapter',
      lead: group.items?.[0]
        ? {
            id: group.items[0].id,
            href: `/festivals/${group.items[0].id}`,
            title: group.items[0].display_name || group.items[0].name,
            summary: startOfSentence(
              group.items[0].summary || group.items[0].ritual_preview || group.items[0].description,
              `${group.items[0].display_name || group.items[0].name} leads this chapter.`,
            ),
            dateLabel: formatDateRange(group.items[0].start_date, group.items[0].end_date, temporalState),
            artKey: getConsumerFestivalArtKey(group.items[0].id, group.items[0].category),
          }
        : null,
      items: (group.items || []).slice(1, 5).map((item) => ({
        id: item.id,
        href: `/festivals/${item.id}`,
        title: item.display_name || item.name,
        summary: startOfSentence(
          item.summary || item.ritual_preview || item.description,
          `${item.display_name || item.name} remains part of the current observance chapter.`,
        ),
        dateLabel: formatDateRange(item.start_date, item.end_date, temporalState),
        artKey: getConsumerFestivalArtKey(item.id, item.category),
      })),
    })),
    timelineCards: allItems.slice(0, 8),
    emptyState: {
      title: 'No observances match this view yet',
      body: 'Try clearing the filters or searching for a broader observance family.',
    },
  };
}

export function buildConsumerFestivalDetailViewModel({
  festival,
  dates,
  nextDates = [],
  nearbyFestivals = [],
  completeness,
  temporalState = {},
}) {
  const rituals = normalizeRitualSteps(festival).slice(0, 6);
  const narrativeStatus = normalizeCompletenessItem(completeness?.narrative, {
    status: festival?.description || festival?.mythology?.summary ? 'partial' : 'missing',
    note: 'Editorial origin material is still partial for this observance.',
  });
  const ritualStatus = normalizeCompletenessItem(completeness?.ritual_sequence, {
    status: rituals.length ? 'available' : 'missing',
    note: rituals.length
      ? 'Structured ritual steps are published for this observance.'
      : 'Structured ritual steps are not part of the live profile for this observance yet.',
  });
  const relatedStatus = normalizeCompletenessItem(completeness?.related_observances, {
    status: nearbyFestivals.length ? 'available' : 'missing',
    note: nearbyFestivals.length
      ? 'Nearby observances are available for the current ritual window.'
      : 'No nearby observances were returned for this festival window.',
  });
  const dateStatus = normalizeCompletenessItem(completeness?.dates, {
    status: dates ? 'available' : 'missing',
    note: dates
      ? 'Resolved calendar dates are available for the requested year.'
      : 'Resolved calendar dates are not available for the requested year.',
  });
  const overallProfileStatus = completeness?.overall || festival?.content_status || 'minimal';
  const ritualEmpty = buildRitualEmptyState(ritualStatus);
  const relatedEmpty = buildRelatedEmptyState(relatedStatus);

  return {
    title: festival?.name || 'Festival',
    subtitle: festival?.name_nepali || '',
    profileStatusLabel: profileStatusLabel(overallProfileStatus),
    dateLabel: formatDateRange(dates?.start_date, dates?.end_date, temporalState),
    countdown: countdownLabel(dates?.start_date),
    summary: startOfSentence(
      festival?.tagline || festival?.description || festival?.mythology?.summary,
      'This observance is part of the living Nepal ritual calendar.',
    ),
    whyItMatters: startOfSentence(
      festival?.mythology?.significance || festival?.description,
      'This observance carries seasonal, ritual, and social meaning.',
    ),
    originStory: startOfSentence(
      festival?.mythology?.summary || festival?.mythology_summary || festival?.mythology?.origin,
      'The deeper story of this observance will appear here as the editorial profile fills in.',
    ),
    originStatusNote: narrativeStatus.note,
    rituals,
    ritualStatus,
    ritualEmpty,
    artKey: getConsumerFestivalArtKey(festival?.id, festival?.category),
    quickFacts: [
      { label: 'Calendar', value: festival?.calendar_system || festival?.calendar_type || 'Traditional profile' },
      { label: 'Duration', value: festival?.duration_days ? `${festival.duration_days} days` : 'Single observance' },
      { label: 'Category', value: festival?.category || 'Observance' },
      { label: 'Profile', value: profileStatusLabel(overallProfileStatus) },
    ],
    occurrences: (Array.isArray(nextDates) ? nextDates : []).slice(0, 4).map((item) => ({
      year: item.gregorian_year,
      label: formatDateRange(item.start_date, item.end_date, temporalState),
      bsLabel: item.bs_start?.formatted || '',
    })),
    related: nearbyFestivals.slice(0, 4).map((item) => ({
      id: item.id,
      title: item.name || item.display_name || item.id,
      href: `/festivals/${item.id}`,
      dateLabel: formatDate(item.start_date, { month: 'short', day: 'numeric' }, temporalState) || 'Open observance',
    })),
    relatedStatus,
    relatedEmpty,
    evidence: {
      title: festival?.name || 'Festival detail',
      intro: 'Festival detail leads with meaning, ritual, and timing. Technical method and metadata stay one step lower.',
      methodRef: dates?.calculation_method || festival?.calculation_method || 'Festival calendar profile',
      confidenceNote: dates?.confidence || 'Computed guidance',
      placeUsed: 'Nepal-focused observance profile',
      computedForDate: dates?.start_date || 'Current observance cycle',
      availability: [
        { label: 'Ritual sequence', available: Boolean(rituals.length), note: ritualStatus.note },
        { label: 'Future occurrences', available: Boolean(nextDates?.length), note: dateStatus.note },
        { label: 'Related observances', available: Boolean(nearbyFestivals.length), note: relatedStatus.note },
      ],
      meta: null,
      traceFallbackId: festival?.calculation_trace_id || null,
    },
  };
}

export function buildConsumerMyPlaceViewModel({
  temporalState,
  memberState,
  activePreset,
  panchanga,
  contextPayload,
  festivals = [],
  meta,
}) {
  const primaryPlace = memberState.savedPlaces[0] || null;
  const placeLabel = primaryPlace?.label || activePreset?.label || contextPayload?.place_title || 'My place';
  const reminders = [...memberState.reminders, ...(contextPayload?.upcoming_reminders || [])].slice(0, 3);

  return {
    title: 'My Place',
    subtitle: 'Set the place that shapes your day, then keep only the place-aware changes that matter in view.',
    placeLabel,
    timezoneLabel: temporalState.timezone || 'Asia/Kathmandu',
    contextTitle: contextPayload?.context_title || 'Current context',
    contextSummary: contextPayload?.context_summary || 'Place-aware context will appear here when the live context payload is available.',
    sunriseShift: sunriseShiftLabel(panchanga),
    localSunrise: formatTime(panchanga?.local_sunrise, temporalState) || 'Pending',
    savedStatus: contextPayload?.visit_note || 'Saved place details remain local-first on this device.',
    reminders: reminders.map((item, index) => ({
      id: item.id || `reminder_${index}`,
      title: item.title || 'Saved reminder',
      note: item.date_label || item.date || item.status || 'Reminder details appear here when available.',
    })),
    festivals: festivals.slice(0, 4).map((festival) => ({
      id: festival.id,
      title: festival.name || festival.display_name,
    })),
    cards: [
      {
        label: 'What changes here',
        value: sunriseShiftLabel(panchanga),
        note: 'This is the simplest signal for whether the place materially changes the day rhythm.',
      },
      {
        label: 'Reminder rhythm',
        value: reminders.length ? `${reminders.length} saved` : 'No reminders yet',
        note: reminders[0]?.title || 'Saved observances and reminders will appear here.',
      },
      {
        label: 'Daily inspiration',
        value: contextPayload?.daily_inspiration || 'Quiet ritual space changes how the day is felt.',
        note: contextPayload?.temperature_note || 'Context notes remain secondary to the main place answer.',
      },
      {
        label: 'Tithi',
        value: panchanga?.tithi?.name || 'Pending',
        note: panchanga?.tithi?.paksha ? `${panchanga.tithi.paksha} fortnight` : 'Lunar day context appears when available.',
      },
      {
        label: 'Nakshatra',
        value: panchanga?.nakshatra?.name || 'Pending',
        note: panchanga?.nakshatra?.number ? `Number ${panchanga.nakshatra.number}` : 'Star field context appears when available.',
      },
      {
        label: 'Yoga',
        value: panchanga?.yoga?.name || 'Pending',
        note: panchanga?.vaara?.name_english || 'The daily signal set appears when available.',
      },
    ],
    evidence: {
      title: 'My Place',
      intro: 'My Place uses the selected date, place, and personal panchanga profile to explain what materially changes for your day.',
      methodRef: meta?.method || panchanga?.method_profile || 'Personal place profile',
      confidenceNote: meta?.confidence?.level || panchanga?.quality_band || 'Computed guidance',
      placeUsed: placeLabel,
      computedForDate: temporalState.date,
      availability: [
        { label: 'Local sunrise shift', available: Boolean(panchanga?.local_sunrise && panchanga?.sunrise), note: 'Shift is shown only when both local and comparison sunrise values are available.' },
        { label: 'Place context', available: Boolean(contextPayload?.context_summary), note: 'The sanctuary summary appears when the personal context endpoint returns a live context block.' },
        { label: 'Same-day observances', available: Boolean(festivals.length), note: 'Observances appear when the selected date intersects current festival coverage.' },
      ],
      meta,
      traceFallbackId: panchanga?.calculation_trace_id || null,
    },
  };
}
