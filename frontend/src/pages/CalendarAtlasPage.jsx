import { useEffect, useMemo, useState } from 'react';
import { calendarAPI } from '../services/api';
import { useTemporalContext } from '../context/TemporalContext';
import './CalendarAtlasPage.css';

const MONTHS = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

function currentGregorian() {
  const now = new Date();
  return {
    year: now.getFullYear(),
    month: now.getMonth() + 1,
  };
}

function formatWeekday(day, lang = 'en') {
  if (!day) return '—';
  if (lang === 'ne') {
    const map = {
      Sunday: 'आइतबार', Monday: 'सोमबार', Tuesday: 'मंगलबार', Wednesday: 'बुधबार',
      Thursday: 'बिहीबार', Friday: 'शुक्रबार', Saturday: 'शनिबार',
    };
    return map[day] || day;
  }
  return day;
}

export function CalendarAtlasPage() {
  const now = useMemo(() => currentGregorian(), []);
  const { state } = useTemporalContext();
  const [year, setYear] = useState(now.year);
  const [month, setMonth] = useState(now.month);

  const [payload, setPayload] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const data = await calendarAPI.getDualMonth(year, month);
        if (!cancelled) setPayload(data);
      } catch (err) {
        if (!cancelled) {
          setPayload(null);
          setError(err.message || 'Failed to load dual calendar month');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [year, month]);

  const yearOptions = useMemo(() => {
    const min = payload?.supported_range?.gregorian_min_year ?? now.year - 200;
    const max = payload?.supported_range?.gregorian_max_year ?? now.year + 200;
    const options = [];
    for (let y = max; y >= min; y -= 1) options.push(y);
    return options;
  }, [payload, now.year]);

  function shiftMonth(delta) {
    const next = new Date(Date.UTC(year, month - 1 + delta, 1));
    setYear(next.getUTCFullYear());
    setMonth(next.getUTCMonth() + 1);
  }

  return (
    <section className="calendar-atlas-page animate-fade-in-up">
      <header className="calendar-atlas-hero ink-card">
        <div>
          <p className="calendar-atlas-eyebrow">Dual Calendar Atlas</p>
          <h1>
            Gregorian + Bikram Sambat
          </h1>
          <p>
            Explore monthly date mappings across a ±200 year window with Nepali and Gregorian alignment.
          </p>
        </div>

        <div className="calendar-atlas-controls">
          <button type="button" className="btn btn-secondary" onClick={() => shiftMonth(-1)}>
            ← Previous
          </button>
          <label className="ink-input">
            <span>Year</span>
            <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
              {yearOptions.map((y) => (
                <option key={y} value={y}>{y}</option>
              ))}
            </select>
          </label>
          <label className="ink-input">
            <span>Month</span>
            <select value={month} onChange={(e) => setMonth(Number(e.target.value))}>
              {MONTHS.map((name, idx) => (
                <option key={name} value={idx + 1}>{name}</option>
              ))}
            </select>
          </label>
          <button type="button" className="btn btn-secondary" onClick={() => shiftMonth(1)}>
            Next →
          </button>
        </div>
      </header>

      {loading && (
        <div className="calendar-atlas-grid calendar-atlas-grid--loading">
          {Array.from({ length: 12 }).map((_, i) => (
            <div key={i} className="skeleton calendar-atlas-skeleton" />
          ))}
        </div>
      )}

      {!loading && error && (
        <div className="ink-card calendar-atlas-error" role="alert">
          <h3>Could not load calendar atlas</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && payload && (
        <>
          <section className="calendar-atlas-meta ink-card">
            <h2>{payload.month_label}</h2>
            <p>
              Supported Gregorian range: {payload.supported_range?.gregorian_min_year} to {payload.supported_range?.gregorian_max_year}
            </p>
          </section>

          <section className="calendar-atlas-grid" aria-label="Dual calendar monthly mapping">
            {(payload.days || []).map((entry) => (
              <article key={entry.gregorian.iso} className="ink-card calendar-atlas-day clickable">
                <div className="calendar-atlas-day__ad">
                  <strong>{entry.gregorian.day}</strong>
                  <span>{MONTHS[entry.gregorian.month - 1]} {entry.gregorian.year}</span>
                  <small>{formatWeekday(entry.gregorian.weekday, state.language)}</small>
                </div>
                <div className="calendar-atlas-day__bs text-nepali">
                  <strong>{entry.bikram_sambat.day}</strong>
                  <span>{entry.bikram_sambat.month_name} {entry.bikram_sambat.year}</span>
                </div>
              </article>
            ))}
          </section>
        </>
      )}
    </section>
  );
}

export default CalendarAtlasPage;
