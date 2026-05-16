import {
  useEffect,
  useState,
  Link,
  placesAPI,
  useTemporalContext,
  usePersonalPlaceBundle,
  useTodayBundle,
  apiHref,
  describeSupportError,
  formatBsDate,
  formatCoordinates,
  formatIsoDate,
  formatTimeRange,
  formatTimeReference,
  humanMethodLabel,
  normalizeMuhurtaWindow,
  placeLabelFromLocation,
  readableCategory,
  supportReference,
  Confidence,
  InfoCell,
  ScoreRing,
  SourceDots,
  TimelineList,
  VerificationStrip,
  buildPanchangaItems,
  buildDayFacts,
  AppChrome,
  PageHero,
} from './ExperienceCommon.jsx';
import {
  countdownText,
  resolveFestivalVisual,
} from './festival/FestivalUtils.jsx';

export function RedesignToday() {
  const { state } = useTemporalContext();
  const {
    loading,
    error,
    compass,
    compassMeta,
    muhurta,
    muhurtaMeta,
    onDateFestivals,
    upcomingFestivals,
  } = useTodayBundle({
    date: state.date,
    latitude: state.location?.latitude,
    longitude: state.location?.longitude,
    timezone: state.timezone,
    upcomingDays: 90,
  });
  const bsLabel = compass?.bikram_sambat ? formatBsDate(compass.bikram_sambat) : state.date;
  const weekday = compass?.signals?.vaara?.name_english || formatIsoDate(state.date, { weekday: 'long', month: undefined, year: undefined });
  const panchangaItems = buildPanchangaItems(compass);
  const dayFacts = buildDayFacts(compass);
  const liveWindows = (muhurta?.blocks || []).slice(0, 8).map(normalizeMuhurtaWindow);
  const bestWindows = liveWindows.filter((window) => window.type === 'good').slice(0, 3);
  const timelineItems = [
    compass?.horizon?.sunrise ? { time: formatTimeReference(compass.horizon.sunrise), title: 'Sunrise', type: 'warm', icon: '☼' } : null,
    ...(liveWindows.slice(0, 3).map((window) => ({ time: window.time, title: window.name, type: window.type, icon: '✣' }))),
    compass?.horizon?.sunset ? { time: formatTimeReference(compass.horizon.sunset), title: 'Sunset', type: 'warm', icon: '☀' } : null,
  ].filter(Boolean);
  const displayTimelineItems = timelineItems.map((item) => ({
    ...item,
    icon: item.title === 'Sunrise' ? 'Sun' : item.title === 'Sunset' ? 'Set' : 'Window',
  }));
  const placeLabel = compass?.location_context?.place_title || placeLabelFromLocation(state.location);
  const qualityScore = Math.max(0, Math.min(100, Math.round(Number(muhurta?.best_window?.score ?? 0))));
  const sourceLabel = humanMethodLabel(compassMeta?.method || compass?.engine?.method || compass?.engine?.method_profile);
  const festivalCards = (onDateFestivals.length ? onDateFestivals : upcomingFestivals).slice(0, 3);
  const bestWindowLabel = muhurta?.best_window?.name || bestWindows[0]?.name || 'Checking windows';
  const bestWindowTime = muhurta?.best_window
    ? formatTimeRange(muhurta.best_window.start, muhurta.best_window.end)
    : bestWindows[0]?.time || 'Loading';

  return (
    <AppChrome>
      <main className="page-shell today-page">
        <PageHero
          eyebrow="Today"
          title={`Today in ${placeLabel}`}
          body={`${bsLabel} - ${weekday}. Source-aware BS date logic, panchanga signals, festivals, and timing windows.`}
          action={(
            <Link className="location-mini" to="/my-place">
              <span>{placeLabel}</span>
              <small>{formatIsoDate(state.date)} · {state.timezone}</small>
            </Link>
          )}
        />
        <VerificationStrip
          items={[
            { label: 'Current timing window', value: bestWindowLabel, meta: bestWindowTime },
            { label: 'Place', value: placeLabel, meta: state.timezone },
            { label: 'Calculation source', value: sourceLabel, meta: supportReference(compassMeta?.request_id) },
            { label: 'Next action', value: 'View full panchanga', meta: 'Calendar-ready' },
          ]}
        />
        {error ? (
          <section className="festival-empty-state panel" role="alert">
            <p className="eyebrow">Today unavailable</p>
            <h2>{error}</h2>
            <p>The public API demo may be waking up. Retry in a few seconds if the first request times out.</p>
          </section>
        ) : null}
        <section className="today-main">
          <div className="today-stack">
            <section className="panel panchanga-panel">
              <div className="panel-heading">
              <div>
                  <p className="eyebrow">Panchanga for {placeLabel}</p>
                </div>
                <Link className="text-link compact-link" to="/panchanga">View full panchanga ›</Link>
              </div>
              {loading && !compass ? <p className="festival-muted-note">Loading panchanga for the selected place...</p> : null}
              <div className="panchanga-grid">
                {panchangaItems.map((item) => <InfoCell key={item.label} {...item} />)}
              </div>
              <div className="fact-row">
                {dayFacts.map(([label, value]) => <InfoCell key={label} label={label} value={value} />)}
                <div className="fact-confidence">
                  <span>{sourceLabel}</span>
                  <SourceDots active={5} />
                </div>
              </div>
            </section>
            <section className="panel observance-panel">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">Upcoming observances</p>
                  <h2>Next on the calendar</h2>
                </div>
                <Link className="ghost-button" to="/festivals">View all</Link>
              </div>
              <div className="observance-row">
                {festivalCards.length ? festivalCards.map((festival) => {
                  const visual = resolveFestivalVisual(festival);
                  return (
                  <Link key={festival.id} className={`observance-card tone-${visual.tone}`} to={`/festivals/${festival.id}`}>
                    <span>{visual.icon}</span>
                    <strong>{festival.name || festival.display_name || festival.id}</strong>
                    <small>{festival.start_date ? countdownText(festival.start_date) : readableCategory(festival.quality_band || festival.category)}</small>
                  </Link>
                  );
                }) : <p className="festival-muted-note">No observances were returned for this API window.</p>}
              </div>
            </section>
            <section className="panel best-overview">
              <div className="panel-heading">
              <div>
                  <p className="eyebrow">Recommended window</p>
                  <h2>{muhurta?.best_window?.name || 'Window pending'}</h2>
                </div>
                <Link className="text-link compact-link" to="/best-time">How it works</Link>
              </div>
              <div className="window-tabs" aria-label="Intent shortcuts">
                {['All', 'Worship', 'Travel', 'Business', 'Learning'].map((item) => (
                  <Link key={item} to="/best-time">{item}</Link>
                ))}
              </div>
              <div className="best-window-row">
                {bestWindows.length ? bestWindows.map((window) => (
                  <Link key={window.id} className={`mini-window is-${window.type}`} to="/best-time">
                    <span>✣</span>
                    <strong>{window.name}</strong>
                    <small>{window.time}</small>
                  </Link>
                )) : <p className="festival-muted-note">No auspicious windows were returned for this date.</p>}
              </div>
              <Link className="primary-button best-time-cta" to="/best-time">Open Best Time</Link>
              <p className="panel-note">{humanMethodLabel(muhurtaMeta?.method, 'Timings are ranked for the selected place and intent.')}</p>
            </section>
          </div>
          <aside className="side-rail">
            <section className="panel timeline-panel">
              <div className="panel-heading tight">
                <p className="eyebrow">Day timeline</p>
                <strong>{state.date}</strong>
              </div>
              <TimelineList compact items={displayTimelineItems} />
            </section>
            <section className="panel quality-panel">
              <p className="eyebrow">Day quality</p>
              <div className="quality-row">
                <ScoreRing value={qualityScore} label={muhurta?.best_window?.quality || 'API'} />
                <ul className="quality-legend">
                  <li><span className="dot good" />Auspicious <strong>{liveWindows.filter((item) => item.type === 'good').length}</strong></li>
                  <li><span className="dot warm" />Neutral <strong>{liveWindows.filter((item) => item.type === 'warm').length}</strong></li>
                  <li><span className="dot bad" />Avoid <strong>{liveWindows.filter((item) => item.type === 'bad').length}</strong></li>
                </ul>
              </div>
            </section>
            <section className="panel source-panel">
              <div className="panel-heading tight">
                <p className="eyebrow">Source & calculation</p>
              </div>
              <dl className="source-list">
                <div><dt>Calendar system</dt><dd>{humanMethodLabel(compass?.engine?.method_profile, 'Nepal calendar')}</dd></div>
                <div><dt>Calculation mode</dt><dd>{humanMethodLabel(compass?.engine?.ephemeris_mode || compass?.engine?.method)}</dd></div>
                <div><dt>Location</dt><dd>{placeLabel}</dd></div>
                <div><dt>Evidence</dt><dd>{supportReference(compassMeta?.request_id)}</dd></div>
              </dl>
              <Link className="text-link" to="/truth-lab">Review evidence</Link>
            </section>
            <section className="panel conversion-panel">
              <p className="eyebrow">Use this day</p>
              <h2>Turn the result into a plan.</h2>
              <p>Every important result should be usable, portable, and source-aware.</p>
              <div>
                <Link className="primary-button" to="/best-time">Choose safest window</Link>
                <a className="ghost-button" href={apiHref('/feeds/all.ics?years=1&download=1')}>Subscribe calendar</a>
                <Link className="ghost-button" to="/truth-lab">Export evidence</Link>
              </div>
            </section>
          </aside>
        </section>
      </main>
    </AppChrome>
  );
}

export function RedesignMyPlace() {
  const { state, setLocation, setTimezone } = useTemporalContext();
  const [query, setQuery] = useState('');
  const [placesState, setPlacesState] = useState({ loading: false, error: '', items: [] });
  const [selected, setSelected] = useState(null);
  const activeLocation = selected || {
    label: placeLabelFromLocation(state.location),
    latitude: state.location?.latitude,
    longitude: state.location?.longitude,
    timezone: state.timezone,
    source: 'temporal_context',
  };
  const activePlaceName = placeLabelFromLocation(activeLocation);
  const coordinateStatus = formatCoordinates(activeLocation);
  const queryReady = query.trim().length >= 2;
  const placeBundle = usePersonalPlaceBundle({
    date: state.date,
    latitude: activeLocation?.latitude,
    longitude: activeLocation?.longitude,
    timezone: activeLocation?.timezone || state.timezone,
  });

  useEffect(() => {
    const value = query.trim();
    if (value.length < 2) {
      return undefined;
    }

    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      setPlacesState((current) => ({ ...current, loading: true, error: '' }));
      try {
        const payload = await placesAPI.search({ query: value, limit: 8 });
        if (!cancelled) {
          setPlacesState({ loading: false, error: '', items: payload.items || [] });
        }
      } catch (error) {
        if (!cancelled) {
          setPlacesState({ loading: false, error: describeSupportError(error, 'Place search failed.'), items: [] });
        }
      }
    }, 250);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [query]);

  const choosePlace = (place) => {
    setSelected(place);
    setLocation({ latitude: place.latitude, longitude: place.longitude, label: place.label });
    setTimezone(place.timezone);
  };

  return (
    <AppChrome>
      <main className="page-shell place-page">
        <section className="place-workspace">
          <aside className="panel place-sidebar">
            <div className="panel-heading tight">
              <h2>Place search</h2>
              <button type="button" className="inline-button" onClick={() => setQuery('')}>Clear</button>
            </div>
            <div className="place-buttons" aria-label="Place search results">
              {placesState.items.length ? placesState.items.map((place) => (
                <button
                  key={`${place.label}-${place.latitude}-${place.longitude}`}
                  type="button"
                  className={activeLocation?.label === place.label ? 'is-selected' : ''}
                  onClick={() => choosePlace(place)}
                >
                  <span>⌖</span>
                  {place.label}
                </button>
              )) : (
                <p className="festival-muted-note">
                  {queryReady ? 'No selectable result yet. Try a district, city, or country name.' : 'Search for a town, city, or village to personalize calculations.'}
                </p>
              )}
            </div>
            <div className="region-stack">
              <p className="eyebrow">Provider</p>
              <span>{placesState.loading ? 'Searching...' : humanMethodLabel(placesState.items[0]?.source || activeLocation.source, 'Local place index')}</span>
              {placesState.error ? <span>{placesState.error}</span> : null}
              <small>Remote search can be skipped; the selected place stays in this browser context.</small>
            </div>
          </aside>
          <section className="panel map-panel">
            <div className="workspace-title">
              <h1>Find your place</h1>
              <p>Choose the calculation place for sunrise, panchanga, festivals, and timing windows.</p>
            </div>
            <label className="search-field">
              <span aria-hidden="true">⌕</span>
              <input
                value={query}
                placeholder="Search Kathmandu, Pokhara, Lalitpur, Biratnagar, or Janakpur"
                onChange={(event) => {
                  const value = event.target.value;
                  setQuery(value);
                  if (value.trim().length < 2) {
                    setPlacesState({ loading: false, error: '', items: [] });
                  }
                }}
                aria-label="Search places"
              />
              <button type="button" onClick={() => setQuery('')} aria-label="Clear place search">×</button>
            </label>
            <p className="place-search-helper">Search a city, town, or village in Nepal. Results only set the browser calculation context.</p>
            <div className="place-suggestions">
              {placesState.loading ? <p className="festival-muted-note">Searching places...</p> : null}
              {!placesState.loading && !queryReady ? <p className="festival-muted-note">Type at least two characters to search places.</p> : null}
              {!placesState.loading && queryReady && !placesState.items.length ? <p className="festival-muted-note">No matching place found. Try Kathmandu, Lalitpur, Pokhara, Nepal, or a nearby district.</p> : null}
              {placesState.items.map((place) => (
                <button key={`${place.label}-${place.latitude}-${place.longitude}`} type="button" onClick={() => choosePlace(place)}>
                  <span>⌖</span>
                  <strong>{place.label}</strong>
                  <small>{humanMethodLabel(place.source, 'Place match')}</small>
                  <em>{formatCoordinates(place)}</em>
                </button>
              ))}
            </div>
            <section className="place-context-card" aria-label={`${activePlaceName} calculation context`}>
              <div>
                <p className="eyebrow">Selected place</p>
                <h2>{activePlaceName}</h2>
                <p className="place-context-meta">{coordinateStatus} - {activeLocation.timezone || state.timezone}</p>
                <p>{coordinateStatus} · {activeLocation.timezone || state.timezone}</p>
              </div>
              <dl>
                <div><dt>Used for</dt><dd>Sunrise, tithi, nakshatra, muhurta</dd></div>
                <div><dt>Precision shown</dt><dd>{coordinateStatus === 'Coordinates pending' ? 'Place name only' : '4 decimal coordinates'}</dd></div>
                <div><dt>Storage</dt><dd>Browser session context</dd></div>
              </dl>
              <div className="place-privacy-row">
                <span>Private by default</span>
                <strong>No account or location tracking required.</strong>
              </div>
            </section>
            <div className="place-result-strip">
              {placesState.items.map((place) => (
                <button key={`${place.label}-${place.source}`} type="button" onClick={() => choosePlace(place)}>
                  {place.label}
                  <small>{formatCoordinates(place)}</small>
                </button>
              ))}
            </div>
            <div className="notice-row">Place search is used only to set calculation context for this browser session. Coordinates are shown for auditability, not as the primary identity of the place.</div>
          </section>
          <aside className="panel place-detail">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Selected place</p>
                <h2>{activePlaceName}</h2>
                <p>{activeLocation.timezone || state.timezone}</p>
              </div>
            </div>
            <dl>
              <div><dt>Sunrise</dt><dd>{formatTimeReference(placeBundle.payload?.local_sunrise || placeBundle.payload?.sunrise)}</dd></div>
              <div><dt>Sunset</dt><dd>{formatTimeReference(placeBundle.payload?.local_sunset)}</dd></div>
              <div><dt>Coordinates</dt><dd>{formatCoordinates(activeLocation)}</dd></div>
              <div><dt>Context</dt><dd>{humanMethodLabel(placeBundle.contextPayload?.status_line || placeBundle.meta?.method, 'Ready for calculation')}</dd></div>
            </dl>
            {placeBundle.error ? <p className="birth-error" role="alert">{placeBundle.error}</p> : null}
            <Confidence value={placeBundle.meta?.confidence?.score || 86} />
          </aside>
        </section>
      </main>
    </AppChrome>
  );
}

