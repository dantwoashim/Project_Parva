import {
  CONSUMER_BEST_TIME_OPTIONS,
  bestTimeConsumerNote,
  bestTimeWindowLabel,
  formatDate,
  sortedBlocks,
  timePercent,
  toneFromBlock,
} from './shared';

export function buildConsumerBestTimeViewModel({ payload, meta, state, type, selectedBlock, placeLabel }) {
  const ranked = sortedBlocks(payload);
  const activity = CONSUMER_BEST_TIME_OPTIONS.find((item) => item.value === type) || CONSUMER_BEST_TIME_OPTIONS[0];
  const best = payload?.best_window || ranked[0] || null;
  const alternates = ranked.filter((item) => item.index !== best?.index && toneFromBlock(item) !== 'avoid').slice(0, 2);
  const avoid = payload?.rahu_kalam || ranked.find((item) => toneFromBlock(item) === 'avoid') || null;
  const selection = selectedBlock || best || alternates[0] || null;

  const timeline = ranked.map((block, index) => {
    const startPct = timePercent(block.start);
    const endPct = timePercent(block.end || block.start);
    const rawWidthPct = Math.max(0, endPct - startPct);
    const widthPct = Math.max(10, rawWidthPct);
    const label = bestTimeWindowLabel(block, state);
    const tone = toneFromBlock(block);
    const compact = widthPct < 14;
    return {
      id: block.index,
      title: compact ? (tone === 'strong' ? 'Best' : tone === 'good' ? 'Backup' : tone === 'avoid' ? 'Avoid' : 'Mixed') : block.name || 'Window',
      time: label || 'Time pending',
      left: `${startPct}%`,
      right: `${Math.max(0, 100 - Math.max(endPct, startPct + widthPct))}%`,
      widthPct,
      lane: index % 2,
      tone,
      isSelected: selection?.index === block.index,
      compact,
      note: bestTimeConsumerNote(block, 'Part of the live ranked schedule.'),
    };
  });

  return {
    title: 'Best Time',
    intro: 'Open the clearest window first, then scan the rest of the day only if you need a backup.',
    activityLabel: activity.label,
    placeLabel: placeLabel || 'Your place',
    dateLabel: formatDate(state.date, { weekday: 'long', month: 'long', day: 'numeric' }, state) || state.date,
    best: {
      title: bestTimeWindowLabel(best, state),
      note: bestTimeConsumerNote(best, 'This is the strongest opening in the current timing profile.'),
    },
    alternates: alternates.map((block) => ({
      id: block.index,
      title: bestTimeWindowLabel(block, state),
      note: bestTimeConsumerNote(block, 'A usable backup if you miss the primary window.'),
      tone: toneFromBlock(block),
    })),
    avoid: {
      title: bestTimeWindowLabel(avoid, state) || 'No dedicated caution period returned',
      note: avoid?.start ? bestTimeConsumerNote(avoid, 'Use this stretch for routine or lower-stakes work.') : 'The timeline below carries the weaker periods when a specific caution window is not returned.',
    },
    timeline,
    selection: selection
      ? {
          title: selection.name || 'Selected window',
          time: bestTimeWindowLabel(selection, state) || 'Time pending',
          note: bestTimeConsumerNote(selection, 'This window is part of the live ranked schedule.'),
        }
      : null,
    evidence: {
      title: 'Best Time',
      intro: 'The ranking combines the current activity type, place, date, and live timing windows. Details stay available without making the page feel like a scoring console.',
      methodRef: meta?.method || 'Best-time profile',
      confidenceNote: meta?.confidence?.level || 'Computed guidance',
      placeUsed: placeLabel || state.timezone,
      computedForDate: state.date,
      availability: [
        { label: 'Primary window', available: Boolean(best?.start), note: 'The first answer should always be a direct recommendation when enough signal exists.' },
        { label: 'Alternate windows', available: Boolean(alternates.length), note: 'Backups only appear when they are meaningfully usable.' },
        { label: 'Avoid period', available: Boolean(avoid?.start), note: 'If no dedicated caution window is returned, the timeline still reveals weaker spans.' },
      ],
      meta,
      traceFallbackId: payload?.calculation_trace_id || null,
    },
  };
}
