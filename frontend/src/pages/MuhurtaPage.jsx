import HoverGlossaryTerm from '../components/UI/HoverGlossaryTerm';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { CONSUMER_BEST_TIME_OPTIONS } from '../consumer/consumerViewModels';
import { useTemporalContext } from '../context/useTemporalContext';
import { addMonths, useBestTimePlanner, windowRangeLabel } from '../hooks/useBestTimePlanner';
import { formatProductDate } from '../utils/productDateTime';
import './MuhurtaPage.css';

function monthLabel(dateValue, state) {
  return formatProductDate(dateValue, { month: 'long', year: 'numeric' }, state) || dateValue;
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
  const {
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
    detailPayload,
    loadingCalendar,
    loadingDetail,
    calendarError,
    detailError,
    rankedDates,
    currentMonthCells,
    nextMonthCells,
    detailViewModel,
  } = useBestTimePlanner({ state });

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
              <strong>
                <HoverGlossaryTerm
                  passive
                  term={summary?.best_window?.name || (summary?.has_viable_window ? 'Good date' : 'No strong pick')}
                  label={summary?.best_window?.name || (summary?.has_viable_window ? 'Good date' : 'No strong pick')}
                />
              </strong>
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
                  <span>
                    <HoverGlossaryTerm passive term={item.title} label={item.title} />
                  </span>
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
