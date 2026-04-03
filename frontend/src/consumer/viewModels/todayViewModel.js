import {
  buildSupportingCopy,
  formatDate,
  formatDateRange,
  formatTime,
  formatTimeRange,
  sortedBlocks,
  startOfSentence,
  toneFromBlock,
  uniqueFestivals,
} from './shared';

function startCaseTruth(value) {
  return String(value || 'unknown')
    .split(/[_-]+/)
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

function truthTone(value) {
  const normalized = String(value || '').toLowerCase();
  if (normalized.includes('gold') || normalized.includes('validated') || normalized.includes('high')) {
    return 'authoritative';
  }
  if (normalized.includes('provisional') || normalized.includes('computed')) {
    return 'computed';
  }
  if (normalized.includes('default') || normalized.includes('degraded')) {
    return 'fallback';
  }
  return 'default';
}

function riskTone(value) {
  const normalized = String(value || '').toLowerCase();
  if (normalized === 'stable') return 'computed';
  if (normalized === 'one_day_sensitive') return 'fallback';
  if (normalized === 'high_disagreement_risk') return 'fallback';
  return 'default';
}

export function buildConsumerTodayViewModel({
  state,
  placeLabel,
  compass,
  compassMeta,
  muhurta,
  muhurtaMeta,
  onDateFestivals = [],
  upcomingFestivals = [],
}) {
  const bestWindow = muhurta?.best_window || sortedBlocks(muhurta)[0] || null;
  const avoidWindow = muhurta?.rahu_kalam || sortedBlocks(muhurta).find((item) => toneFromBlock(item) === 'avoid') || null;
  const observances = uniqueFestivals(onDateFestivals, upcomingFestivals).slice(0, 4);
  const truthSources = [
    muhurtaMeta
      ? {
          label: 'Best time',
          qualityBand: muhurtaMeta.quality_band || null,
          method: muhurtaMeta.method || null,
          confidence: muhurtaMeta.confidence?.level || null,
          degraded: Boolean(muhurtaMeta.degraded?.active),
          boundaryRadar: muhurta?.boundary_radar || muhurtaMeta.boundary_radar || null,
          stabilityScore: muhurta?.stability_score ?? muhurtaMeta.stability_score ?? null,
          recommendedAction: muhurta?.recommended_action || muhurtaMeta.recommended_action || null,
        }
      : null,
    compassMeta
      ? {
          label: 'Temporal compass',
          qualityBand: compassMeta.quality_band || null,
          method: compassMeta.method || null,
          confidence: compassMeta.confidence?.level || null,
          degraded: Boolean(compassMeta.degraded?.active),
          boundaryRadar: compass?.boundary_radar || compassMeta.boundary_radar || null,
          stabilityScore: compass?.stability_score ?? compassMeta.stability_score ?? null,
          recommendedAction: compass?.recommended_action || compassMeta.recommended_action || null,
        }
      : null,
  ].filter(Boolean);
  const truthChips = truthSources.flatMap((item) => {
    const chips = [];
    if (item.qualityBand) {
      chips.push({
        label: `${item.label}: ${startCaseTruth(item.qualityBand)}`,
        tone: truthTone(item.qualityBand),
      });
    } else if (item.confidence) {
      chips.push({
        label: `${item.label}: ${startCaseTruth(item.confidence)}`,
        tone: truthTone(item.confidence),
      });
    }
    if (item.degraded) {
      chips.push({
        label: `${item.label}: Defaults Applied`,
        tone: 'fallback',
      });
    }
    if (item.boundaryRadar) {
      chips.push({
        label: `${item.label}: ${startCaseTruth(item.boundaryRadar)}`,
        tone: riskTone(item.boundaryRadar),
      });
    }
    return chips;
  });
  const signals = [
    {
      label: 'Tithi',
      value: compass?.primary_readout?.tithi_name || 'Pending',
      note: compass?.primary_readout?.paksha ? `${compass.primary_readout.paksha} fortnight` : 'Lunar day context is still loading.',
    },
    {
      label: 'Nakshatra',
      value: compass?.signals?.nakshatra?.name || 'Pending',
      note: compass?.signals?.nakshatra?.pada ? `Pada ${compass.signals.nakshatra.pada}` : 'Star field context appears here when available.',
    },
    {
      label: 'Yoga',
      value: compass?.signals?.yoga?.name || 'Pending',
      note: compass?.signals?.karana?.name || 'The day tone becomes clearer when yoga data is present.',
    },
    {
      label: 'Karana',
      value: compass?.signals?.karana?.name || 'Pending',
      note: compass?.signals?.vaara?.name_english || 'Weekday context joins here when available.',
    },
  ];

  return {
    placeLabel: placeLabel || 'Your place',
    headline: `Today in ${placeLabel || 'your place'}`,
    bsDate: compass?.bikram_sambat
      ? `${compass.bikram_sambat.month_name} ${compass.bikram_sambat.day}, ${compass.bikram_sambat.year}`
      : 'Bikram Sambat date pending',
    gregorianDate: formatDate(state.date, { month: 'long', day: 'numeric', year: 'numeric' }, state) || state.date,
    summary: startOfSentence(
      compass?.primary_readout?.tithi_name
        ? `${compass.primary_readout.tithi_name} shapes the day with a steadier, more intentional tone.`
        : null,
      'A calm reading of today should tell you what matters, what opens cleanly, and what to leave alone.',
    ),
    supporting: bestWindow?.name
      ? `${bestWindow.name} is the clearest opening in the current live ranking.`
      : 'The strongest opening will appear here when the live timing profile returns.',
    bestWindow: {
      label: 'Best window',
      value: bestWindow?.start ? formatTimeRange(bestWindow.start, bestWindow.end, state) : 'Pending',
      note: buildSupportingCopy(bestWindow, 'Use this window for the most important plan of the day.'),
    },
    avoidWindow: {
      label: 'Avoid window',
      value: avoidWindow?.start ? formatTimeRange(avoidWindow.start, avoidWindow.end, state) : 'No strong caution returned',
      note: avoidWindow?.start ? 'Keep lower-priority tasks here when possible.' : 'If no avoid window is returned, the timeline below carries the stronger signal.',
    },
    dayTone: {
      label: 'Day tone',
      value: compass?.signals?.yoga?.name || compass?.signals?.nakshatra?.name || 'Balanced',
      note: compass?.signals?.nakshatra?.name
        ? `${compass.signals.nakshatra.name} is shaping the social and emotional tone of the day.`
        : 'The day tone softens when fewer signal layers are available.',
    },
    sunrise: formatTime(compass?.horizon?.sunrise, state),
    sunset: formatTime(compass?.horizon?.sunset, state),
    rhythm: compass?.signals?.yoga?.name || 'Steady rhythm',
    timeline: sortedBlocks(muhurta).slice(0, 4).map((block) => ({
      id: block.index,
      title: block.name || 'Window',
      time: block.start ? formatTimeRange(block.start, block.end, state) : 'Time pending',
      note: buildSupportingCopy(block, 'This slot is part of the live timing read.'),
      tone: toneFromBlock(block),
    })),
    observances: observances.map((festival) => ({
      id: festival.id,
      title: festival.display_name || festival.name,
      category: festival.category || 'Observance',
      dateLabel: formatDateRange(festival.start_date || festival.start, festival.end_date || festival.end, state),
      summary: startOfSentence(
        festival.summary || festival.description || festival.tagline,
        'Open the observance for the story, timing, and practice notes.',
      ),
      truthNote: festival.support_tier
        ? `${startCaseTruth(festival.support_tier)} via ${festival.selection_policy || 'public_default'}`
        : null,
    })),
    truthSurface: {
      chips: truthChips,
      sources: truthSources.map((item) => ({
        label: item.label,
        qualityBand: startCaseTruth(item.qualityBand || 'unknown'),
        method: startCaseTruth(item.method || 'unknown'),
        confidence: startCaseTruth(item.confidence || 'unknown'),
        degraded: item.degraded,
        boundaryRadar: item.boundaryRadar ? startCaseTruth(item.boundaryRadar) : null,
        stabilityScore: item.stabilityScore,
        recommendedAction: item.recommendedAction || null,
      })),
    },
    signals,
    evidence: {
      title: 'Today',
      intro: 'Parva uses the current place, date, and live timing profile to build the day reading. Method stays available without crowding the answer.',
      methodRef: muhurtaMeta?.method || compassMeta?.method || 'Daily guidance profile',
      confidenceNote: muhurtaMeta?.confidence?.level || compassMeta?.confidence?.level || 'Computed guidance',
      placeUsed: placeLabel || state.timezone,
      computedForDate: state.date,
      availability: [
        { label: 'Best-time ranking', available: Boolean(bestWindow?.start), note: 'A clear recommendation appears only when the live ranking returns enough signal.' },
        { label: 'Sunrise and sunset', available: Boolean(compass?.horizon?.sunrise || compass?.horizon?.sunset), note: 'The day answer should not break when horizon data is partial.' },
        { label: 'Same-day observance', available: Boolean(observances.length), note: 'Observances appear when the calendar payload intersects the selected day.' },
      ],
      meta: muhurtaMeta || compassMeta,
      traceFallbackId: muhurta?.calculation_trace_id || compass?.calculation_trace_id || null,
    },
  };
}
