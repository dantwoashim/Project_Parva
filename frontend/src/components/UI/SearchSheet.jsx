import { useDeferredValue, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { countdownLabel } from '../../consumer/viewModels/shared';
import { searchInlineGlossary } from '../../data/inlineGlossary';
import { useMemberContext } from '../../context/useMemberContext';
import { todayIso } from '../../context/temporalContextState';
import { useTemporalContext } from '../../context/useTemporalContext';
import { useDialogA11y } from '../../hooks/useDialogA11y';
import { useCopy } from '../../i18n/useCopy';
import { getSearchCommands } from '../../navigation/routeManifest';
import { festivalAPI, placesAPI } from '../../services/api';
import { trackEvent } from '../../services/analytics';
import { addIsoDays } from '../../utils/isoDate';
import './SearchSheet.css';

function reminderRoute(reminder) {
  if (reminder?.kind === 'festival' && reminder.id?.startsWith('festival:')) {
    return `/festivals/${reminder.id.split(':')[1]}`;
  }
  return '/saved';
}

function scoreMatch(item, query) {
  const normalizedQuery = String(query || '').trim().toLowerCase();
  if (!normalizedQuery) return 1;

  const label = String(item.label || '').toLowerCase();
  const haystack = `${item.label || ''} ${item.keywords || ''} ${item.meta || ''} ${item.description || ''}`.toLowerCase();
  if (label === normalizedQuery) return 120;
  if (label.startsWith(normalizedQuery)) return 95;
  if (haystack.includes(normalizedQuery)) return 72;

  const tokens = normalizedQuery.split(/\s+/).filter(Boolean);
  if (tokens.length && tokens.every((token) => haystack.includes(token))) {
    return 48;
  }

  return -1;
}

function sortScored(items, query) {
  return items
    .map((item) => ({ ...item, score: scoreMatch(item, query) }))
    .filter((item) => item.score >= 0)
    .sort((left, right) => right.score - left.score || left.label.localeCompare(right.label));
}

function buildMemberResults(state, copy) {
  return [
    ...(state.savedFestivals || []).map((festival) => ({
      id: `saved-festival-${festival.id}`,
      to: `/festivals/${festival.id}`,
      label: festival.name,
      keywords: `${festival.name} ${festival.category || ''} saved observance`,
      kind: copy('search.kind.savedFestival'),
      meta: festival.startDate || 'Saved observance',
      description: 'Open a saved observance directly.',
      section: 'saved',
    })),
    ...(state.savedPlaces || []).map((place, index) => ({
      id: `saved-place-${place.id || index}`,
      to: '/my-place',
      label: place.label || 'Saved place',
      keywords: `${place.label || ''} ${place.timezone || ''} saved place`,
      kind: copy('search.kind.savedPlace'),
      meta: place.timezone || 'Saved place',
      description: 'Jump back to a saved place context.',
      section: 'saved',
    })),
    ...(state.reminders || []).map((reminder, index) => ({
      id: `reminder-${reminder.id || index}`,
      to: reminderRoute(reminder),
      label: reminder.title || 'Reminder',
      keywords: `${reminder.title || ''} reminder ${reminder.date || ''}`,
      kind: copy('search.kind.reminder'),
      meta: reminder.date || 'Saved reminder',
      description: 'Open the page linked to this reminder.',
      section: 'saved',
    })),
    ...(state.savedReadings || []).map((reading, index) => ({
      id: `reading-${reading.id || index}`,
      to: '/birth-reading',
      label: reading.title || 'Saved reading',
      keywords: `${reading.title || ''} ${reading.summary || ''} saved reading`,
      kind: copy('search.kind.savedReading'),
      meta: 'Birth Reading',
      description: 'Reopen a saved birth-reading session.',
      section: 'saved',
    })),
    ...(state.integrations || []).map((integration, index) => ({
      id: `integration-${integration.id || index}`,
      to: '/integrations',
      label: integration.title || 'Integration',
      keywords: `${integration.title || ''} ${integration.platform || ''} integration calendar`,
      kind: copy('search.kind.integration'),
      meta: integration.platform || 'Calendar integration',
      description: 'Open the integration setup surface.',
      section: 'saved',
    })),
  ];
}

function groupResults(items) {
  const groups = [
    { id: 'pages', title: 'Pages' },
    { id: 'saved', title: 'Saved' },
    { id: 'festivals', title: 'Festival matches' },
    { id: 'places', title: 'Place matches' },
    { id: 'terms', title: 'What this means' },
  ];

  return groups
    .map((group) => ({
      ...group,
      items: items.filter((item) => item.section === group.id),
    }))
    .filter((group) => group.items.length);
}

export function SearchSheet({ open, onClose }) {
  const navigate = useNavigate();
  const { state: memberState } = useMemberContext();
  const { state: temporalState, setLocation, setTimezone } = useTemporalContext();
  const { copy } = useCopy();
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const [remoteResults, setRemoteResults] = useState({
    festivals: [],
    places: [],
    loading: false,
    error: null,
  });
  const deferredQuery = useDeferredValue(query);
  const { dialogRef } = useDialogA11y(open, onClose);

  const localResults = useMemo(() => {
    const normalized = deferredQuery.trim();
    const commandResults = getSearchCommands(copy, { includeSupport: Boolean(normalized) }).map((item) => ({
      ...item,
      id: `page-${item.to}`,
      description: item.meta || 'Open this page',
      section: 'pages',
    }));
    const savedResults = buildMemberResults(memberState, copy);
    const glossaryResults = searchInlineGlossary(normalized, 5).map((entry) => ({
      id: `term-${entry.term}`,
      to: entry.route,
      label: entry.term,
      keywords: `${entry.term} ${entry.kind} ${entry.meaning}`,
      kind: 'Glossary term',
      meta: entry.kind,
      description: entry.meaning,
      section: 'terms',
    }));

    if (!normalized) {
      return [
        ...commandResults.slice(0, 5),
        ...savedResults.slice(0, 3),
      ];
    }

    return [
      ...sortScored(commandResults, normalized),
      ...sortScored(savedResults, normalized),
      ...sortScored(glossaryResults, normalized).slice(0, 4),
    ];
  }, [copy, deferredQuery, memberState]);

  useEffect(() => {
    if (!open) {
      setQuery('');
      setActiveIndex(0);
      setRemoteResults({ festivals: [], places: [], loading: false, error: null });
      return;
    }

    const normalized = deferredQuery.trim();
    if (normalized.length < 2) {
      setRemoteResults({ festivals: [], places: [], loading: false, error: null });
      return;
    }

    let cancelled = false;
    const anchorDate = todayIso(temporalState.timezone);

    setRemoteResults((current) => ({
      ...current,
      loading: true,
      error: null,
    }));

    async function loadRemote() {
      const [festivalResponse, placeResponse] = await Promise.allSettled([
        festivalAPI.getTimelineEnvelope({
          from: anchorDate,
          to: addIsoDays(anchorDate, 365),
          qualityBand: 'all',
          search: normalized,
          sort: 'upcoming',
          lang: temporalState.language || 'en',
        }),
        placesAPI.search({ query: normalized, limit: 6 }),
      ]);

      if (cancelled) return;

      const festivals = festivalResponse.status === 'fulfilled'
        ? ((festivalResponse.value?.data?.groups || []).flatMap((group) => group.items || []).slice(0, 4).map((item) => ({
            id: `festival-${item.id}`,
            to: `/festivals/${item.id}`,
            label: item.display_name || item.name,
            keywords: `${item.name || ''} ${item.name_nepali || ''} ${item.category || ''} ${item.summary || ''}`,
            kind: 'Festival',
            meta: [item.start_date, countdownLabel(item.start_date)].filter(Boolean).join(' · '),
            description: item.summary || item.date_status_note || 'Open the observance detail.',
            section: 'festivals',
          })))
        : [];

      const places = placeResponse.status === 'fulfilled'
        ? ((placeResponse.value?.items || []).slice(0, 4).map((item, index) => ({
            id: `place-${item.label}-${index}`,
            to: '/my-place',
            label: item.label,
            keywords: `${item.label} ${item.timezone} ${item.source || ''}`,
            kind: 'Place',
            meta: [item.timezone, item.source].filter(Boolean).join(' · '),
            description: 'Apply this place and open My Place with its local timezone.',
            section: 'places',
            place: item,
          })))
        : [];

      setRemoteResults({
        festivals,
        places,
        loading: false,
        error:
          festivalResponse.status === 'rejected' && placeResponse.status === 'rejected'
            ? 'Search could not reach live festival or place results right now.'
            : null,
      });
    }

    void loadRemote();
    return () => {
      cancelled = true;
    };
  }, [deferredQuery, open, temporalState.language, temporalState.timezone]);

  const sections = useMemo(
    () => groupResults([...localResults, ...remoteResults.festivals, ...remoteResults.places]),
    [localResults, remoteResults.festivals, remoteResults.places],
  );

  const flatResults = useMemo(
    () => sections.flatMap((section) => section.items),
    [sections],
  );

  useEffect(() => {
    if (activeIndex >= flatResults.length) {
      setActiveIndex(flatResults.length ? 0 : -1);
    } else if (flatResults.length && activeIndex < 0) {
      setActiveIndex(0);
    }
  }, [activeIndex, flatResults.length]);

  useEffect(() => {
    setActiveIndex(0);
  }, [deferredQuery]);

  async function handleSelect(item) {
    if (item.place) {
      setLocation({
        latitude: item.place.latitude,
        longitude: item.place.longitude,
      });
      setTimezone(item.place.timezone);
    }

    trackEvent('path_card_selected', {
      destination: item.to,
      source: 'search',
      kind: item.kind,
      section: item.section,
    });
    navigate(item.to);
    onClose();
  }

  if (!open) return null;

  const normalizedQuery = deferredQuery.trim();

  return (
    <div className="search-sheet__overlay" role="presentation" onClick={onClose}>
      <aside
        ref={dialogRef}
        className="search-sheet"
        role="dialog"
        aria-modal="true"
        aria-labelledby="search-sheet-title"
        onClick={(event) => event.stopPropagation()}
      >
        <div className="search-sheet__header">
          <div>
            <p className="search-sheet__eyebrow">{copy('common.search')}</p>
            <h2 id="search-sheet-title">{copy('search.title')}</h2>
            <p className="search-sheet__intro">
              Jump to pages, places, festivals, and quick meanings without leaving the current view.
            </p>
          </div>
          <button type="button" className="search-sheet__close" onClick={onClose}>
            {copy('common.close')}
          </button>
        </div>

        <label className="ink-input search-sheet__input">
          <span>{copy('search.inputLabel')}</span>
          <div className="search-sheet__input-row">
            <span className="material-symbols-outlined">search</span>
            <input
              type="search"
              autoFocus
              data-dialog-initial-focus="true"
              placeholder={copy('search.placeholder')}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              onKeyDown={(event) => {
                if (!flatResults.length) return;
                if (event.key === 'ArrowDown') {
                  event.preventDefault();
                  setActiveIndex((current) => (current + 1) % flatResults.length);
                } else if (event.key === 'ArrowUp') {
                  event.preventDefault();
                  setActiveIndex((current) => (current <= 0 ? flatResults.length - 1 : current - 1));
                } else if (event.key === 'Enter' && activeIndex >= 0) {
                  event.preventDefault();
                  void handleSelect(flatResults[activeIndex]);
                }
              }}
            />
            {query ? (
              <button type="button" className="search-sheet__clear" onClick={() => setQuery('')}>
                Clear
              </button>
            ) : null}
          </div>
        </label>

        <div className="search-sheet__status-row">
          <span className="search-sheet__hint">Ctrl/Cmd + K or /</span>
          <span className="search-sheet__hint">
            {remoteResults.loading
              ? 'Searching live festivals and places…'
              : normalizedQuery
                ? `${flatResults.length} result${flatResults.length === 1 ? '' : 's'}`
                : 'Start typing to search everything'}
          </span>
        </div>

        <div className="search-sheet__results" role="list">
          {sections.map((section) => (
            <section key={section.id} className="search-sheet__section">
              <div className="search-sheet__section-head">
                <span>{section.title}</span>
                <small>{section.items.length}</small>
              </div>
              <div className="search-sheet__section-list">
                {section.items.map((item) => {
                  const flattenedIndex = flatResults.findIndex((entry) => entry.id === item.id);
                  return (
                    <button
                      key={item.id}
                      type="button"
                      className={`search-sheet__result ${flattenedIndex === activeIndex ? 'is-active' : ''}`.trim()}
                      role="listitem"
                      onMouseEnter={() => setActiveIndex(flattenedIndex)}
                      onClick={() => {
                        void handleSelect(item);
                      }}
                    >
                      <div className="search-sheet__result-main">
                        <span className="search-sheet__result-kind">{item.kind}</span>
                        <div className="search-sheet__result-copy">
                          <div className="search-sheet__result-line">
                            <strong>{item.label}</strong>
                            {item.meta ? <small>{item.meta}</small> : null}
                          </div>
                          {(normalizedQuery.length >= 2 || item.section === 'terms') && item.description ? (
                            <p>{item.description}</p>
                          ) : null}
                        </div>
                        <span className="material-symbols-outlined search-sheet__result-arrow" aria-hidden="true">
                          arrow_outward
                        </span>
                      </div>
                    </button>
                  );
                })}
              </div>
            </section>
          ))}
          {!sections.length && !remoteResults.loading ? (
            <p className="search-sheet__empty">{copy('search.empty')}</p>
          ) : null}
          {remoteResults.error ? <p className="search-sheet__empty">{remoteResults.error}</p> : null}
        </div>
      </aside>
    </div>
  );
}

export default SearchSheet;
