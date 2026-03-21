import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  CONSUMER_FESTIVAL_FILTERS,
  buildConsumerFestivalsViewModel,
} from '../consumer/consumerViewModels';
import { useMemberContext } from '../context/useMemberContext';
import { useTemporalContext } from '../context/useTemporalContext';
import { useDialogA11y } from '../hooks/useDialogA11y';
import { useCopy } from '../i18n/useCopy';
import { festivalAPI } from '../services/api';
import { trackEvent } from '../services/analytics';
import { describeSupportError } from '../services/errorFormatting';
import './FestivalExplorerPage.css';

function addDays(base, days) {
  const date = new Date(`${base}T00:00:00`);
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
}

function posterClass(item) {
  return `explorer-poster explorer-poster--${item?.artKey || 'lamp'}`.trim();
}

function dedupeFestivalItems(items = []) {
  const seen = new Set();
  return items.filter((item) => {
    const key = item?.id || item?.href || item?.title;
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function FeaturedFestival({ item, lead = false, source = 'chapter' }) {
  if (!item) return null;
  return (
    <Link
      to={item.href}
      className={`explorer-card ${lead ? 'is-lead' : ''}`.trim()}
      onClick={() => trackEvent('festival_opened', { festival_id: item.id, source })}
    >
      <div className={posterClass(item)}>
        <span>{item.title}</span>
      </div>
      <div className="explorer-card__copy">
        <h3>{item.title}</h3>
        <p className="explorer-card__meta">{item.dateLabel}</p>
        <p>{item.summary}</p>
      </div>
    </Link>
  );
}

export function FestivalExplorerPage() {
  const { state } = useTemporalContext();
  const { state: memberState } = useMemberContext();
  const { copy } = useCopy();
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [region, setRegion] = useState('');
  const [sort, setSort] = useState('recommended');
  const [filtersOpen, setFiltersOpen] = useState(false);
  const { dialogRef } = useDialogA11y(filtersOpen, () => setFiltersOpen(false));
  const [payload, setPayload] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fromDate = state.date;
  const toDate = useMemo(() => addDays(state.date, 180), [state.date]);

  useEffect(() => {
    let cancelled = false;

    async function loadTimeline() {
      setLoading(true);
      setError(null);

      try {
        const envelope = await festivalAPI.getTimelineEnvelope({
          from: fromDate,
          to: toDate,
          qualityBand: 'computed',
          category: category || undefined,
          region: region || undefined,
          search: search.trim() || undefined,
          sort: sort || undefined,
          lang: state.language,
        });

        if (!cancelled) {
          setPayload(envelope.data || null);
        }
      } catch (err) {
        if (!cancelled) {
          setPayload(null);
          setError(describeSupportError(err, 'Festival timeline is unavailable right now.'));
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadTimeline();
    return () => {
      cancelled = true;
    };
  }, [category, fromDate, region, search, sort, state.language, toDate]);

  const viewModel = useMemo(
    () => buildConsumerFestivalsViewModel({
      payload,
      search,
      category,
      savedFestivals: memberState.savedFestivals,
      temporalState: {
        language: state.language,
        timezone: state.timezone,
      },
    }),
    [payload, search, category, memberState.savedFestivals, state.language, state.timezone],
  );

  const galleryItems = useMemo(() => {
    const lead = viewModel.featured;
    const supporting = [...viewModel.supporting];
    if (viewModel.chapters[0]?.items?.length) {
      supporting.push(...viewModel.chapters[0].items.slice(0, Math.max(0, 4 - supporting.length)));
    }
    return { lead, supporting: dedupeFestivalItems(supporting).slice(0, 4) };
  }, [viewModel]);

  if (loading) {
    return (
      <section className="explorer-page animate-fade-in-up consumer-route consumer-route--explorer">
        <div className="skeleton explorer-hero-skeleton" />
        <div className="explorer-gallery">
          <div className="skeleton explorer-gallery__lead-skeleton" />
          <div className="explorer-gallery__stack">
            {Array.from({ length: 4 }).map((_, index) => (
              <div key={index} className="skeleton explorer-gallery__card-skeleton" />
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="explorer-page animate-fade-in-up consumer-route consumer-route--explorer">
        <article className="explorer-error ink-card" role="alert">
          <p className="explorer-eyebrow">Festivals</p>
          <h1>Festival guidance is temporarily unavailable.</h1>
          <p>{error}</p>
        </article>
      </section>
    );
  }

  return (
    <section className="explorer-page animate-fade-in-up consumer-route consumer-route--explorer">
      <header className="explorer-hero">
        <div className="explorer-hero__copy">
          <p className="explorer-eyebrow">Sacred Calendars</p>
          <h1>
            <span>Festival</span>
            <em>Explorer</em>
          </h1>
          <p>{viewModel.subtitle}</p>
        </div>

        <div className="explorer-hero__actions">
          {CONSUMER_FESTIVAL_FILTERS.map((option) => (
            <button
              key={option.value || 'all'}
              type="button"
              className={`explorer-pill ${category === option.value ? 'is-active' : ''}`.trim()}
              onClick={() => {
                setCategory(option.value);
                trackEvent('path_card_selected', {
                  surface: 'festivals',
                  filter: option.value || 'all_observances',
                });
              }}
            >
              {option.label}
            </button>
          ))}
        </div>
      </header>

      <section className="explorer-gallery">
        <FeaturedFestival item={galleryItems.lead} lead source="lead_gallery" />
        <div className="explorer-gallery__stack">
          {galleryItems.supporting.map((item, index) => (
            <FeaturedFestival key={item.id} item={item} source={`gallery_${index + 1}`} />
          ))}
        </div>
      </section>

      <section className="explorer-cta">
        <div>
          <h2>Never miss a sacred moment.</h2>
          <p>Sync the Panchanga with your personal calendar and receive ritual guidance based on your precise location.</p>
        </div>
        <Link to="/integrations" className="btn btn-primary">Sync My Calendar</Link>
      </section>

      <section className="explorer-ribbon">
        <div className="explorer-ribbon__head">
          <div>
            <p className="explorer-eyebrow">Browse all</p>
            <h2>Seasonal observance ribbon</h2>
          </div>
          <button type="button" className="btn btn-secondary" onClick={() => setFiltersOpen(true)}>
            {copy('festivalExplorer.filters.more')}
          </button>
        </div>

        <div className="explorer-ribbon__grid">
          {viewModel.timelineCards.length ? viewModel.timelineCards.map((item) => (
            <FeaturedFestival key={item.id} item={item} source="ribbon" />
          )) : (
            <article className="explorer-card">
              <div className="explorer-card__copy">
                <h3>{viewModel.emptyState.title}</h3>
                <p>{viewModel.emptyState.body}</p>
              </div>
            </article>
          )}
        </div>
      </section>

      {filtersOpen ? (
        <div className="explorer-sheet__overlay" role="presentation" onClick={() => setFiltersOpen(false)}>
          <aside
            ref={dialogRef}
            className="explorer-sheet"
            role="dialog"
            aria-modal="true"
            aria-labelledby="festival-explorer-filters-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="explorer-sheet__header">
              <div>
                <p className="explorer-eyebrow">{copy('festivalExplorer.filters.eyebrow')}</p>
                <h2 id="festival-explorer-filters-title">{copy('festivalExplorer.filters.title')}</h2>
              </div>
              <button
                type="button"
                className="btn btn-secondary"
                data-dialog-initial-focus="true"
                onClick={() => setFiltersOpen(false)}
              >
                {copy('festivalExplorer.filters.close')}
              </button>
            </div>

            <div className="explorer-filters">
              <label className="ink-input explorer-control explorer-control--wide">
                <span>{copy('festivalExplorer.filters.searchLabel')}</span>
                <input
                  type="search"
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder={copy('festivalExplorer.filters.searchPlaceholder')}
                />
              </label>

              <label className="ink-input explorer-control">
                <span>{copy('festivalExplorer.filters.category')}</span>
                <select value={category} onChange={(event) => setCategory(event.target.value)}>
                  {CONSUMER_FESTIVAL_FILTERS.map((chip) => (
                    <option key={chip.value || 'all'} value={chip.value}>{chip.label}</option>
                  ))}
                </select>
              </label>

              <label className="ink-input explorer-control">
                <span>{copy('festivalExplorer.filters.region')}</span>
                <select value={region} onChange={(event) => setRegion(event.target.value)}>
                  <option value="">{copy('festivalExplorer.region.all')}</option>
                  {viewModel.facets.regions.map((item) => (
                    <option key={item.value} value={item.value}>{item.label || item.value}</option>
                  ))}
                </select>
              </label>

              <label className="ink-input explorer-control">
                <span>{copy('festivalExplorer.filters.sort')}</span>
                <select value={sort} onChange={(event) => setSort(event.target.value)}>
                  <option value="recommended">{copy('festivalExplorer.sort.recommended')}</option>
                  <option value="soonest">{copy('festivalExplorer.sort.soonest')}</option>
                  <option value="latest">{copy('festivalExplorer.sort.latest')}</option>
                </select>
              </label>
            </div>
          </aside>
        </div>
      ) : null}
    </section>
  );
}

export default FestivalExplorerPage;
