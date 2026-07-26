import {
  useEffect,
  useMemo,
  useRef,
  useState,
  Link,
  festivalAPI,
  todayIso,
  apiHref,
  describeSupportError,
  defaultFestivalFilters,
  fallbackFestivalCategories,
  fallbackFestivalRegions,
  festivalMonths,
  festivalQualityOptions,
  festivalSortOptions,
  readableCategory,
  AppChrome,
  PageHero,
} from '../ExperienceCommon.jsx';
import { AnimatePresence, m as Motion } from 'motion/react';
import {
  ArrowDownUp,
  ArrowUpRight,
  Bookmark,
  BookmarkCheck,
  CalendarPlus,
  CalendarRange,
  Check,
  ChevronDown,
  ChevronUp,
  Copy,
  Download,
  Search,
  SlidersHorizontal,
  Tags,
  X,
} from 'lucide-react';
import { useParvaToast } from '../../motion/ParvaToastContext';

import {
  FestivalArtwork,
  QualityDots,
  resolveFestivalVisual,
  addDaysIso,
  formatFestivalDateRange,
  normalizeFestivalTimelineRows,
  groupFestivalRowsByMonth,
  festivalDateRail,
  monthFilterValue,
  activeFestivalFilterCount,
  normalizeFacetOptions,
  buildExpandedFestivalStory,
  buildCalendarFeedUrl,
  readSavedFestivalIds,
  writeSavedFestivalIds,
  buildFestivalEvidenceUrl,
  festivalOccurrenceKey,
} from './FestivalUtils.jsx';

export function RedesignFestivals() {
  const { notify } = useParvaToast();
  const [search, setSearch] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState(defaultFestivalFilters);
  const [draftFilters, setDraftFilters] = useState(defaultFestivalFilters);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [expandedKey, setExpandedKey] = useState('');
  const [savedIds, setSavedIds] = useState(() => new Set(readSavedFestivalIds()));
  const [copiedId, setCopiedId] = useState('');
  const [timelineEnvelope, setTimelineEnvelope] = useState(null);
  const [timelineLoading, setTimelineLoading] = useState(true);
  const [timelineRefreshing, setTimelineRefreshing] = useState(false);
  const [timelineError, setTimelineError] = useState(null);
  const [detailCache, setDetailCache] = useState({});
  const [visibleLimit, setVisibleLimit] = useState(16);
  const hasLoadedTimelineRef = useRef(false);

  const fromDate = useMemo(() => todayIso('Asia/Kathmandu'), []);
  const toDate = useMemo(() => addDaysIso(fromDate, 420), [fromDate]);

  useEffect(() => {
    const timeoutId = window.setTimeout(() => setSearchQuery(search.trim()), 250);
    return () => window.clearTimeout(timeoutId);
  }, [search]);

  useEffect(() => {
    let cancelled = false;
    const bootstrapping = !hasLoadedTimelineRef.current;

    async function loadTimeline() {
      setTimelineLoading(bootstrapping);
      setTimelineRefreshing(!bootstrapping);
      setTimelineError(null);

      try {
        const envelope = await festivalAPI.getTimelineEnvelope({
          from: fromDate,
          to: toDate,
          qualityBand: filters.qualityBand,
          category: filters.category === 'All' ? undefined : filters.category,
          region: filters.region === 'All' ? undefined : filters.region,
          search: searchQuery || undefined,
          sort: filters.sort,
          lang: 'en',
        });
        if (!cancelled) {
          setTimelineEnvelope(envelope);
          hasLoadedTimelineRef.current = true;
        }
      } catch (reason) {
        if (!cancelled) {
          setTimelineError(describeSupportError(reason, 'Festival timeline is unavailable right now.'));
          setTimelineEnvelope(null);
        }
      } finally {
        if (!cancelled) {
          setTimelineLoading(false);
          setTimelineRefreshing(false);
        }
      }
    }

    loadTimeline();
    return () => {
      cancelled = true;
    };
  }, [filters.category, filters.qualityBand, filters.region, filters.sort, fromDate, searchQuery, toDate]);

  const timelineData = timelineEnvelope?.data || {};
  const allFestivalRows = useMemo(() => normalizeFestivalTimelineRows(timelineData.groups || []), [timelineData.groups]);
  const monthOptions = useMemo(() => {
    const months = Array.from(new Set(allFestivalRows.map(monthFilterValue).filter(Boolean)));
    const ordered = festivalMonths.filter((monthName) => monthName === 'All' || months.includes(monthName));
    const extras = months.filter((monthName) => !ordered.includes(monthName));
    return [...ordered, ...extras];
  }, [allFestivalRows]);
  const categoryOptions = useMemo(
    () => normalizeFacetOptions(timelineData.facets?.categories, fallbackFestivalCategories),
    [timelineData.facets],
  );
  const regionOptions = useMemo(
    () => normalizeFacetOptions(timelineData.facets?.regions, fallbackFestivalRegions),
    [timelineData.facets],
  );
  const visibleFestivals = useMemo(() => {
    const rows = filters.month === 'All'
      ? allFestivalRows
      : allFestivalRows.filter((item) => monthFilterValue(item) === filters.month);
    return rows;
  }, [allFestivalRows, filters.month]);
  const renderedFestivals = useMemo(
    () => visibleFestivals.slice(0, visibleLimit),
    [visibleFestivals, visibleLimit],
  );
  const groupedVisibleFestivals = useMemo(
    () => groupFestivalRowsByMonth(renderedFestivals),
    [renderedFestivals],
  );
  const activeFilterCount = activeFestivalFilterCount(filters, search);
  const expandedFestival = visibleFestivals.find((item) => festivalOccurrenceKey(item) === expandedKey) || null;
  const expandedDetail = expandedFestival ? detailCache[expandedFestival.id] : null;

  useEffect(() => {
    writeSavedFestivalIds(savedIds);
  }, [savedIds]);

  useEffect(() => {
    if (!expandedKey) return;
    const festival = allFestivalRows.find((item) => festivalOccurrenceKey(item) === expandedKey);
    if (!festival) return;
    const detailId = festival.id;
    if (detailCache[detailId]?.data || detailCache[detailId]?.loading) return;
    const year = festival.start_date ? new Date(`${festival.start_date}T00:00:00`).getFullYear() : undefined;
    let cancelled = false;

    setDetailCache((current) => ({
      ...current,
      [detailId]: { loading: true, error: null, data: current[detailId]?.data || null, meta: current[detailId]?.meta || null },
    }));

    festivalAPI.getByIdEnvelope(detailId, year, 'authority_compare')
      .then((envelope) => {
        if (cancelled) return;
        setDetailCache((current) => ({
          ...current,
          [detailId]: { loading: false, error: null, data: envelope.data, meta: envelope.meta },
        }));
      })
      .catch((reason) => {
        if (cancelled) return;
        setDetailCache((current) => ({
          ...current,
          [detailId]: {
            loading: false,
            error: describeSupportError(reason, 'Detailed festival profile is unavailable right now.'),
            data: null,
            meta: null,
          },
        }));
      });

    return () => {
      cancelled = true;
    };
  }, [allFestivalRows, detailCache, expandedKey]);

  const openFilters = () => {
    setDraftFilters(filters);
    setFiltersOpen(true);
  };

  const applyFilters = () => {
    setFilters(draftFilters);
    setExpandedKey('');
    setVisibleLimit(16);
    setFiltersOpen(false);
    notify('Filters applied', { detail: 'The festival timeline has been refreshed.' });
  };

  const resetFilters = () => {
    setDraftFilters(defaultFestivalFilters);
    setFilters(defaultFestivalFilters);
    setExpandedKey('');
    setVisibleLimit(16);
  };

  const toggleSave = (festival) => {
    const wasSaved = savedIds.has(festival.id);
    setSavedIds((current) => {
      const next = new Set(current);
      if (next.has(festival.id)) {
        next.delete(festival.id);
      } else {
        next.add(festival.id);
      }
      return next;
    });
    notify(wasSaved ? 'Festival removed from saved' : 'Festival saved', {
      detail: festival.displayName,
      tone: wasSaved ? 'info' : 'success',
    });
  };

  const copyFestivalLink = async (festival) => {
    const link = `${window.location.origin}/festivals/${festival.id}`;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard API unavailable');
      await navigator.clipboard.writeText(link);
      setCopiedId(festival.id);
      notify('Festival link copied', { detail: festival.displayName });
      window.setTimeout(() => setCopiedId(''), 1800);
    } catch {
      if (typeof window.prompt === 'function') window.prompt('Copy festival link', link);
      notify('Clipboard unavailable', { detail: 'Use the copy field shown by your browser.', tone: 'warning' });
    }
  };

  return (
    <AppChrome>
      <main className="page-shell festivals-page">
        <PageHero
          title="Festivals"
          body="Scan Nepal festivals by date, status, region, and source confidence without losing the calendar thread."
          action={(
            <div className="hero-actions festival-hero-actions">
              <label className="festival-search-control">
                <span><Search aria-hidden="true" /> Search</span>
                <input
                  value={search}
                  onChange={(event) => {
                    setSearch(event.target.value);
                    setVisibleLimit(16);
                  }}
                  placeholder="Dashain, Ekadashi, Jatra..."
                />
              </label>
              <button type="button" className="filter-open-button" onClick={openFilters}>
                <SlidersHorizontal aria-hidden="true" /> Filters {activeFilterCount ? <b>{activeFilterCount}</b> : null}
              </button>
              <a className="primary-button subscribe-calendar-button" href={apiHref('/feeds/all.ics?years=1&download=1')}>
                <CalendarPlus aria-hidden="true" /> Subscribe calendar
              </a>
              <label className="sort-control">
                <span><ArrowDownUp aria-hidden="true" /> Sort by</span>
                <select
                  value={filters.sort}
                  onChange={(event) => {
                    setFilters((current) => ({ ...current, sort: event.target.value }));
                    setVisibleLimit(16);
                  }}
                >
                  {festivalSortOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
                </select>
              </label>
            </div>
          )}
        />

        <section className="festival-results-shell">
          <div
            className="festival-status-bar"
            aria-label={`${visibleFestivals.length} festival${visibleFestivals.length === 1 ? '' : 's'} in this view`}
          >
            <div>
              <strong>{visibleFestivals.length}</strong>
              <span>festival{visibleFestivals.length === 1 ? '' : 's'} in this view</span>
            </div>
            <p>
              {timelineRefreshing ? 'Refreshing calendar...' : `Showing ${filters.month === 'All' ? 'all BS months' : filters.month}`}
              {filters.category !== 'All' ? ` · ${readableCategory(filters.category)}` : ''}
              {filters.qualityBand !== 'all' ? ` · ${readableCategory(filters.qualityBand)}` : ''}
            </p>
          </div>

          {timelineLoading ? (
            <section className="festival-empty-state panel">
              <p className="eyebrow">Loading live catalog</p>
              <h2>Preparing the festival calendar.</h2>
              <p>Dates, source state, and observance windows are being verified for this view.</p>
            </section>
          ) : timelineError ? (
            <section className="festival-empty-state panel">
              <p className="eyebrow">Timeline unavailable</p>
              <h2>Festival data could not be loaded.</h2>
              <p>{timelineError}</p>
              <button type="button" onClick={() => setFilters((current) => ({ ...current }))}>Try again</button>
            </section>
          ) : visibleFestivals.length ? (
            <div className="festival-list-view" aria-label="Festival list">
              {groupedVisibleFestivals.map((group) => (
                <section key={group.key} className="festival-month-group" aria-label={`${group.label} festivals`}>
                  <div className="festival-month-heading">
                    <h2>{group.label}</h2>
                    <span>{group.items.length} observance{group.items.length === 1 ? '' : 's'}</span>
                  </div>
                  {group.items.map((festival) => {
                    const occurrenceKey = festivalOccurrenceKey(festival);
                    return (
                      <FestivalListCard
                        key={occurrenceKey}
                        occurrenceKey={occurrenceKey}
                        festival={festival}
                        expanded={expandedKey === occurrenceKey}
                        detail={expandedKey === occurrenceKey ? expandedDetail : null}
                        saved={savedIds.has(festival.id)}
                        copied={copiedId === festival.id}
                        onToggle={() => setExpandedKey((current) => (current === occurrenceKey ? '' : occurrenceKey))}
                        onSave={() => toggleSave(festival)}
                        onCopy={() => copyFestivalLink(festival)}
                      />
                    );
                  })}
                </section>
              ))}
              {renderedFestivals.length < visibleFestivals.length ? (
                <div className="festival-load-more">
                  <button
                    type="button"
                    onClick={() => setVisibleLimit((current) => current + 12)}
                  >
                    <ChevronDown aria-hidden="true" />
                    <span>
                      <strong>Show more festivals</strong>
                      <small>{visibleFestivals.length - renderedFestivals.length} remain in this view</small>
                    </span>
                  </button>
                </div>
              ) : null}
            </div>
          ) : (
            <section className="festival-empty-state panel">
              <p className="eyebrow">No matching observances</p>
              <h2>Nothing matches this exact view.</h2>
              <p>Clear filters or search a broader family such as “jatra”, “ekadashi”, or “puja”.</p>
              <button type="button" onClick={resetFilters}>Reset filters</button>
            </section>
          )}
        </section>

        {filtersOpen ? (
          <FestivalFilterSheet
            draftFilters={draftFilters}
            setDraftFilters={setDraftFilters}
            monthOptions={monthOptions}
            categoryOptions={categoryOptions}
            regionOptions={regionOptions}
            resultCount={visibleFestivals.length}
            onApply={applyFilters}
            onReset={resetFilters}
            onClose={() => setFiltersOpen(false)}
          />
        ) : null}
      </main>
    </AppChrome>
  );
}

function FestivalFilterSheet({
  draftFilters,
  setDraftFilters,
  monthOptions,
  categoryOptions,
  regionOptions,
  resultCount,
  onApply,
  onReset,
  onClose,
}) {
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  return (
    <Motion.div
      className="festival-filter-layer"
      role="dialog"
      aria-modal="true"
      aria-label="Festival filters"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.16 }}
    >
      <Motion.button
        type="button"
        className="festival-filter-scrim"
        onClick={onClose}
        aria-label="Close festival filters"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      />
      <Motion.aside
        className="festival-filter-sheet"
        initial={{ opacity: 0, y: 16, scale: 0.985 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 10, scale: 0.985 }}
        transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="festival-filter-heading">
          <div>
            <p className="eyebrow">Refine list</p>
            <h2>Festival filters</h2>
          </div>
          <button type="button" className="close-button" onClick={onClose} aria-label="Close filters">
            <X aria-hidden="true" />
          </button>
        </div>

        <section className="filter-block">
          <div className="filter-title">
            <CalendarRange aria-hidden="true" />
            <strong>Month (BS)</strong>
          </div>
          <div className="chip-grid">
            {monthOptions.map((item) => (
              <button
                key={item}
                type="button"
                className={draftFilters.month === item ? 'is-selected' : ''}
                onClick={() => setDraftFilters((current) => ({ ...current, month: item }))}
              >
                {item}
              </button>
            ))}
          </div>
        </section>

        <section className="filter-block">
          <div className="filter-title">
            <Tags aria-hidden="true" />
            <strong>Category</strong>
          </div>
          <div className="type-filter-list">
            <button
              type="button"
              className={draftFilters.category === 'All' ? 'is-selected' : ''}
              onClick={() => setDraftFilters((current) => ({ ...current, category: 'All' }))}
            >
              All categories
            </button>
            {categoryOptions.map((item) => (
              <button
                key={item.value}
                type="button"
                className={draftFilters.category === item.value ? 'is-selected' : ''}
                onClick={() => setDraftFilters((current) => ({ ...current, category: item.value }))}
              >
                {item.label}{item.count ? ` (${item.count})` : ''}
              </button>
            ))}
          </div>
        </section>

        <section className="filter-block select-filter-block">
          <label>
            <span>Region</span>
            <select
              value={draftFilters.region}
              onChange={(event) => setDraftFilters((current) => ({ ...current, region: event.target.value }))}
            >
              <option value="All">All regions</option>
              {regionOptions.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
            </select>
          </label>
          <label>
            <span>Source state</span>
            <select
              value={draftFilters.qualityBand}
              onChange={(event) => setDraftFilters((current) => ({ ...current, qualityBand: event.target.value }))}
            >
              {festivalQualityOptions.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
            </select>
          </label>
          <label>
            <span>Sort</span>
            <select
              value={draftFilters.sort}
              onChange={(event) => setDraftFilters((current) => ({ ...current, sort: event.target.value }))}
            >
              {festivalSortOptions.map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
            </select>
          </label>
        </section>

        <section className="filter-summary-card">
          <span>Current result estimate</span>
          <strong>{resultCount}</strong>
          <small>Filters apply to the verified festival calendar. Month is refined from BS month labels.</small>
        </section>

        <div className="festival-filter-actions">
          <button type="button" onClick={onReset}>Reset</button>
          <button type="button" onClick={onClose}>Cancel</button>
          <button type="button" className="primary-button" onClick={onApply}>
            <Check aria-hidden="true" /> Apply filters
          </button>
        </div>
      </Motion.aside>
    </Motion.div>
  );
}

function FestivalListCard({ festival, occurrenceKey, expanded, detail, saved, copied, onToggle, onSave, onCopy }) {
  const visual = resolveFestivalVisual(festival);
  const detailFestival = detail?.data?.festival || {};
  const detailDates = detail?.data?.dates || {};
  const related = detail?.data?.nearby_festivals || [];
  const source = festival.source;
  const story = buildExpandedFestivalStory(festival, detail?.data || {});
  const rituals = story.rituals;
  const detailPending = expanded && !detail;
  const artworkFestival = { ...festival, ...detailFestival, images: detailFestival.images || festival.images };
  const panelId = `festival-detail-${String(occurrenceKey || festivalOccurrenceKey(festival)).replace(/[^a-z0-9_-]+/gi, '-')}`;
  const dateRail = festivalDateRail(festival);

  return (
    <article className={`festival-list-card tone-${visual.tone} ${expanded ? 'is-expanded' : ''}`}>
      <button
        type="button"
        className="festival-list-card__button"
        aria-expanded={expanded}
        aria-controls={panelId}
        onClick={onToggle}
      >
        <span className="festival-date-rail">
          <strong>{dateRail.day}</strong>
          <small>{dateRail.month}</small>
        </span>
        <span className="festival-list-card__media">
          <FestivalArtwork festival={artworkFestival} />
        </span>
        <span className="festival-list-card__body">
          <span className="festival-list-card__main">
            <span className="festival-list-card__kicker">
              <em>{festival.categoryLabel}</em>
              <em>{festival.durationLabel}</em>
              <em>{source.label}</em>
            </span>
            <strong>{festival.displayName}</strong>
            {festival.name_nepali ? <small>{festival.name_nepali}</small> : null}
            <span>{festival.summary}</span>
          </span>
          <span className="festival-list-card__dates">
            <b>{festival.bsLabel}</b>
            <span>{festival.adLabel}</span>
            <em>{festival.countdownLabel}</em>
          </span>
          <span className="festival-list-card__expand">
            {expanded ? <ChevronUp aria-hidden="true" /> : <ChevronDown aria-hidden="true" />}
            {expanded ? 'Hide details' : 'View details'}
          </span>
        </span>
      </button>

      {!expanded ? (
        <div className="festival-list-card__quick-actions" aria-label={`${festival.displayName} quick actions`}>
          <button type="button" onClick={onSave}>
            {saved ? <BookmarkCheck aria-hidden="true" /> : <Bookmark aria-hidden="true" />}
            {saved ? 'Following' : 'Follow'}
          </button>
          <a href={buildCalendarFeedUrl(festival.id)}><CalendarPlus aria-hidden="true" /> Calendar</a>
          <Link to={`/festivals/${festival.id}`}>Open <ArrowUpRight aria-hidden="true" /></Link>
        </div>
      ) : null}

      <AnimatePresence initial={false}>
      {expanded ? (
        <Motion.section
          id={panelId}
          className="festival-expanded-panel"
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: 'auto' }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.28, ease: [0.22, 1, 0.36, 1] }}
        >
          {detail?.error ? (
            <div className="festival-detail-loading">
              <p className="eyebrow">Detail unavailable</p>
              <h3>{detail.error}</h3>
              <p>The list date and source state above are still available.</p>
            </div>
          ) : (
            <>
              <div className="festival-expanded-lead">
                <div>
                  <p className="eyebrow">Festival detail</p>
                  <h3>{story.title}</h3>
                  <p>{story.lead}</p>
                </div>
                <dl>
                  <div><dt>Public window</dt><dd>{formatFestivalDateRange(detailDates.start_date || festival.start_date, detailDates.end_date || festival.end_date)}</dd></div>
                  <div><dt>BS date</dt><dd>{festival.bsLabel}</dd></div>
                  <div><dt>Source state</dt><dd>{source.label}</dd></div>
                  <div><dt>Regional focus</dt><dd>{festival.regions.length ? festival.regions.join(', ') : 'Nepal-focused'}</dd></div>
                </dl>
              </div>

              {detailPending || detail?.loading ? (
                <div className="festival-detail-loading is-inline">
                  <p className="eyebrow">Opening source profile</p>
                  <h3>Showing the calendar profile while detailed evidence loads.</h3>
                </div>
              ) : null}

              <div className="festival-story-grid">
                {story.sections.map((section) => (
                  <section key={section.title}>
                    <strong>{section.title}</strong>
                    <p>{section.body}</p>
                  </section>
                ))}
              </div>

              <div className="festival-expanded-grid">
                <section>
                  <p className="eyebrow">Ritual structure</p>
                  {rituals.length ? (
                    <ol className="festival-ritual-steps">
                      {rituals.map((ritual) => (
                        <li key={ritual.id}>
                          <span>{ritual.day}</span>
                          <strong>{ritual.title}</strong>
                          <p>{ritual.body}</p>
                        </li>
                      ))}
                    </ol>
                  ) : (
                    <p className="festival-muted-note">Structured ritual steps are still being normalized for this observance.</p>
                  )}
                </section>

                <section>
                  <p className="eyebrow">Provenance</p>
                  <dl className="festival-fact-list">
                    {story.facts.map(([label, value]) => (
                      <div key={label}>
                        <dt>{label}</dt>
                        <dd>{value}</dd>
                      </div>
                    ))}
                  </dl>
                  <div className="festival-source-card">
                    <QualityDots value={source.score} />
                    <strong>{source.label}</strong>
                    <p>{detailDates.calculation_method || festival.date_status_note || 'Resolved through the Parva public festival timeline.'}</p>
                  </div>
                  {related.length ? (
                    <div className="festival-related-list">
                      <strong>Nearby observances</strong>
                      {related.slice(0, 3).map((item) => (
                        <Link key={item.id} to={`/festivals/${item.id}`}>{item.name || item.display_name || item.id}</Link>
                      ))}
                    </div>
                  ) : (
                    <p className="festival-muted-note">No nearby observances were returned for this window.</p>
                  )}
                </section>
              </div>

              <footer className="festival-list-card__actions" aria-label={`${festival.displayName} actions`}>
                <button type="button" onClick={onSave}>
                  {saved ? <BookmarkCheck aria-hidden="true" /> : <Bookmark aria-hidden="true" />}
                  {saved ? 'Saved' : 'Save'}
                </button>
                <button type="button" onClick={onCopy}>
                  {copied ? <Check aria-hidden="true" /> : <Copy aria-hidden="true" />}
                  {copied ? 'Copied' : 'Copy link'}
                </button>
                <a href={buildCalendarFeedUrl(festival.id)}><CalendarPlus aria-hidden="true" /> Add to calendar</a>
                <a href={buildFestivalEvidenceUrl(festival)}><Download aria-hidden="true" /> Export evidence</a>
              </footer>
            </>
          )}
        </Motion.section>
      ) : null}
      </AnimatePresence>
    </article>
  );
}

