import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { festivalAPI } from '../services/api';
import { useTemporalContext } from '../context/useTemporalContext';
import { TimelineRibbon } from '../components/TimelineRibbon/TimelineRibbon';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { trackEvent } from '../services/analytics';
import './FestivalExplorerPage.css';

function addDays(base, days) {
  const date = new Date(`${base}T00:00:00`);
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

function monthKey(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  if (Number.isNaN(date.valueOf())) return '';
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
}

function formatDate(dateString) {
  if (!dateString) return 'Date in details';
  const date = new Date(dateString);
  if (Number.isNaN(date.valueOf())) return dateString;
  return date.toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' });
}

const CATEGORY_CHIPS = [
  { value: '', label: 'All traditions' },
  { value: 'national', label: 'National' },
  { value: 'newari', label: 'Newari' },
  { value: 'hindu', label: 'Hindu' },
  { value: 'buddhist', label: 'Buddhist' },
  { value: 'regional', label: 'Regional' },
];

export function FestivalExplorerPage() {
  const { state } = useTemporalContext();
  const [fromDate, setFromDate] = useState(state.date);
  const [windowDays, setWindowDays] = useState(180);
  const [category, setCategory] = useState('');
  const [region, setRegion] = useState('');
  const [search, setSearch] = useState('');
  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filtersOpen, setFiltersOpen] = useState(false);

  const toDate = useMemo(() => addDays(fromDate, windowDays), [fromDate, windowDays]);
  const allItems = useMemo(() => (payload?.groups || []).flatMap((group) => group.items || []), [payload]);
  const featuredItems = allItems.slice(0, 3);
  const leadFestival = featuredItems[0] || null;
  const supportingFestivals = featuredItems.slice(1);
  const currentMonthKey = useMemo(() => monthKey(fromDate), [fromDate]);
  const currentMonthGroup = useMemo(
    () => (payload?.groups || []).find((group) => group.month_key === currentMonthKey) || payload?.groups?.[0] || null,
    [currentMonthKey, payload],
  );
  const monthItems = currentMonthGroup?.items?.slice(0, 4) || [];

  useEffect(() => {
    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);
      try {
        const envelope = await festivalAPI.getTimelineEnvelope({
          from: fromDate,
          to: toDate,
          qualityBand: 'computed',
          category: category || undefined,
          region: region || undefined,
          search: search || undefined,
          lang: state.language,
        });

        if (!cancelled) {
          setPayload(envelope.data);
          setMeta(envelope.meta);
        }
      } catch (err) {
        if (!cancelled) {
          setPayload(null);
          setMeta(null);
          setError(err.message || 'Failed to load festival timeline');
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load();
    return () => {
      cancelled = true;
    };
  }, [fromDate, toDate, category, region, search, state.language]);

  function openFestival(item, source) {
    trackEvent('festival_opened', {
      festival_id: item.id,
      source,
    });
  }

  return (
    <section className="explorer-page animate-fade-in-up">
      <header className="explorer-hero editorial-card">
        <div className="explorer-hero__copy">
          <p className="landing-eyebrow">Festivals</p>
          <h1>Follow observances through meaning first, then the wider calendar.</h1>
          <p className="explorer-hero__sub">
            Start with the next featured observance, keep the rest of this month in view, and open the full timeline only when you want more range.
          </p>
        </div>
        <div className="explorer-hero__actions">
          <button type="button" className="btn btn-secondary" onClick={() => setFiltersOpen(true)}>
            Open filters
          </button>
          <EvidenceDrawer
            title="Festivals"
            intro="This drawer keeps the festival timeline method, language profile, and data-availability context nearby without leading the page with system detail."
            methodRef={meta?.method || 'Festival timeline profile'}
            confidenceNote={meta?.confidence?.level || meta?.confidence || 'Computed festival guidance'}
            placeUsed="Nepal-focused calendar profile"
            computedForDate={`${fromDate} to ${toDate}`}
            availability={[
              { label: 'Featured observance', available: Boolean(leadFestival), note: 'The lead card uses the first available observance in the visible range.' },
              { label: 'This month chapter', available: Boolean(monthItems.length), note: 'Monthly discovery should stay visible even when the wider timeline is long.' },
              { label: 'Full timeline', available: Boolean(payload?.groups?.length), note: 'Timeline chapters remain available below the fold for browsing.' },
            ]}
            meta={meta}
            traceFallbackId={payload?.calculation_trace_id}
          />
        </div>
      </header>

      <section className="explorer-chip-row">
        {CATEGORY_CHIPS.map((chip) => (
          <button
            key={chip.label}
            type="button"
            className={`explorer-chip ${category === chip.value ? 'is-active' : ''}`.trim()}
            onClick={() => setCategory(chip.value)}
          >
            {chip.label}
          </button>
        ))}
      </section>

      {filtersOpen ? (
        <div className="explorer-sheet__overlay" role="presentation" onClick={() => setFiltersOpen(false)}>
          <aside
            className="explorer-sheet ink-card"
            role="dialog"
            aria-modal="true"
            aria-label="Festival filters"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="explorer-sheet__header">
              <div>
                <p className="landing-eyebrow">Filters</p>
                <h2>Tune the calendar without leading with a dense form.</h2>
              </div>
              <button type="button" className="btn btn-secondary btn-sm" onClick={() => setFiltersOpen(false)}>
                Close
              </button>
            </div>
            <div className="explorer-filters explorer-filters--sheet">
              <label className="ink-input explorer-control">
                <span>From</span>
                <input type="date" value={fromDate} onChange={(event) => setFromDate(event.target.value)} />
              </label>
              <label className="ink-input explorer-control">
                <span>Window</span>
                <select value={windowDays} onChange={(event) => setWindowDays(Number(event.target.value))}>
                  <option value={90}>90 days</option>
                  <option value={180}>180 days</option>
                  <option value={365}>365 days</option>
                </select>
              </label>
              <label className="ink-input explorer-control">
                <span>Region</span>
                <input value={region} onChange={(event) => setRegion(event.target.value)} placeholder="Kathmandu Valley" />
              </label>
              <label className="ink-input explorer-control explorer-control--wide">
                <span>Search</span>
                <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Dashain, Indra Jatra, Shivaratri..." />
              </label>
            </div>
          </aside>
        </div>
      ) : null}

      {loading ? (
        <div className="explorer-grid">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="skeleton explorer-skeleton" />
          ))}
        </div>
      ) : null}

      {!loading && error ? (
        <div className="ink-card explorer-error" role="alert">
          <h2>Festival guidance is unavailable right now</h2>
          <p>{error}</p>
        </div>
      ) : null}

      {!loading && !error ? (
        <>
          <section className="explorer-featured">
            {leadFestival ? (
              <Link
                to={`/festivals/${leadFestival.id}`}
                className="ink-card explorer-featured__lead"
                onClick={() => openFestival(leadFestival, 'featured')}
              >
                <span className="today-page__eyebrow">Featured next observance</span>
                <h2>{leadFestival.display_name || leadFestival.name}</h2>
                <p>
                  Open the observance when you want the story, ritual arc, and date guidance together instead of buried inside a dense calendar wall.
                </p>
                <div className="explorer-featured__lead-meta">
                  <span>{leadFestival.category || 'Festival'}</span>
                  <strong>{formatDate(leadFestival.start_date)}</strong>
                </div>
              </Link>
            ) : (
              <article className="ink-card explorer-featured__lead explorer-featured__lead--empty">
                <span className="today-page__eyebrow">Featured next observance</span>
                <h2>The next observance will appear here when the current festival range is available.</h2>
                <p>Use filters if you want to widen the range or search a specific tradition.</p>
              </article>
            )}

            <div className="explorer-featured__stack">
              {supportingFestivals.map((item) => (
                <Link
                  key={`${item.id}-${item.start_date}`}
                  to={`/festivals/${item.id}`}
                  className="ink-card explorer-featured__card"
                  onClick={() => openFestival(item, 'supporting')}
                >
                  <span className="today-page__eyebrow">Also coming soon</span>
                  <h3>{item.display_name || item.name}</h3>
                  <p>{item.category || 'Festival'}</p>
                  <small>{formatDate(item.start_date)}</small>
                </Link>
              ))}
            </div>
          </section>

          <section className="ink-card explorer-month">
            <div className="explorer-section-header">
              <div>
                <p className="today-page__eyebrow">Coming this month</p>
                <h2>{currentMonthGroup?.month_label || 'Current festival chapter'}</h2>
              </div>
            </div>
            {monthItems.length ? (
              <div className="explorer-month__grid">
                {monthItems.map((item, index) => (
                  <Link
                    key={`${item.id}-${item.start_date}-${index}`}
                    to={`/festivals/${item.id}`}
                    className={`explorer-month__item ${index === 0 ? 'is-lead' : ''}`.trim()}
                    onClick={() => openFestival(item, 'month_chapter')}
                  >
                    <strong>{item.display_name || item.name}</strong>
                    <span>{formatDate(item.start_date)}</span>
                    <p>{item.category || 'Festival'}</p>
                  </Link>
                ))}
              </div>
            ) : (
              <p className="muted">This month chapter will appear here when the selected range returns observances.</p>
            )}
          </section>

          <section className="explorer-timeline">
            <div className="explorer-section-header">
              <div>
                <p className="today-page__eyebrow">Full timeline</p>
                <h2>Browse the wider calendar</h2>
              </div>
            </div>
            <TimelineRibbon groups={payload?.groups || []} />
          </section>
        </>
      ) : null}
    </section>
  );
}

export default FestivalExplorerPage;
