import { useEffect, useMemo, useState } from 'react';
import { CONSUMER_BEST_TIME_OPTIONS, buildConsumerBestTimeViewModel } from '../consumer/consumerViewModels';
import { findPresetByLocation } from '../data/locationPresets';
import { muhurtaAPI } from '../services/api';
import { describeSupportError } from '../services/errorFormatting';
import {
  addIsoDays,
  addIsoMonths,
  daysInIsoMonth,
  endOfIsoMonth,
  isoDayOfWeek,
  startOfIsoMonth,
} from '../utils/isoDate';
import { formatProductDate, formatProductTimeRange } from '../utils/productDateTime';

function startOfMonth(dateValue) {
  return startOfIsoMonth(dateValue);
}

function endOfMonth(dateValue) {
  return endOfIsoMonth(dateValue);
}

function addMonths(dateValue, count) {
  return addIsoMonths(dateValue, count);
}

function toneRank(tone) {
  switch (tone) {
    case 'strong':
      return 4;
    case 'good':
      return 3;
    case 'mixed':
      return 2;
    case 'avoid':
      return 1;
    default:
      return 0;
  }
}

function windowRangeLabel(windowLike, state) {
  if (!windowLike?.start || !windowLike?.end) {
    return '';
  }
  return formatProductTimeRange(windowLike.start, windowLike.end, state);
}

function buildMonthDays(monthStart, summaries = []) {
  const summaryMap = new Map(summaries.map((item) => [item.date, item]));
  const leadingEmptyCells = isoDayOfWeek(monthStart);
  const totalDays = daysInIsoMonth(monthStart);
  const cells = [];

  for (let index = 0; index < leadingEmptyCells; index += 1) {
    cells.push({ id: `empty-${monthStart}-${index}`, empty: true });
  }

  for (let day = 1; day <= totalDays; day += 1) {
    const iso = addIsoDays(monthStart, day - 1);
    cells.push({
      id: iso,
      empty: false,
      date: iso,
      day,
      summary: summaryMap.get(iso) || null,
    });
  }

  return cells;
}

function pickInitialDate(payload, preferredDate) {
  const availableDates = Array.isArray(payload?.days) ? payload.days : [];
  if (availableDates.some((item) => item.date === preferredDate)) {
    return preferredDate;
  }
  return availableDates.find((item) => item.has_viable_window)?.date
    || availableDates[0]?.date
    || preferredDate;
}

export function useBestTimePlanner({ state, initialType = 'general' } = {}) {
  const activePreset = useMemo(() => findPresetByLocation(state.location), [state.location]);
  const [type, setType] = useState(initialType);
  const [windowStart, setWindowStart] = useState(() => startOfMonth(state.date));
  const [selectedDate, setSelectedDate] = useState(state.date);
  const [calendarPayload, setCalendarPayload] = useState(null);
  const [detailPayload, setDetailPayload] = useState(null);
  const [detailMeta, setDetailMeta] = useState(null);
  const [selectedBlock, setSelectedBlock] = useState(null);
  const [loadingCalendar, setLoadingCalendar] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(true);
  const [calendarError, setCalendarError] = useState(null);
  const [detailError, setDetailError] = useState(null);

  const currentMonth = windowStart;
  const nextMonth = useMemo(() => addMonths(windowStart, 1), [windowStart]);
  const rangeEnd = useMemo(() => endOfMonth(nextMonth), [nextMonth]);

  useEffect(() => {
    let cancelled = false;

    async function loadCalendar() {
      setLoadingCalendar(true);
      setCalendarError(null);

      try {
        const payload = await muhurtaAPI.getCalendar({
          from: currentMonth,
          to: rangeEnd,
          lat: state.location?.latitude,
          lon: state.location?.longitude,
          tz: state.timezone,
          type,
          assumptionSet: 'np-mainstream-v2',
        });

        if (cancelled) return;

        setCalendarPayload(payload);
        setSelectedDate((previous) => pickInitialDate(payload, previous || state.date));
      } catch (reason) {
        if (cancelled) return;

        setCalendarPayload(null);
        setCalendarError(describeSupportError(reason, 'Best-date guidance is unavailable right now.'));
      } finally {
        if (!cancelled) {
          setLoadingCalendar(false);
        }
      }
    }

    loadCalendar();
    return () => {
      cancelled = true;
    };
  }, [currentMonth, rangeEnd, state.date, state.location?.latitude, state.location?.longitude, state.timezone, type]);

  useEffect(() => {
    let cancelled = false;

    async function loadDetail() {
      if (!selectedDate) return;

      setLoadingDetail(true);
      setDetailError(null);

      try {
        const envelope = await muhurtaAPI.getHeatmapEnvelope({
          date: selectedDate,
          lat: state.location?.latitude,
          lon: state.location?.longitude,
          tz: state.timezone,
          type,
          assumptionSet: 'np-mainstream-v2',
        });

        if (cancelled) return;

        const nextPayload = envelope.data || null;
        setDetailPayload(nextPayload);
        setDetailMeta(envelope.meta || null);
        setSelectedBlock(nextPayload?.best_window || nextPayload?.blocks?.[0] || null);
      } catch (reason) {
        if (cancelled) return;

        setDetailPayload(null);
        setDetailMeta(null);
        setSelectedBlock(null);
        setDetailError(describeSupportError(reason, 'Best-time details are unavailable for the selected date.'));
      } finally {
        if (!cancelled) {
          setLoadingDetail(false);
        }
      }
    }

    loadDetail();
    return () => {
      cancelled = true;
    };
  }, [selectedDate, state.location?.latitude, state.location?.longitude, state.timezone, type]);

  const placeLabel = activePreset?.label || 'Your place';
  const activity = useMemo(
    () => CONSUMER_BEST_TIME_OPTIONS.find((item) => item.value === type) || CONSUMER_BEST_TIME_OPTIONS[0],
    [type],
  );

  const rankedDates = useMemo(() => {
    const days = Array.isArray(calendarPayload?.days) ? calendarPayload.days : [];
    return [...days]
      .sort((left, right) => (
        toneRank(right.tone) - toneRank(left.tone)
        || Number(right.top_score || -999) - Number(left.top_score || -999)
        || left.date.localeCompare(right.date)
      ))
      .slice(0, 3)
      .map((item) => ({
        ...item,
        dateLabel: formatProductDate(item.date, { weekday: 'short', month: 'short', day: 'numeric' }, state),
        windowLabel: item.best_window?.start && item.best_window?.end
          ? windowRangeLabel(item.best_window, state)
          : item.has_viable_window
            ? item.best_window?.name || 'Best window'
            : 'Use with caution',
        note: item.has_viable_window
          ? item.best_window?.rank_explanation || 'One of the clearest dates in the current planning range.'
          : 'No strong window crossed the threshold for this date.',
      }));
  }, [calendarPayload, state]);

  const currentMonthCells = useMemo(
    () => buildMonthDays(currentMonth, calendarPayload?.days || []),
    [calendarPayload?.days, currentMonth],
  );
  const nextMonthCells = useMemo(
    () => buildMonthDays(nextMonth, calendarPayload?.days || []),
    [calendarPayload?.days, nextMonth],
  );

  const detailViewModel = useMemo(
    () => buildConsumerBestTimeViewModel({
      payload: detailPayload,
      meta: detailMeta,
      state: { ...state, date: selectedDate },
      type,
      selectedBlock,
      placeLabel,
    }),
    [detailMeta, detailPayload, placeLabel, selectedBlock, selectedDate, state, type],
  );

  return {
    type,
    setType,
    windowStart,
    setWindowStart,
    selectedDate,
    setSelectedDate,
    selectedBlock,
    setSelectedBlock,
    currentMonth,
    nextMonth,
    placeLabel,
    activity,
    calendarPayload,
    detailPayload,
    loadingCalendar,
    loadingDetail,
    calendarError,
    detailError,
    rankedDates,
    currentMonthCells,
    nextMonthCells,
    detailViewModel,
  };
}

export { addMonths, startOfMonth, windowRangeLabel };

export default useBestTimePlanner;
