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
  CalendarDays,
  ChevronRight,
  Clock3,
  Compass,
  LocateFixed,
  MapPin,
  Search,
  ShieldCheck,
  Sparkles,
  Sun,
  X,
} from 'lucide-react';
import { useParvaToast } from '../motion/ParvaToastContext';
import {
  countdownText,
  resolveFestivalVisual,
} from './festival/FestivalUtils.jsx';

const quickPlaces = [
  { label: 'Kathmandu, Nepal', latitude: 27.7172, longitude: 85.3240, timezone: 'Asia/Kathmandu', source: 'quick_place' },
  { label: 'Pokhara, Nepal', latitude: 28.2096, longitude: 83.9856, timezone: 'Asia/Kathmandu', source: 'quick_place' },
  { label: 'Janakpur, Nepal', latitude: 26.7288, longitude: 85.9250, timezone: 'Asia/Kathmandu', source: 'quick_place' },
  { label: 'Biratnagar, Nepal', latitude: 26.4525, longitude: 87.2718, timezone: 'Asia/Kathmandu', source: 'quick_place' },
  { label: 'Nepalgunj, Nepal', latitude: 28.0500, longitude: 81.6167, timezone: 'Asia/Kathmandu', source: 'quick_place' },
  { label: 'Dhangadhi, Nepal', latitude: 28.7017, longitude: 80.5898, timezone: 'Asia/Kathmandu', source: 'quick_place' },
];

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
  const displayTimelineItems = [
    compass?.horizon?.sunrise ? { time: formatTimeReference(compass.horizon.sunrise), title: 'Sunrise', type: 'warm', icon: <Sun /> } : null,
    ...(liveWindows.slice(0, 3).map((window) => ({ time: window.time, title: window.name, type: window.type, icon: <Sparkles /> }))),
    compass?.horizon?.sunset ? { time: formatTimeReference(compass.horizon.sunset), title: 'Sunset', type: 'warm', icon: <Clock3 /> } : null,
  ].filter(Boolean);
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
                <Link className="text-link compact-link" to="/panchanga">View full panchanga <ChevronRight aria-hidden="true" /></Link>
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
                    <span><CalendarDays aria-hidden="true" /></span>
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
                    <span><Sparkles aria-hidden="true" /></span>
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
  const { notify } = useParvaToast();
  const { state, setLocation, setTimezone } = useTemporalContext();
  const [query, setQuery] = useState('');
  const [placesState, setPlacesState] = useState({ loading: false, error: '', items: [] });
  const [selected, setSelected] = useState(null);
  const [locating, setLocating] = useState(false);
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
    notify('Calculation place updated', { detail: place.label });
  };

  const useCurrentLocation = () => {
    if (!navigator.geolocation) {
      setPlacesState((current) => ({ ...current, error: 'This browser does not provide location access.' }));
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      ({ coords }) => {
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || state.timezone;
        choosePlace({
          label: 'Current location',
          latitude: Number(coords.latitude.toFixed(5)),
          longitude: Number(coords.longitude.toFixed(5)),
          timezone,
          source: 'browser_geolocation',
        });
        setLocating(false);
      },
      () => {
        setLocating(false);
        setPlacesState((current) => ({
          ...current,
          error: 'Location access was unavailable. Search or choose a place below.',
        }));
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 },
    );
  };

  return (
    <AppChrome>
      <main className="page-shell place-page">
        <section className="place-workspace">
          <section className="panel place-search-panel">
            <div className="workspace-title">
              <p className="eyebrow">My place</p>
              <h1>Find your place</h1>
              <p>Choose the calculation place for sunrise, panchanga, festivals, and timing windows.</p>
            </div>
            <label className="search-field">
              <span aria-hidden="true"><Search /></span>
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
              <button type="button" onClick={() => setQuery('')} aria-label="Clear place search" disabled={!query}><X aria-hidden="true" /></button>
            </label>
            <p className="place-search-helper">Search a city, town, or village in Nepal. Results only set the browser calculation context.</p>
            <div className={`place-suggestions${!queryReady ? ' is-discovery' : ''}`}>
              {placesState.loading ? <p className="festival-muted-note">Searching places...</p> : null}
              {!placesState.loading && !queryReady ? (
                <section className="place-discovery" aria-label="Quick places">
                  <header>
                    <div><span>Quick places</span><small>Choose a familiar calculation context.</small></div>
                    <button type="button" onClick={useCurrentLocation} disabled={locating}>
                      <LocateFixed aria-hidden="true" />
                      {locating ? 'Locating' : 'Use my location'}
                    </button>
                  </header>
                  <div>
                    {quickPlaces.map((place) => (
                      <button
                        key={place.label}
                        type="button"
                        className={activePlaceName === place.label ? 'is-selected' : ''}
                        onClick={() => choosePlace(place)}
                      >
                        <MapPin aria-hidden="true" />
                        <span>{place.label.replace(', Nepal', '')}</span>
                        <small>{place.latitude.toFixed(2)}, {place.longitude.toFixed(2)}</small>
                      </button>
                    ))}
                  </div>
                </section>
              ) : null}
              {!placesState.loading && queryReady && !placesState.items.length ? <p className="festival-muted-note">No matching place found. Try Kathmandu, Lalitpur, Pokhara, Nepal, or a nearby district.</p> : null}
              {placesState.items.map((place) => (
                <button
                  key={`${place.label}-${place.latitude}-${place.longitude}`}
                  type="button"
                  className={activeLocation?.label === place.label ? 'is-selected' : ''}
                  onClick={() => choosePlace(place)}
                >
                  <MapPin aria-hidden="true" />
                  <strong>{place.label}</strong>
                  <small>{humanMethodLabel(place.source, 'Place match')}</small>
                  <em>{formatCoordinates(place)}</em>
                </button>
              ))}
            </div>
            <div className="place-provider-line">
              <Compass aria-hidden="true" />
              <span>
                <strong>{placesState.loading ? 'Searching place index' : humanMethodLabel(placesState.items[0]?.source || activeLocation.source, 'Local place index')}</strong>
                <small>{placesState.error || 'Results update the calculation context in this browser.'}</small>
              </span>
            </div>
          </section>
          <aside className="panel place-detail">
            <div className="place-context-heading">
              <span className="place-pin-mark"><MapPin aria-hidden="true" /></span>
              <div>
                <p className="eyebrow">Selected place</p>
                <h2>{activePlaceName}</h2>
                <p>{coordinateStatus} / {activeLocation.timezone || state.timezone}</p>
              </div>
            </div>
            <dl className="place-fact-grid">
              <div><Sun aria-hidden="true" /><dt>Sunrise</dt><dd>{formatTimeReference(placeBundle.payload?.local_sunrise || placeBundle.payload?.sunrise)}</dd></div>
              <div><Clock3 aria-hidden="true" /><dt>Sunset</dt><dd>{formatTimeReference(placeBundle.payload?.local_sunset)}</dd></div>
              <div><Compass aria-hidden="true" /><dt>Coordinates</dt><dd>{formatCoordinates(activeLocation)}</dd></div>
              <div><ShieldCheck aria-hidden="true" /><dt>Context</dt><dd>{humanMethodLabel(placeBundle.contextPayload?.status_line || placeBundle.meta?.method, 'Ready for calculation')}</dd></div>
            </dl>
            {placeBundle.error ? <p className="birth-error" role="alert">{placeBundle.error}</p> : null}
            <div className="place-confidence-row">
              <Confidence value={placeBundle.meta?.confidence?.score || 86} />
            </div>
            <div className="place-context-actions">
              <Link to="/today">Open today</Link>
              <Link to="/best-time">Find a time</Link>
              <Link to="/panchanga">View panchanga</Link>
            </div>
            <div className="place-privacy-row">
              <ShieldCheck aria-hidden="true" />
              <span><strong>Stored in this browser</strong><small>No account or live location tracking.</small></span>
            </div>
          </aside>
        </section>
      </main>
    </AppChrome>
  );
}

