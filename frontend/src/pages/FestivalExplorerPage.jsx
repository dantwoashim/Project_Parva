import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { CONSUMER_FESTIVAL_FILTERS } from '../consumer/consumerViewModels';
import { useMemberContext } from '../context/useMemberContext';
import { useTemporalContext } from '../context/useTemporalContext';
import { useDialogA11y } from '../hooks/useDialogA11y';
import { useFestivalExplorerData } from '../hooks/useFestivalExplorerData';
import { useCopy } from '../i18n/useCopy';
import { trackEvent } from '../services/analytics';
import './FestivalExplorerPage.css';

function posterClass(item) {
  return `explorer-poster explorer-poster--${item?.artKey || 'lamp'}`.trim();
}

function FestivalCard({ item, emphasis = 'default', source = 'festival_card' }) {
  if (!item) return null;

  return (
    <Link
      to={item.href}
      className={`explorer-card explorer-card--${emphasis}`.trim()}
      onClick={() => trackEvent('festival_opened', { festival_id: item.id, source })}
    >
      <div className={posterClass(item)}>
        <span>{item.title}</span>
      </div>
      <div className="explorer-card__copy">
        {(item.badges?.length || item.countdown) ? (
          <div className="explorer-card__badges">
            {(item.badges || []).map((badge) => (
              <span key={`${item.id}-${badge}`}>{badge}</span>
            ))}
            {item.countdown ? <span key={`${item.id}-countdown`}>{item.countdown}</span> : null}
          </div>
        ) : null}
        <h3>{item.title}</h3>
        <p className="explorer-card__meta">{item.dateLabel}</p>
        {item.statusNote ? <p className="explorer-card__status-note">{item.statusNote}</p> : null}
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
  const [sort, setSort] = useState('chronological');
  const [filtersOpen, setFiltersOpen] = useState(false);
  const { dialogRef } = useDialogA11y(filtersOpen, () => setFiltersOpen(false));
  const allFestivalsRef = useRef(null);
  const { loading, error, viewModel } = useFestivalExplorerData({
    date: state.date,
    timezone: state.timezone,
    savedFestivals: memberState.savedFestivals,
    search,
    category,
    region,
    sort,
  });

  const scrollToAllFestivals = () => {
    allFestivalsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const hasActiveFilters = Boolean(search.trim() || category || region || sort !== 'chronological');

  const resetFilters = () => {
    setSearch('');
    setCategory('');
    setRegion('');
    setSort('chronological');
  };

  if (loading) {
    return (
      <section className="explorer-page animate-fade-in-up consumer-route consumer-route--explorer">
        <div className="skeleton explorer-hero-skeleton" />
        <div className="skeleton explorer-gallery__lead-skeleton" />
        <div className="skeleton explorer-gallery__card-skeleton" />
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
          <p className="explorer-eyebrow">Festivals</p>
          <h1>Closest observances first.</h1>
          <p>{viewModel.subtitle}</p>
        </div>

        <div className="explorer-hero__actions">
          <label className="ink-input explorer-search">
            <span>Search observances</span>
            <input
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Bisket Jatra, Buddha Jayanti, Indra..."
            />
          </label>
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
          {hasActiveFilters ? (
            <button type="button" className="btn btn-secondary explorer-reset" onClick={resetFilters}>
              Clear filters
            </button>
          ) : null}
        </div>
      </header>

      <section className="explorer-closest">
        <div className="explorer-section-head">
          <div>
            <p className="explorer-eyebrow">Closest observances</p>
            <h2>Start with what is happening now, then what comes next.</h2>
            <p>
              {viewModel.activeToday.length
                ? `${viewModel.activeToday.length} observance${viewModel.activeToday.length === 1 ? ' is' : 's are'} active today.`
                : 'No observance is active today, so the next dates lead this list.'}
            </p>
          </div>
          <button type="button" className="btn btn-secondary" onClick={scrollToAllFestivals}>
            See all festivals
          </button>
        </div>

        {viewModel.closestLead ? (
          <div className="explorer-closest__grid">
            <FestivalCard item={viewModel.closestLead} emphasis="lead" source="closest_lead" />
            <div className="explorer-closest__stack">
              {viewModel.closestSupporting.map((item, index) => (
                <FestivalCard
                  key={item.id}
                  item={item}
                  emphasis="compact"
                  source={`closest_supporting_${index + 1}`}
                />
              ))}
            </div>
          </div>
        ) : (
          <article className="explorer-card explorer-card--empty">
            <div className="explorer-card__copy">
              <h3>{viewModel.emptyState.title}</h3>
              <p>{viewModel.emptyState.body}</p>
            </div>
          </article>
        )}
      </section>

      <section ref={allFestivalsRef} className="explorer-ribbon">
        <div className="explorer-ribbon__head">
          <div>
            <p className="explorer-eyebrow">All festivals</p>
            <h2>From today forward, grouped by month.</h2>
          </div>
          <button type="button" className="btn btn-secondary" onClick={() => setFiltersOpen(true)}>
            {copy('festivalExplorer.filters.more')}
          </button>
        </div>

        <div className="explorer-months">
          {viewModel.chapters.length ? viewModel.chapters.map((chapter, chapterIndex) => (
            <section key={chapter.id} className="explorer-month">
              <div className="explorer-month__head">
                <p className="explorer-eyebrow">{chapter.label}</p>
              </div>
              <div className="explorer-month__grid">
                <FestivalCard item={chapter.lead} emphasis={chapterIndex === 0 ? 'feature' : 'default'} source={`month_${chapter.id}_lead`} />
                <div className="explorer-month__stack">
                  {chapter.items.map((item, index) => (
                    <FestivalCard
                      key={item.id}
                      item={item}
                      emphasis="compact"
                      source={`month_${chapter.id}_${index + 1}`}
                    />
                  ))}
                </div>
              </div>
            </section>
          )) : (
            <article className="explorer-card explorer-card--empty">
              <div className="explorer-card__copy">
                <h3>{viewModel.emptyState.title}</h3>
                <p>{viewModel.emptyState.body}</p>
              </div>
            </article>
          )}
        </div>

        {viewModel.unresolvedMatches?.length ? (
          <section className="explorer-unresolved" aria-label="Verification still in progress">
            <div className="explorer-month__head">
              <p className="explorer-eyebrow">Still being verified</p>
            </div>
            <div className="explorer-month__stack">
              {viewModel.unresolvedMatches.map((item) => (
                <FestivalCard key={item.id} item={item} emphasis="compact" source="unresolved_match" />
              ))}
            </div>
          </section>
        ) : null}
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
              <div className="explorer-sheet__actions">
                {hasActiveFilters ? (
                  <button type="button" className="btn btn-secondary" onClick={resetFilters}>
                    Clear filters
                  </button>
                ) : null}
                <button
                  type="button"
                  className="btn btn-secondary"
                  data-dialog-initial-focus="true"
                  onClick={() => setFiltersOpen(false)}
                >
                  {copy('festivalExplorer.filters.close')}
                </button>
              </div>
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
                  <option value="chronological">{copy('festivalExplorer.sort.soonest')}</option>
                  <option value="popular">Popular</option>
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
