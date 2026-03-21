import { useEffect, useMemo, useState } from 'react';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { CONSUMER_BEST_TIME_OPTIONS, buildConsumerBestTimeViewModel } from '../consumer/consumerViewModels';
import { findPresetByLocation } from '../data/locationPresets';
import { useTemporalContext } from '../context/useTemporalContext';
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
import './MuhurtaPage.css';

function startOfMonth(dateValue) {
  return startOfIsoMonth(dateValue);
}

function endOfMonth(dateValue) {
  return endOfIsoMonth(dateValue);
}

function addMonths(dateValue, count) {
  return addIsoMonths(dateValue, count);
}

function monthLabel(dateValue, state) {
  return formatProductDate(dateValue, { month: 'long', year: 'numeric' }, state) || dateValue;
}

function windowRangeLabel(windowLike, state) {
  if (!windowLike?.start || !windowLike?.end) {
    return '';
  }
  return formatProductTimeRange(windowLike.start, windowLike.end, state);
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

function DaySummaryList({ title, items, onSelectDate }) {
  if (!items.length) return null;

  return (
    <article className="muhurta-page__summary-card">
      <p className="muhurta-page__eyebrow">{title}</p>
      <div className="muhurta-page__summary-list">
        {items.map((item) => (
          <button key={item.date} type="button" className="muhurta-page__summary-item" onClick={() => onSelectDate(item.date)}>
            <span>{item.dateLabel}</span>
            <strong>{item.windowLabel}</strong>
            <small>{item.note}</small>
          </button>
        ))}
      </div>
    </article>
  );
}

export function MuhurtaPage() {
  const { state } = useTemporalContext();
  const activePreset = useMemo(() => findPresetByLocation(state.location), [state.location]);
  const [type, setType] = useState('general');
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
      } catch (error) {
        if (cancelled) return;
        setCalendarPayload(null);
        setCalendarError(describeSupportError(error, 'Best-date guidance is unavailable right now.'));
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
      } catch (error) {
        if (cancelled) return;
        setDetailPayload(null);
        setDetailMeta(null);
        setSelectedBlock(null);
        setDetailError(describeSupportError(error, 'Best-time details are unavailable for the selected date.'));
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

  const renderMonth = (monthStart, cells) => (
    <article className="muhurta-page__month-card">
      <div className="muhurta-page__month-head">
        <h2>{monthLabel(monthStart, state)}</h2>
      </div>
      <div className="muhurta-page__weekday-row" aria-hidden="true">
        {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map((label) => (
          <span key={`${monthStart}-${label}`}>{label}</span>
        ))}
      </div>
      <div className="muhurta-page__calendar-grid">
        {cells.map((cell) => {
          if (cell.empty) {
            return <div key={cell.id} className="muhurta-page__calendar-empty" aria-hidden="true" />;
          }

          const summary = cell.summary;
          const tone = summary?.tone || 'unavailable';
          const isSelected = cell.date === selectedDate;
          return (
            <button
              key={cell.id}
              type="button"
              className={`muhurta-page__day-card muhurta-page__day-card--${tone}${isSelected ? ' is-selected' : ''}`.trim()}
              onClick={() => setSelectedDate(cell.date)}
            >
              <span className="muhurta-page__day-number">{cell.day}</span>
              <strong>{summary?.best_window?.name || (summary?.has_viable_window ? 'Good date' : 'No strong pick')}</strong>
              <small>
                {summary?.best_window?.start && summary?.best_window?.end
                  ? windowRangeLabel(summary.best_window, state)
                  : summary?.has_viable_window
                    ? 'Open day details'
                    : 'Caution'}
              </small>
            </button>
          );
        })}
      </div>
    </article>
  );

  return (
    <section className="muhurta-page animate-fade-in-up consumer-route consumer-route--analysis">
      <header className="muhurta-page__hero">
        <div>
          <p className="muhurta-page__eyebrow">Best Time</p>
          <h1>Choose a date first.</h1>
          <p className="muhurta-page__intro">
            Pick the occasion, scan the stronger dates across the next two months, then open one day for the exact timing.
          </p>
        </div>
        <div className="muhurta-page__hero-meta">
          <span>Place</span>
          <strong>{placeLabel}</strong>
        </div>
      </header>

      <section className="muhurta-page__activities">
        {CONSUMER_BEST_TIME_OPTIONS.map((option) => (
          <button
            key={option.value}
            type="button"
            className={`muhurta-page__activity-pill ${type === option.value ? 'is-active' : ''}`.trim()}
            onClick={() => setType(option.value)}
          >
            {option.label}
          </button>
        ))}
      </section>

      <section className="muhurta-page__planner">
        <div className="muhurta-page__planner-head">
          <div>
            <p className="muhurta-page__eyebrow">Date planner</p>
            <h2>{activity.label}</h2>
          </div>
          <div className="muhurta-page__planner-actions">
            <button type="button" className="btn btn-secondary" onClick={() => setWindowStart(addMonths(windowStart, -1))}>
              Earlier
            </button>
            <button type="button" className="btn btn-secondary" onClick={() => setWindowStart(addMonths(windowStart, 1))}>
              Later
            </button>
          </div>
        </div>

        {loadingCalendar ? (
          <div className="skeleton muhurta-page__calendar-skeleton" />
        ) : calendarError ? (
          <article className="muhurta-page__error ink-card" role="alert">
            <h2>Best-date guidance is temporarily unavailable.</h2>
            <p>{calendarError}</p>
          </article>
        ) : (
          <>
            <div className="muhurta-page__summary-grid">
              <DaySummaryList title="Strongest dates" items={rankedDates} onSelectDate={setSelectedDate} />
              <article className="muhurta-page__summary-card">
                <p className="muhurta-page__eyebrow">Selected date</p>
                <strong className="muhurta-page__selected-date">
                  {formatProductDate(selectedDate, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }, state) || selectedDate}
                </strong>
                <p>
                  Open one date at a time so the exact window, caution periods, and detailed timing stay readable.
                </p>
              </article>
            </div>

            <div className="muhurta-page__months">
              {renderMonth(currentMonth, currentMonthCells)}
              {renderMonth(nextMonth, nextMonthCells)}
            </div>
          </>
        )}
      </section>

      <section className="muhurta-page__detail">
        <div className="muhurta-page__detail-head">
          <div>
            <p className="muhurta-page__eyebrow">Day details</p>
            <h2>{detailViewModel.dateLabel}</h2>
          </div>
          <EvidenceDrawer {...detailViewModel.evidence} />
        </div>

        {loadingDetail ? (
          <div className="skeleton muhurta-page__detail-skeleton" />
        ) : detailError ? (
          <article className="muhurta-page__error ink-card" role="alert">
            <h2>Best-time details are temporarily unavailable.</h2>
            <p>{detailError}</p>
          </article>
        ) : (
          <>
            <div className="muhurta-page__window-grid">
              {[detailViewModel.best, ...(detailViewModel.alternates || []).slice(0, 2)].filter(Boolean).map((item, index) => (
                <article key={`${item.title}-${index}`} className={`muhurta-page__window-card ${index === 0 ? 'is-primary' : ''}`.trim()}>
                  <span>{index === 0 ? 'Best of the day' : index === 1 ? 'Backup' : 'Another option'}</span>
                  <h3>{item.title}</h3>
                  <p>{item.note}</p>
                </article>
              ))}
            </div>

            <div className="muhurta-page__timeline-grid">
              {detailViewModel.timeline.length ? detailViewModel.timeline.map((item) => (
                <button
                  key={item.id}
                  type="button"
                  className={`muhurta-page__timeline-item muhurta-page__timeline-item--${item.tone}${selectedBlock?.index === item.id ? ' is-selected' : ''}`.trim()}
                  onClick={() => {
                    const block = (detailPayload?.blocks || []).find((entry) => entry.index === item.id);
                    if (block) setSelectedBlock(block);
                  }}
                >
                  <strong>{item.time}</strong>
                  <span>{item.title}</span>
                  <small>{item.note}</small>
                </button>
              )) : (
                <article className="muhurta-page__timeline-empty">Timing blocks are still loading.</article>
              )}
            </div>
          </>
        )}
      </section>
    </section>
  );
}

export default MuhurtaPage;
