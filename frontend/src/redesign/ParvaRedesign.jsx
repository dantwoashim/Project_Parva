import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, NavLink, useParams } from 'react-router-dom';
import {
  calendarAPI,
  feedAPI,
  festivalAPI,
  kundaliAPI,
  muhurtaAPI,
  placesAPI,
  policyAPI,
  reliabilityAPI,
  temporalAPI,
} from '../services/api';
import { todayIso } from '../context/temporalContextState';
import { useTemporalContext } from '../context/useTemporalContext';
import { useFestivalDetail } from '../hooks/useFestivals';
import usePersonalPlaceBundle from '../hooks/usePersonalPlaceBundle';
import useTodayBundle from '../hooks/useTodayBundle';
import { describeSupportError } from '../services/errorFormatting';
import './ParvaRedesign.css';

const navItems = [
  { label: 'Today', to: '/today' },
  { label: 'My Place', to: '/my-place' },
  { label: 'Festivals', to: '/festivals' },
  { label: 'Best Time', to: '/best-time' },
  { label: 'Birth Reading', to: '/birth-reading' },
  { label: 'Time Lab', to: '/panchanga' },
];

const footerGroups = [
  {
    title: 'Explore',
    links: [
      { label: 'Today', to: '/today' },
      { label: 'Festivals', to: '/festivals' },
      { label: 'Best Time', to: '/best-time' },
      { label: 'Birth Reading', to: '/birth-reading' },
    ],
  },
  {
    title: 'Tools',
    links: [
      { label: 'My Place', to: '/my-place' },
      { label: 'Time Lab', to: '/panchanga' },
      { label: 'Saved', to: '/profile' },
      { label: 'Integrations', to: '/integrations' },
    ],
  },
  {
    title: 'Trust',
    links: [
      { label: 'Trust', to: '/trust' },
      { label: 'Methodology', to: '/methodology' },
      { label: 'Truth Lab', to: '/truth-lab' },
      { label: 'About', to: '/about' },
      { label: 'API Policy', to: '/policy' },
    ],
  },
];

const sourceDots = [1, 2, 3, 4, 5, 6];

const festivalMonths = ['All', 'Baishakh', 'Jyestha', 'Ashar', 'Shrawan', 'Bhadra', 'Ashwin', 'Kartik', 'Mangsir', 'Poush', 'Magh', 'Falgun', 'Chaitra'];

const fallbackFestivalCategories = [
  { value: 'national', label: 'National' },
  { value: 'religious', label: 'Religious' },
  { value: 'buddhist', label: 'Buddhist' },
  { value: 'regional', label: 'Regional' },
  { value: 'fast', label: 'Fast / Vrata' },
];

const festivalSortOptions = [
  { value: 'chronological', label: 'Calendar order' },
  { value: 'recommended', label: 'Recommended' },
  { value: 'popular', label: 'Major first' },
  { value: 'upcoming', label: 'Upcoming' },
];

const fallbackFestivalRegions = [
  { value: 'nepal', label: 'Nepal-wide' },
  { value: 'Kathmandu Valley', label: 'Kathmandu Valley' },
  { value: 'Madhesh', label: 'Madhesh / Terai' },
  { value: 'Lumbini', label: 'Lumbini' },
];

const festivalQualityOptions = [
  { value: 'all', label: 'All source states' },
  { value: 'computed', label: 'Computed dates' },
  { value: 'provisional', label: 'Provisional dates' },
  { value: 'inventory', label: 'Inventory only' },
];

const defaultFestivalFilters = {
  month: 'All',
  category: 'All',
  region: 'All',
  qualityBand: 'all',
  sort: 'chronological',
};

const festivalVisualMeta = {
  dashain: { tone: 'orange', art: 'durga', icon: '✣' },
  tihar: { tone: 'gold', art: 'diya', icon: '◒' },
  'buddha-jayanti': { tone: 'green', art: 'buddha', icon: '◇' },
  chhath: { tone: 'orange', art: 'sun', icon: '✺' },
  holi: { tone: 'red', art: 'holi', icon: '☆' },
  'ekadashi-apara': { tone: 'green', art: 'leaf', icon: '✤' },
};

const categoryVisualMeta = {
  national: { tone: 'orange', art: 'durga', icon: '✣' },
  buddhist: { tone: 'green', art: 'buddha', icon: '◇' },
  religious: { tone: 'gold', art: 'diya', icon: '◒' },
  fast: { tone: 'green', art: 'leaf', icon: '✤' },
  regional: { tone: 'red', art: 'holi', icon: '✦' },
};


const grahaShort = {
  sun: 'Su',
  moon: 'Mo',
  mars: 'Ma',
  mercury: 'Me',
  jupiter: 'Ju',
  venus: 'Ve',
  saturn: 'Sa',
  rahu: 'Ra',
  ketu: 'Ke',
};

const signShort = {
  Aries: 'Ari',
  Taurus: 'Tau',
  Gemini: 'Gem',
  Cancer: 'Can',
  Leo: 'Leo',
  Virgo: 'Vir',
  Libra: 'Lib',
  Scorpio: 'Sco',
  Sagittarius: 'Sag',
  Capricorn: 'Cap',
  Aquarius: 'Aqu',
  Pisces: 'Pis',
};

const housePositions = {
  1: { x: 50, y: 22 },
  2: { x: 66, y: 30 },
  3: { x: 77, y: 42 },
  4: { x: 66, y: 52 },
  5: { x: 77, y: 64 },
  6: { x: 66, y: 75 },
  7: { x: 50, y: 78 },
  8: { x: 34, y: 75 },
  9: { x: 23, y: 64 },
  10: { x: 34, y: 52 },
  11: { x: 23, y: 42 },
  12: { x: 34, y: 30 },
};

const readingTraits = {
  Aries: 'direct, decisive, and action-led',
  Taurus: 'steady, tactile, and materially grounded',
  Gemini: 'curious, verbal, and adaptive',
  Cancer: 'protective, memory-rich, and emotionally tuned',
  Leo: 'visible, expressive, and self-directed',
  Virgo: 'precise, service-minded, and pattern-sensitive',
  Libra: 'relational, aesthetic, and balance-seeking',
  Scorpio: 'private, intense, and transformation-oriented',
  Sagittarius: 'searching, principled, and horizon-facing',
  Capricorn: 'structured, patient, and responsibility-led',
  Aquarius: 'independent, systems-minded, and future-facing',
  Pisces: 'intuitive, porous, and symbol-sensitive',
};

function titleCase(value) {
  return String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function formatDateTime(value) {
  if (!value) return 'Unknown';
  try {
    return new Intl.DateTimeFormat('en', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(new Date(value));
  } catch {
    return String(value).slice(0, 10);
  }
}

function formatIsoDate(value, options = {}) {
  if (!value) return 'Date pending';
  try {
    return new Intl.DateTimeFormat('en', {
      weekday: options.weekday,
      month: options.month || 'short',
      day: 'numeric',
      year: options.year || 'numeric',
      timeZone: options.timeZone,
    }).format(new Date(`${String(value).slice(0, 10)}T00:00:00`));
  } catch {
    return String(value);
  }
}

function formatTimeReference(value) {
  if (!value) return 'Pending';
  const candidate = typeof value === 'object' ? value.local_time || value.local || value.utc : value;
  if (!candidate) return 'Pending';
  if (/^\d{2}:\d{2}/.test(candidate)) return candidate.slice(0, 5);
  try {
    return new Intl.DateTimeFormat('en', {
      hour: '2-digit',
      minute: '2-digit',
    }).format(new Date(candidate));
  } catch {
    return String(candidate);
  }
}

function formatTimeRange(start, end) {
  return `${formatTimeReference(start)} - ${formatTimeReference(end)}`;
}

function formatBsDate(bs = {}) {
  if (bs.formatted) return bs.formatted;
  if (bs.year && bs.month_name && bs.day) return `${bs.year} ${bs.month_name} ${bs.day}`;
  if (bs.year && bs.month && bs.day) return `${bs.year}-${String(bs.month).padStart(2, '0')}-${String(bs.day).padStart(2, '0')} BS`;
  return 'BS date pending';
}

function formatCoordinates(location = {}) {
  const lat = Number(location.latitude);
  const lon = Number(location.longitude);
  if (!Number.isFinite(lat) || !Number.isFinite(lon)) return 'Coordinates pending';
  return `${lat.toFixed(4)}°, ${lon.toFixed(4)}°`;
}

function placeLabelFromLocation(location = {}) {
  return location.label || location.place_title || location.name || `${formatCoordinates(location)}`;
}

function scoreTone(scoreOrClass) {
  const normalized = String(scoreOrClass || '').toLowerCase();
  if (normalized.includes('avoid') || normalized.includes('inauspicious')) return 'bad';
  if (normalized.includes('neutral') || normalized.includes('mixed')) return 'warm';
  const score = Number(scoreOrClass);
  if (Number.isFinite(score)) {
    if (score < 25) return 'bad';
    if (score < 55) return 'warm';
  }
  return 'good';
}

function normalizeMuhurtaWindow(block = {}, index = 0) {
  const score = Number(block.score ?? block.top_score ?? 0);
  return {
    id: String(block.id ?? block.index ?? block.name ?? index),
    name: block.name || block.best_window?.name || 'Time window',
    time: block.start && block.end ? formatTimeRange(block.start, block.end) : 'Window pending',
    start: block.start,
    end: block.end,
    score: Number.isFinite(score) ? Math.max(0, Math.min(100, Math.round(score))) : 0,
    kind: readableCategory(block.class || block.quality || block.tone || 'timing'),
    type: scoreTone(block.class || score),
    left: Math.max(0, Math.min(90, index * 8)),
    width: 8,
    reasonCodes: block.reason_codes || [],
  };
}

function buildPanchangaItems(compass = {}, panchangaPayload = null) {
  const compassData = compass || {};
  const signals = compassData.signals || {};
  const panchanga = panchangaPayload?.panchanga || {};
  const primary = compassData.primary_readout || panchanga.tithi || {};
  return [
    { icon: '☾', label: 'Tithi', value: primary.tithi_name || primary.name || 'Pending', meta: primary.paksha ? readableCategory(primary.paksha) : 'From API' },
    { icon: '◐', label: 'Paksha', value: readableCategory(primary.paksha || panchanga.tithi?.paksha || 'Pending'), meta: primary.tithi_number || panchanga.tithi?.number ? `Tithi ${primary.tithi_number || panchanga.tithi.number}` : 'From API' },
    { icon: '✦', label: 'Nakshatra', value: signals.nakshatra?.name || panchanga.nakshatra?.name || 'Pending', meta: signals.nakshatra?.pada ? `Pada ${signals.nakshatra.pada}` : 'From API' },
    { icon: '✣', label: 'Yoga', value: signals.yoga?.name || panchanga.yoga?.name || 'Pending', meta: 'From API' },
    { icon: '❋', label: 'Karana', value: signals.karana?.name || panchanga.karana?.name || 'Pending', meta: 'From API' },
  ];
}

function buildDayFacts(compass = {}) {
  const horizon = (compass || {}).horizon || {};
  return [
    ['Sunrise', formatTimeReference(horizon.sunrise)],
    ['Sunset', formatTimeReference(horizon.sunset)],
    ['Rahu Kalam', horizon.rahu_kalam ? formatTimeRange(horizon.rahu_kalam.start, horizon.rahu_kalam.end) : 'Pending'],
    ['Current window', horizon.current_muhurta?.name || 'Pending'],
  ];
}

function currentDasha(timeline = [], reference = new Date()) {
  const now = reference.getTime();
  return timeline.find((period) => {
    const start = new Date(period.start).getTime();
    const end = new Date(period.end).getTime();
    return Number.isFinite(start) && Number.isFinite(end) && start <= now && now <= end;
  }) || timeline[0] || null;
}

function strongestGraha(payload) {
  return Object.values(payload?.grahas || {}).find((graha) => graha?.dignity?.state && graha.dignity.state !== 'neutral')
    || Object.values(payload?.grahas || {})[0]
    || null;
}

function d9Houses(payload) {
  const d9 = payload?.d9 || {};
  const grouped = Array.from({ length: 12 }, (_, index) => ({
    house_number: index + 1,
    rashi_english: Object.values(signShort)[index] || `Sign ${index + 1}`,
    occupants: [],
  }));

  Object.entries(d9).forEach(([id, graha]) => {
    const signNo = Number(graha?.navamsa_rashi_number || 1);
    const bucket = grouped[Math.max(0, Math.min(11, signNo - 1))];
    bucket.rashi_english = graha?.navamsa_rashi_english || bucket.rashi_english;
    bucket.occupants.push(id);
  });

  return grouped;
}

function AppChrome({ children }) {
  const [searchOpen, setSearchOpen] = useState(false);
  const { state } = useTemporalContext();
  const [summary, setSummary] = useState(null);
  const placeLabel = summary?.location_context?.place_title
    || summary?.place_title
    || placeLabelFromLocation(state.location);
  const bsLabel = summary?.bikram_sambat ? formatBsDate(summary.bikram_sambat) : state.date;

  useEffect(() => {
    let cancelled = false;

    temporalAPI.getCompassEnvelope({
      date: state.date,
      lat: state.location?.latitude,
      lon: state.location?.longitude,
      tz: state.timezone,
      qualityBand: 'computed',
    }).then((envelope) => {
      if (!cancelled) setSummary(envelope.data || null);
    }).catch(() => {
      if (!cancelled) setSummary(null);
    });

    return () => {
      cancelled = true;
    };
  }, [state.date, state.location?.latitude, state.location?.longitude, state.timezone]);

  return (
    <div className="parva-app">
      <header className="parva-topbar">
        <Link className="brand-mark" to="/today" aria-label="Parva home">
          <span className="brand-symbol" aria-hidden="true"><span /></span>
          <span>Parva</span>
        </Link>
        <nav className="top-nav" aria-label="Primary navigation">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to}>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="top-actions">
          <button type="button" className="search-trigger" onClick={() => setSearchOpen(true)}>
            <span aria-hidden="true">⌕</span>
            <span>Search Parva</span>
            <kbd>⌘ K</kbd>
          </button>
          <Link className="place-pill" to="/my-place" aria-label={`Current place ${placeLabel}`}>
            <span aria-hidden="true">⌖</span>
            <strong>{placeLabel}</strong>
            <small>{state.timezone}</small>
          </Link>
          <Link className="icon-button" to="/trust" aria-label="Open trust center">⌁</Link>
          <Link className="profile-chip" to="/profile" aria-label="Open profile">
            <span aria-hidden="true">◎</span>
            <strong>Profile</strong>
            <small>Local only</small>
          </Link>
        </div>
      </header>
      <div className="mobile-context-bar" aria-label="Current day and place">
        <Link className="mobile-date-card" to="/today">
          <small>Today</small>
          <strong>{bsLabel}</strong>
        </Link>
        <Link className="mobile-place-card" to="/my-place">
          <span aria-hidden="true">⌖</span>
          <strong>{placeLabel}</strong>
        </Link>
        <button type="button" className="mobile-search-button" onClick={() => setSearchOpen(true)} aria-label="Search Parva">
          ⌕
        </button>
      </div>
      {children}
      <footer className="parva-footer">
        <section className="footer-main" aria-label="Parva footer">
          <div className="footer-brand">
            <Link className="brand-mark footer-logo" to="/today" aria-label="Parva home">
              <span className="brand-symbol" aria-hidden="true"><span /></span>
              <span>Parva</span>
            </Link>
            <p>
              A public reference beta for Nepal-focused time, festival, panchanga, muhurta,
              and kundali surfaces. Built for clarity, provenance, and careful self-hosting.
            </p>
            <div className="footer-status" aria-label="Service status">
              <span><i aria-hidden="true" /> v3 API canonical</span>
              <span>AGPL-3.0-or-later</span>
            </div>
          </div>
          <div className="footer-link-grid">
            {footerGroups.map((group) => (
              <nav key={group.title} aria-label={`${group.title} links`}>
                <h2>{group.title}</h2>
                {group.links.map((link) => (
                  link.href
                    ? <a key={link.label} href={link.href}>{link.label}</a>
                    : <Link key={link.label} to={link.to}>{link.label}</Link>
                ))}
              </nav>
            ))}
          </div>
        </section>
        <section className="footer-bottom" aria-label="Legal and service notes">
          <span>Public reference beta. Informational use only; verify ritual decisions with local authorities or a trusted panchang.</span>
          <span>© 2026 Parva. Source-aware temporal tools for Nepal.</span>
        </section>
      </footer>
      <nav className="bottom-nav" aria-label="Mobile navigation">
        {navItems.slice(0, 5).map((item) => (
          <NavLink key={item.to} to={item.to}>
            {item.label}
          </NavLink>
        ))}
      </nav>
      {searchOpen ? <SearchDialog onClose={() => setSearchOpen(false)} /> : null}
    </div>
  );
}

function SearchDialog({ onClose }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const fromDate = useMemo(() => todayIso('Asia/Kathmandu'), []);
  const toDate = useMemo(() => addDaysIso(fromDate, 365), [fromDate]);

  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  useEffect(() => {
    const value = query.trim();
    if (value.length < 2) {
      setResults([]);
      setLoading(false);
      return undefined;
    }

    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      setLoading(true);
      try {
        const [timeline, places] = await Promise.allSettled([
          festivalAPI.getTimelineEnvelope({ from: fromDate, to: toDate, search: value, qualityBand: 'all', lang: 'en' }),
          placesAPI.search({ query: value, limit: 4 }),
        ]);
        if (cancelled) return;
        const festivalRows = timeline.status === 'fulfilled'
          ? normalizeFestivalTimelineRows(timeline.value.data?.groups || []).slice(0, 6).map((item) => ({
            label: item.displayName,
            meta: `Festival · ${item.adLabel}`,
            to: `/festivals/${item.id}`,
          }))
          : [];
        const placeRows = places.status === 'fulfilled'
          ? (places.value.items || []).slice(0, 4).map((item) => ({
            label: item.label,
            meta: `Place · ${formatCoordinates(item)}`,
            to: `/my-place?q=${encodeURIComponent(item.label)}`,
          }))
          : [];
        const supportRows = [
          { label: 'Trust', meta: 'Reliability and policy center', to: '/trust' },
          { label: 'Methodology', meta: 'How Parva computes and explains results', to: '/methodology' },
          { label: 'Truth Lab', meta: 'Live reliability and source evidence', to: '/truth-lab' },
          { label: 'About', meta: 'Product stance and scope', to: '/about' },
          { label: 'API Policy', meta: 'Backend advisory policy', to: '/policy' },
        ].filter((item) => `${item.label} ${item.meta}`.toLowerCase().includes(value.toLowerCase()));
        setResults([...supportRows, ...festivalRows, ...placeRows]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 250);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [fromDate, query, toDate]);

  return (
    <div className="modal-layer" role="dialog" aria-modal="true" aria-label="Search Parva">
      <button type="button" className="modal-scrim" onClick={onClose} aria-label="Close search" />
      <section className="search-dialog">
        <div className="search-input-row">
          <span aria-hidden="true">⌕</span>
          <input
            autoFocus
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search festivals, places, timings..."
          />
          <button type="button" onClick={onClose}>Close</button>
        </div>
        <div className="search-results">
          {loading ? <p className="festival-muted-note">Searching the API...</p> : null}
          {!loading && query.trim().length < 2 ? <p className="festival-muted-note">Type at least two characters to search live festival and place data.</p> : null}
          {!loading && query.trim().length >= 2 && !results.length ? <p className="festival-muted-note">No API results found.</p> : null}
          {results.map((result) => (
            <Link key={result.to} to={result.to} onClick={onClose}>
              <span>{result.label}</span>
              <small>{result.meta}</small>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

function PageHero({ eyebrow, title, body, action }) {
  return (
    <section className="page-hero">
      <div>
        {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
        <h1>{title}</h1>
        {body ? <p>{body}</p> : null}
      </div>
      {action ? <div className="hero-action">{action}</div> : null}
    </section>
  );
}

function Confidence({ value, label = 'Source confidence' }) {
  const score = Number(value);
  const normalizedValue = Number.isFinite(score) ? Math.max(0, Math.min(100, Math.round(score))) : 0;
  return (
    <div className="confidence-meter">
      <span>{label}</span>
      <div><i style={{ width: `${normalizedValue}%` }} /></div>
      <strong>{normalizedValue}%</strong>
    </div>
  );
}

function SourceDots({ active = 5 }) {
  return (
    <span className="source-dots" aria-label={`${active} of 6 source checks passed`}>
      {sourceDots.map((dot) => <i key={dot} className={dot <= active ? 'is-active' : ''} />)}
    </span>
  );
}

function ScoreRing({ value, label = 'Score' }) {
  return (
    <div className="score-ring" style={{ '--score': `${value}%` }}>
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function InfoCell({ icon, label, value, meta }) {
  return (
    <article className="info-cell">
      {icon ? <span className="cell-icon" aria-hidden="true">{icon}</span> : null}
      <small>{label}</small>
      <strong>{value}</strong>
      {meta ? <em>{meta}</em> : null}
    </article>
  );
}

function TimelineList({ compact = false, items = [] }) {
  return (
    <div className={compact ? 'timeline-list compact' : 'timeline-list'}>
      {items.length ? items.map((item) => (
        <Link key={`${item.time}-${item.title}`} className={`timeline-item tone-${item.type}`} to="/best-time">
          <span>{item.time}</span>
          <strong>{item.title}</strong>
          <i aria-hidden="true">{item.icon}</i>
        </Link>
      )) : <p className="festival-muted-note">Timeline data is loading from the API.</p>}
    </div>
  );
}

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
  const placeLabel = compass?.location_context?.place_title || placeLabelFromLocation(state.location);
  const qualityScore = Math.max(0, Math.min(100, Math.round(Number(muhurta?.best_window?.score ?? 0))));
  const sourceLabel = compassMeta?.method || compass?.engine?.method || 'API';
  const festivalCards = (onDateFestivals.length ? onDateFestivals : upcomingFestivals).slice(0, 3);

  return (
    <AppChrome>
      <main className="page-shell today-page">
        <PageHero
          eyebrow="Today"
          title={`${weekday}, ${bsLabel}`}
          body={`${formatIsoDate(state.date)}  •  ${state.timezone}`}
          action={(
            <Link className="location-mini" to="/my-place">
              <span>⌖ {placeLabel}</span>
              <small>{formatCoordinates(state.location)}</small>
            </Link>
          )}
        />
        {error ? (
          <section className="festival-empty-state panel" role="alert">
            <p className="eyebrow">Today unavailable</p>
            <h2>{error}</h2>
          </section>
        ) : null}
        <section className="today-main">
          <div className="today-stack">
            <section className="panel panchanga-panel">
              <div className="panel-heading">
              <div>
                  <p className="eyebrow">Panchanga ⓘ ({placeLabel})</p>
                </div>
                <Link className="text-link compact-link" to="/panchanga">View full panchanga ›</Link>
              </div>
              {loading && !compass ? <p className="festival-muted-note">Loading panchanga from the API...</p> : null}
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
                  <p className="eyebrow">Best time today ⓘ</p>
                  <h2>{muhurta?.best_window?.name || 'API window pending'}</h2>
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
              <p className="panel-note">{muhurtaMeta?.method || 'Timings are computed by the API for the selected location.'}</p>
            </section>
          </div>
          <aside className="side-rail">
            <section className="panel timeline-panel">
              <div className="panel-heading tight">
                <p className="eyebrow">Day timeline</p>
                <strong>{state.date}</strong>
              </div>
              <TimelineList compact items={timelineItems} />
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
                <div><dt>Calendar system</dt><dd>{compass?.engine?.method_profile || 'API'}</dd></div>
                <div><dt>Calculation mode</dt><dd>{compass?.engine?.ephemeris_mode || compass?.engine?.method || 'API'}</dd></div>
                <div><dt>Location</dt><dd>{placeLabel}</dd></div>
                <div><dt>Request ID</dt><dd>{compassMeta?.request_id || 'Pending'}</dd></div>
              </dl>
              <Link className="text-link" to="/truth-lab">Review evidence</Link>
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
            <div className="place-buttons">
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
              )) : <p className="festival-muted-note">Search results appear here from `/places/search`.</p>}
            </div>
            <div className="region-stack">
              <p className="eyebrow">Provider</p>
              <span>{placesState.loading ? 'Searching...' : placesState.items[0]?.source || activeLocation.source || 'API'}</span>
              {placesState.error ? <span>{placesState.error}</span> : null}
            </div>
          </aside>
          <section className="panel map-panel">
            <div className="workspace-title">
              <h1>Find your place</h1>
              <p>Search any city, town, or village to get accurate Nepal temporal data.</p>
            </div>
            <label className="search-field">
              <span aria-hidden="true">⌕</span>
              <input
                value={query}
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
            <div className="place-suggestions">
              {placesState.loading ? <p className="festival-muted-note">Searching backend gazetteer...</p> : null}
              {!placesState.loading && query.trim().length < 2 ? <p className="festival-muted-note">Type at least two characters to search the backend place index.</p> : null}
              {!placesState.loading && query.trim().length >= 2 && !placesState.items.length ? <p className="festival-muted-note">No backend place result found.</p> : null}
              {placesState.items.map((place) => (
                <button key={`${place.label}-${place.latitude}-${place.longitude}`} type="button" onClick={() => choosePlace(place)}>
                  <span>⌖</span>
                  <strong>{place.label}</strong>
                  <small>{place.source}</small>
                  <em>{formatCoordinates(place)}</em>
                </button>
              ))}
            </div>
            <div className="map-canvas" role="img" aria-label={`${placeLabelFromLocation(activeLocation)} map preview`}>
              <div className="map-label">{placeLabelFromLocation(activeLocation)}</div>
              <div className="map-ring" />
              <div className="map-pin" />
              <div className="map-road one" />
              <div className="map-road two" />
            </div>
            <div className="place-result-strip">
              {placesState.items.map((place) => (
                <button key={`${place.label}-${place.source}`} type="button" onClick={() => choosePlace(place)}>
                  {place.label}
                  <small>{formatCoordinates(place)}</small>
                </button>
              ))}
            </div>
            <div className="notice-row">◇ Place results and privacy notices are returned by the backend place search service.</div>
          </section>
          <aside className="panel place-detail">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Selected place</p>
                <h2>{placeLabelFromLocation(activeLocation)}</h2>
                <p>{activeLocation.timezone || state.timezone}</p>
              </div>
            </div>
            <dl>
              <div><dt>Sunrise</dt><dd>{formatTimeReference(placeBundle.payload?.local_sunrise || placeBundle.payload?.sunrise)}</dd></div>
              <div><dt>Sunset</dt><dd>{formatTimeReference(placeBundle.payload?.local_sunset)}</dd></div>
              <div><dt>Coordinates</dt><dd>{formatCoordinates(activeLocation)}</dd></div>
              <div><dt>Context</dt><dd>{placeBundle.contextPayload?.status_line || placeBundle.meta?.method || 'API context pending'}</dd></div>
            </dl>
            {placeBundle.error ? <p className="birth-error" role="alert">{placeBundle.error}</p> : null}
            <Confidence value={placeBundle.meta?.confidence?.score || 86} />
          </aside>
        </section>
      </main>
    </AppChrome>
  );
}

function FestivalIllustration({ art }) {
  if (art === 'diya') {
    return (
      <svg viewBox="0 0 120 120" role="img" aria-label="Diya lamp illustration">
        <path className="festival-svg-fill" d="M22 70c11 21 65 21 76 0-9 8-67 8-76 0Z" />
        <path d="M22 70c11 21 65 21 76 0M28 70c11 8 53 8 64 0" />
        <path d="M59 62c-8-13 5-25 8-36 15 19 6 32-8 36Z" />
        <path d="M43 86h34M35 94h50" />
      </svg>
    );
  }

  if (art === 'buddha') {
    return (
      <svg viewBox="0 0 120 120" role="img" aria-label="Buddha lotus illustration">
        <circle className="festival-svg-fill" cx="60" cy="46" r="18" />
        <path d="M43 46c0-12 7-23 17-23s17 11 17 23" />
        <path d="M47 54c5 8 21 8 26 0" />
        <path d="M60 64v16" />
        <path d="M28 82c14-18 28-16 32 4 4-20 18-22 32-4" />
        <path d="M20 93c18 9 62 9 80 0" />
      </svg>
    );
  }

  if (art === 'sun') {
    return (
      <svg viewBox="0 0 120 120" role="img" aria-label="Sun and river illustration">
        <circle className="festival-svg-fill" cx="60" cy="44" r="19" />
        <path d="M60 14v12M60 62v12M30 44H18M102 44H90M39 23l-8-8M81 23l8-8M39 65l-8 8M81 65l8 8" />
        <path d="M19 87c12-10 22-10 34 0s22 10 34 0 18-8 24-2" />
        <path d="M24 100c12-8 20-8 32 0s22 8 34 0" />
      </svg>
    );
  }

  if (art === 'holi') {
    return (
      <svg viewBox="0 0 120 120" role="img" aria-label="Holi color bowl illustration">
        <path className="festival-svg-fill" d="M28 72c5 20 59 20 64 0H28Z" />
        <path d="M28 72c5 20 59 20 64 0H28Z" />
        <path d="M39 61c8-12 36-12 44 0" />
        <path d="M35 31l11 11M84 29l-10 13M62 18v17M24 45l14 5M96 45l-14 5" />
        <circle cx="47" cy="50" r="4" /><circle cx="61" cy="45" r="4" /><circle cx="75" cy="51" r="4" />
      </svg>
    );
  }

  if (art === 'leaf') {
    return (
      <svg viewBox="0 0 120 120" role="img" aria-label="Fasting leaf illustration">
        <path className="festival-svg-fill" d="M33 70c16-35 46-42 64-34-2 34-25 55-58 50" />
        <path d="M33 70c16-35 46-42 64-34-2 34-25 55-58 50" />
        <path d="M33 70c19-3 38-13 56-31" />
        <path d="M38 86c-10 4-17 11-20 21" />
        <path d="M55 59l-2-15M67 51l7-15M48 72l-14-5M64 69l15 6" />
      </svg>
    );
  }

  return (
    <svg viewBox="0 0 120 120" role="img" aria-label="Durga flower illustration">
      <path className="festival-svg-fill" d="M60 20c10 15 10 28 0 40-10-12-10-25 0-40Z" />
      <path d="M60 20c10 15 10 28 0 40-10-12-10-25 0-40Z" />
      <path d="M27 48c18-6 31-2 39 12-15 5-28 1-39-12Z" />
      <path d="M93 48c-18-6-31-2-39 12 15 5 28 1 39-12Z" />
      <path d="M34 88c10-17 23-24 39-20-7 17-20 24-39 20Z" />
      <path d="M86 88c-10-17-23-24-39-20 7 17 20 24 39 20Z" />
      <circle cx="60" cy="62" r="9" />
    </svg>
  );
}

function FestivalArtwork({ festival, compact = false }) {
  const visual = resolveFestivalVisual(festival);
  const image = festivalImageSrc(festival);

  return (
    <span className={`festival-art festival-art--${visual.art} ${image ? 'has-image' : ''} ${compact ? 'is-compact' : ''}`} aria-hidden="true">
      <span className="festival-art__halo" />
      {image ? (
        <img
          src={image}
          alt=""
          loading="lazy"
          onError={(event) => {
            event.currentTarget.hidden = true;
            event.currentTarget.closest('.festival-art')?.classList.remove('has-image');
          }}
        />
      ) : null}
      <span className="festival-art__glyph"><FestivalIllustration art={visual.art} /></span>
      <span className="festival-art__line one" />
      <span className="festival-art__line two" />
    </span>
  );
}

function QualityDots({ value }) {
  const activeDots = Math.max(1, Math.round(value / 20));

  return (
    <span className="quality-dots" aria-label={`${value}% confidence`}>
      {sourceDots.slice(0, 5).map((dot) => (
        <i key={dot} className={dot <= activeDots ? 'is-active' : ''} />
      ))}
    </span>
  );
}

function resolveFestivalVisual(festival = {}) {
  const id = String(festival.id || '').toLowerCase();
  const category = String(festival.category || festival.kind || '').toLowerCase();
  return festivalVisualMeta[id] || categoryVisualMeta[category] || { tone: 'orange', art: 'durga', icon: '✣' };
}

function festivalImageSrc(festival = {}) {
  if (Array.isArray(festival.images) && festival.images[0]) return festival.images[0];
  if (festival.image) return festival.image;
  if (festival.id) return `/festival-images/${festival.id}.png`;
  return '';
}

function addDaysIso(baseIso, days) {
  const date = new Date(`${baseIso}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return date.toISOString().slice(0, 10);
}

function formatFestivalDate(value, options = {}) {
  if (!value) return 'Date pending';
  try {
    return new Intl.DateTimeFormat('en', {
      month: options.month || 'short',
      day: 'numeric',
      year: options.year || 'numeric',
    }).format(new Date(`${value}T00:00:00`));
  } catch {
    return value;
  }
}

function formatFestivalDateRange(startDate, endDate) {
  if (!startDate) return 'Date pending';
  if (!endDate || endDate === startDate) return formatFestivalDate(startDate);
  return `${formatFestivalDate(startDate, { year: undefined })} - ${formatFestivalDate(endDate)}`;
}

function formatBsDateRange(item = {}) {
  const start = item.bs_start?.formatted;
  const end = item.bs_end?.formatted;
  if (!start) return 'BS date pending';
  if (!end || end === start) return start;
  return `${start} - ${end}`;
}

function daysUntil(startDate) {
  if (!startDate) return null;
  const start = new Date(`${startDate}T00:00:00`);
  const today = new Date(`${todayIso('Asia/Kathmandu')}T00:00:00`);
  const diff = Math.ceil((start.getTime() - today.getTime()) / 86400000);
  return Number.isFinite(diff) ? diff : null;
}

function countdownText(startDate) {
  const days = daysUntil(startDate);
  if (days === null) return 'Date pending';
  if (days < 0) return 'Recently observed';
  if (days === 0) return 'Today';
  if (days === 1) return 'Tomorrow';
  return `In ${days} days`;
}

function readableCategory(value) {
  return String(value || 'observance')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function sourceStrength(item = {}) {
  const band = String(item.quality_band || '').toLowerCase();
  const status = String(item.rule_status || '').toLowerCase();
  if (band === 'computed' || status === 'active') {
    return { label: 'Computed', tone: 'high', score: 88 };
  }
  if (band === 'provisional') {
    return { label: 'Provisional', tone: 'medium', score: 68 };
  }
  if (band === 'inventory') {
    return { label: 'Inventory', tone: 'low', score: 42 };
  }
  return { label: readableCategory(band || status || 'Source'), tone: 'medium', score: 62 };
}

function normalizeFestivalTimelineRows(groups = []) {
  return groups.flatMap((group) => (group.items || []).map((item) => ({
    ...item,
    monthKey: group.month_key || item.start_date?.slice(0, 7) || '',
    monthLabel: group.month_label || item.start_date?.slice(0, 7) || 'Upcoming',
    displayName: item.display_name || item.name || 'Festival',
    bsLabel: formatBsDateRange(item),
    adLabel: formatFestivalDateRange(item.start_date, item.end_date),
    durationLabel: item.duration_days && item.duration_days > 1 ? `${item.duration_days} days` : 'Single day',
    countdownLabel: countdownText(item.start_date),
    categoryLabel: readableCategory(item.category),
    summary: item.summary || item.ritual_preview || 'Festival details are available from the public Parva calendar.',
    regions: item.regional_focus || [],
    visual: resolveFestivalVisual(item),
    source: sourceStrength(item),
  })));
}

function monthFilterValue(item = {}) {
  return item.bs_start?.month_name || item.monthLabel || 'Other';
}

function activeFestivalFilterCount(filters, search) {
  return [
    filters.month !== defaultFestivalFilters.month,
    filters.category !== defaultFestivalFilters.category,
    filters.region !== defaultFestivalFilters.region,
    filters.qualityBand !== defaultFestivalFilters.qualityBand,
    filters.sort !== defaultFestivalFilters.sort,
    Boolean(search.trim()),
  ].filter(Boolean).length;
}

function normalizeFacetOptions(options = [], fallback = []) {
  const normalized = options.map((item) => ({
    value: item.value || item.label,
    label: item.label || readableCategory(item.value),
    count: item.count,
  })).filter((item) => item.value && item.label);
  return normalized.length ? normalized : fallback;
}

function compactParagraph(value, fallback = '') {
  const text = String(value || fallback || '').replace(/\s+/g, ' ').trim();
  if (text.length <= 520) return text;
  const sentenceBreak = text.slice(0, 520).lastIndexOf('.');
  return `${text.slice(0, sentenceBreak > 260 ? sentenceBreak + 1 : 520).trim()}...`;
}

function getDetailRituals(detailData = {}, fallbackFestival = {}) {
  const sequence = detailData.festival?.ritual_sequence
    || detailData.festival?.ritual_preview
    || detailData.ritual_preview
    || fallbackFestival.ritual_sequence
    || fallbackFestival.ritual_preview;
  const days = sequence?.days;
  if (!Array.isArray(days)) return [];
  return days.flatMap((day, dayIndex) => {
    const events = Array.isArray(day.events) && day.events.length ? day.events : [day];
    return events.map((event, eventIndex) => ({
      id: `${day.name || dayIndex}-${event.title || event.name || eventIndex}`,
      day: day.name || `Step ${dayIndex + 1}`,
      title: event.title || event.name || day.name || 'Ritual step',
      body: event.description || event.detail || day.description || 'Practice details are being normalized for this observance.',
    }));
  }).slice(0, 5);
}

function buildExpandedFestivalStory(festival = {}, detailData = {}) {
  const detailFestival = detailData.festival || {};
  const mythology = detailFestival.mythology || {};
  const displayName = detailFestival.name || festival.displayName || festival.name || 'Festival';
  const description = detailFestival.description || festival.summary;
  const origin = mythology.origin_story || mythology.summary || description;
  const history = mythology.historical_context || festival.date_status_note;
  const regions = detailFestival.regional_focus || festival.regions || [];
  const deities = detailFestival.connected_deities || festival.connected_deities || [];
  const who = detailFestival.who_celebrates || 'Families and devotees who keep this observance in their community calendar.';
  const rituals = getDetailRituals(detailData, festival);
  const ritualNames = rituals.map((ritual) => ritual.title).filter(Boolean).slice(0, 4);
  const ritualBody = ritualNames.length
    ? `${displayName} is best understood through its sequence: ${ritualNames.join(', ')}. The details below preserve the order returned by the backend profile.`
    : `${displayName} is observed through household preparation, offerings, prayer, food, and community gathering, with local practice varying by lineage and region.`;

  return {
    title: detailFestival.tagline || festival.summary || displayName,
    lead: compactParagraph(description, mythology.summary || festival.summary),
    sections: [
      {
        title: 'Mythology and Meaning',
        body: compactParagraph(origin, description),
      },
      {
        title: 'Ritual Structure',
        body: compactParagraph(ritualBody),
      },
      {
        title: 'Living Practice',
        body: compactParagraph(history || `${who} ${regions.length ? `Regional focus: ${regions.join(', ')}.` : ''}`),
      },
    ],
    facts: [
      ['Who observes', who],
      ['Associated deities', deities.length ? deities.join(', ') : 'Community and household deities'],
      ['Regional focus', regions.length ? regions.join(', ') : 'Nepal-focused'],
      ['Catalog depth', readableCategory(detailFestival.content_status || festival.content_status || 'API-backed')],
    ],
    rituals,
  };
}

function buildCalendarFeedUrl(festivalId) {
  return `/v3/api/feeds/custom.ics?festivals=${encodeURIComponent(festivalId)}&years=1&download=1`;
}

function festivalOccurrenceKey(festival = {}) {
  return [
    festival.id || 'festival',
    festival.start_date || festival.bs_start?.formatted || festival.monthKey || 'catalog',
    festival.end_date || 'single',
  ].join(':');
}

export function RedesignFestivals() {
  const [search, setSearch] = useState('');
  const [filters, setFilters] = useState(defaultFestivalFilters);
  const [draftFilters, setDraftFilters] = useState(defaultFestivalFilters);
  const [filtersOpen, setFiltersOpen] = useState(false);
  const [expandedKey, setExpandedKey] = useState('');
  const [savedIds, setSavedIds] = useState(() => new Set());
  const [copiedId, setCopiedId] = useState('');
  const [timelineEnvelope, setTimelineEnvelope] = useState(null);
  const [timelineLoading, setTimelineLoading] = useState(true);
  const [timelineRefreshing, setTimelineRefreshing] = useState(false);
  const [timelineError, setTimelineError] = useState(null);
  const [detailCache, setDetailCache] = useState({});
  const hasLoadedTimelineRef = useRef(false);

  const fromDate = useMemo(() => todayIso('Asia/Kathmandu'), []);
  const toDate = useMemo(() => addDaysIso(fromDate, 420), [fromDate]);

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
          search: search.trim() || undefined,
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
  }, [filters.category, filters.qualityBand, filters.region, filters.sort, fromDate, search, toDate]);

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
  const activeFilterCount = activeFestivalFilterCount(filters, search);
  const expandedFestival = visibleFestivals.find((item) => festivalOccurrenceKey(item) === expandedKey) || null;
  const expandedDetail = expandedFestival ? detailCache[expandedFestival.id] : null;

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
    setFiltersOpen(false);
  };

  const resetFilters = () => {
    setDraftFilters(defaultFestivalFilters);
    setFilters(defaultFestivalFilters);
    setExpandedKey('');
  };

  const toggleSave = (festival) => {
    setSavedIds((current) => {
      const next = new Set(current);
      if (next.has(festival.id)) {
        next.delete(festival.id);
      } else {
        next.add(festival.id);
      }
      return next;
    });
  };

  const copyFestivalLink = async (festival) => {
    const link = `${window.location.origin}/festivals/${festival.id}`;
    try {
      if (!navigator.clipboard?.writeText) throw new Error('Clipboard API unavailable');
      await navigator.clipboard.writeText(link);
      setCopiedId(festival.id);
      window.setTimeout(() => setCopiedId(''), 1800);
    } catch {
      if (typeof window.prompt === 'function') window.prompt('Copy festival link', link);
    }
  };

  return (
    <AppChrome>
      <main className="page-shell festivals-page">
        <PageHero
          title="Festivals"
          body="A source-aware list of Nepal observances. Search, filter, and expand without leaving the calendar."
          action={(
            <div className="hero-actions festival-hero-actions">
              <label className="festival-search-control">
                <span>Search</span>
                <input
                  value={search}
                  onChange={(event) => setSearch(event.target.value)}
                  placeholder="Dashain, Ekadashi, Jatra..."
                />
              </label>
              <button type="button" className="filter-open-button" onClick={openFilters}>
                Filters {activeFilterCount ? <b>{activeFilterCount}</b> : null}
              </button>
              <label className="sort-control">
                <span>Sort by</span>
                <select
                  value={filters.sort}
                  onChange={(event) => setFilters((current) => ({ ...current, sort: event.target.value }))}
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
              {timelineRefreshing ? 'Refreshing live calendar...' : `Showing ${filters.month === 'All' ? 'all BS months' : filters.month}`}
              {filters.category !== 'All' ? ` · ${readableCategory(filters.category)}` : ''}
              {filters.qualityBand !== 'all' ? ` · ${readableCategory(filters.qualityBand)}` : ''}
            </p>
          </div>

          {timelineLoading ? (
            <section className="festival-empty-state panel">
              <p className="eyebrow">Loading live catalog</p>
              <h2>Fetching the public festival timeline.</h2>
              <p>Dates, source state, and observance windows are coming from the Parva API.</p>
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
              {visibleFestivals.map((festival) => {
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
    <div className="festival-filter-layer" role="dialog" aria-modal="true" aria-label="Festival filters">
      <button type="button" className="festival-filter-scrim" onClick={onClose} aria-label="Close festival filters" />
      <aside className="festival-filter-sheet">
        <div className="festival-filter-heading">
          <div>
            <p className="eyebrow">Refine list</p>
            <h2>Festival filters</h2>
          </div>
          <button type="button" className="close-button" onClick={onClose} aria-label="Close filters">×</button>
        </div>

        <section className="filter-block">
          <div className="filter-title">
            <span>▣</span>
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
            <span>✦</span>
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
          <small>Filters apply to the API-backed festival timeline. Month is refined locally from BS month labels.</small>
        </section>

        <div className="festival-filter-actions">
          <button type="button" onClick={onReset}>Reset</button>
          <button type="button" onClick={onClose}>Cancel</button>
          <button type="button" className="primary-button" onClick={onApply}>Apply filters</button>
        </div>
      </aside>
    </div>
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

  return (
    <article className={`festival-list-card tone-${visual.tone} ${expanded ? 'is-expanded' : ''}`}>
      <button
        type="button"
        className="festival-list-card__button"
        aria-expanded={expanded}
        aria-controls={panelId}
        onClick={onToggle}
      >
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
            {expanded ? 'Hide details' : 'View details'}
          </span>
        </span>
      </button>

      {expanded ? (
        <section id={panelId} className="festival-expanded-panel">
          {detail?.error ? (
            <div className="festival-detail-loading">
              <p className="eyebrow">Detail unavailable</p>
              <h3>{detail.error}</h3>
              <p>The list date and source state above are still available from the timeline endpoint.</p>
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
                  <p className="eyebrow">Refreshing backend detail</p>
                  <h3>Showing the timeline profile while the full source profile opens.</h3>
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
                <button type="button" onClick={onSave}>{saved ? 'Saved' : 'Save'}</button>
                <button type="button" onClick={onCopy}>{copied ? 'Copied' : 'Copy link'}</button>
                <a href={buildCalendarFeedUrl(festival.id)}>Add to calendar</a>
              </footer>
            </>
          )}
        </section>
      ) : null}
    </article>
  );
}

export function RedesignFestivalDetail() {
  const { festivalId = 'dashain' } = useParams();
  const [tab, setTab] = useState('rituals');
  const {
    festival,
    dates,
    nearbyFestivals,
    completeness,
    meta,
    loading,
    error,
  } = useFestivalDetail(festivalId, 2026);
  const displayName = festival?.name || readableCategory(festivalId);
  const detailRow = {
    id: festivalId,
    name: displayName,
    displayName,
    category: festival?.category || 'observance',
    start_date: dates?.start_date,
    end_date: dates?.end_date,
    bs_start: dates?.bs_start,
    bs_end: dates?.bs_end,
    duration_days: festival?.duration_days,
    quality_band: dates?.confidence || meta?.quality_band,
    rule_status: completeness?.overall,
    regional_focus: festival?.regions || festival?.regional_focus || [],
    images: festival?.images || [],
    summary: festival?.tagline || festival?.description || festival?.mythology?.summary || 'Festival detail is being loaded from the Parva API.',
  };
  const visual = resolveFestivalVisual(detailRow);
  const source = sourceStrength(detailRow);
  const rituals = getDetailRituals({ festival });
  const related = Array.isArray(nearbyFestivals) ? nearbyFestivals : [];
  const tags = [
    readableCategory(detailRow.category),
    ...(Array.isArray(festival?.deities) ? festival.deities : []),
    ...(Array.isArray(detailRow.regional_focus) ? detailRow.regional_focus.slice(0, 2) : []),
  ].filter(Boolean).slice(0, 5);

  return (
    <AppChrome>
      <main className="page-shell detail-page">
        <div className="breadcrumb"><Link to="/festivals">Back to festivals</Link><span>/</span><strong>{displayName}</strong></div>

        {loading && !festival ? (
          <section className="panel festival-empty-state">
            <p className="eyebrow">Loading festival</p>
            <h1>Opening {displayName}.</h1>
            <p>The full detail route is fetching its source-aware profile from the API.</p>
          </section>
        ) : error ? (
          <section className="panel festival-empty-state">
            <p className="eyebrow">Detail unavailable</p>
            <h1>{displayName}</h1>
            <p>{error}</p>
            <Link className="primary-button" to="/festivals">Return to festival list</Link>
          </section>
        ) : (
          <>
        <section className={`detail-hero festival-detail-hero tone-${visual.tone}`}>
          <aside className="panel deity-card">
            <FestivalArtwork festival={detailRow} />
            <strong>{festival?.mythology?.summary || source.label}</strong>
          </aside>
          <section className="detail-title-block">
            <p className="eyebrow">{readableCategory(detailRow.category)}</p>
            <h1>{displayName}</h1>
            <p>{detailRow.summary}</p>
            <div className="detail-date-strip">
              <span><b>{formatBsDateRange(detailRow)}</b><small>Bikram Sambat</small></span>
              <span><b>{formatFestivalDateRange(dates?.start_date, dates?.end_date)}</b><small>Gregorian</small></span>
              <span><b>{source.score}%</b><small>Source confidence</small></span>
            </div>
            <div className="festival-tag-row">
              {tags.map((tag) => <span key={tag}>{tag}</span>)}
            </div>
          </section>
          <aside className="panel countdown-card">
            <p className="eyebrow">Starts in</p>
            <h2>{countdownText(dates?.start_date)}</h2>
            <p>{formatBsDateRange(detailRow)}</p>
            <a className="primary-button" href={buildCalendarFeedUrl(festivalId)}>Add to calendar</a>
          </aside>
        </section>
        <section className="detail-workspace">
          <section className="panel detail-main">
            <div className="tab-row">
              {['rituals', 'meaning', 'calendar'].map((item) => (
                <button key={item} type="button" className={tab === item ? 'is-selected' : ''} onClick={() => setTab(item)}>{item}</button>
              ))}
            </div>
            <h2>{tab === 'rituals' ? 'Ritual sequence' : tab === 'meaning' ? 'Meaning and context' : 'Calendar window'}</h2>
            {tab === 'rituals' && (
              <>
                <p>{festival?.mythology?.significance || festival?.description || 'Structured ritual notes are loaded from the public festival profile when available.'}</p>
                <div className="ritual-list">
                  {(rituals.length ? rituals : [{ id: 'pending', day: 'API', title: 'Ritual notes pending', body: 'This observance is in the catalog, but detailed ritual sequencing is still being normalized.' }]).map((ritual, index) => (
                    <article key={ritual.id} className={index === 0 ? 'is-current' : ''}>
                      <span>0{index + 1}</span>
                      <div>
                        <strong>{ritual.title}</strong>
                        <p>{ritual.body}</p>
                      </div>
                      <time>{ritual.day}</time>
                    </article>
                  ))}
                </div>
              </>
            )}
            {tab === 'meaning' && (
              <div className="meaning-grid">
                <article>
                  <p className="eyebrow">Cultural meaning</p>
                  <h3>{festival?.mythology?.summary || 'Meaning profile'}</h3>
                  <p>{festival?.mythology?.significance || festival?.description || detailRow.summary}</p>
                </article>
                <article>
                  <p className="eyebrow">How Parva presents it</p>
                  <h3>Source-aware, not prescriptive</h3>
                  <p>The app separates public date confidence from local ritual practice so families and communities can still follow their trusted authority.</p>
                </article>
              </div>
            )}
            {tab === 'calendar' && (
              <div className="calendar-window-grid">
                <article>
                  <span>Primary date</span>
                  <strong>{formatBsDateRange(detailRow)}</strong>
                  <p>{formatFestivalDateRange(dates?.start_date, dates?.end_date)}</p>
                </article>
                <article>
                  <span>Source state</span>
                  <strong>{source.label}</strong>
                  <p>{dates?.calculation_method || 'Parva festival profile'}</p>
                </article>
                <article>
                  <span>Region</span>
                  <strong>{detailRow.regional_focus.length ? detailRow.regional_focus.join(', ') : 'Nepal-focused'}</strong>
                  <p>Regional practice may refine ritual time.</p>
                </article>
              </div>
            )}
          </section>
          <aside className="detail-rail">
            <section className="panel observance-note-panel">
              <p className="eyebrow">Observance notes</p>
              <h3>{detailRow.regional_focus.length ? detailRow.regional_focus.join(', ') : 'Nepal-focused'}</h3>
              <p>{detailRow.summary}</p>
              <Link to="/festivals">Return to inline list</Link>
            </section>
            <section className="panel provenance-panel">
              <div className="panel-heading tight">
                <p className="eyebrow">Provenance</p>
                <strong>{source.label}</strong>
              </div>
              <p>{dates?.calculation_method || 'Resolved through the Parva festival endpoint and source metadata.'}</p>
              {[
                { name: 'Timeline profile', note: meta?.method || 'API detail endpoint', confidence: source.score },
                { name: 'Quality band', note: meta?.quality_band || dates?.confidence || 'source-aware', confidence: source.score },
              ].map((item) => (
                <article key={item.name}>
                  <div>
                    <strong>{item.name}</strong>
                    <p>{item.note}</p>
                  </div>
                  <b>{item.confidence}%</b>
                </article>
              ))}
              <Link className="primary-button" to="/truth-lab">Open evidence</Link>
            </section>
            <section className="panel related-festivals-panel">
              <p className="eyebrow">Related observances</p>
              {related.length ? related.map((item) => (
                <Link key={item.id} to={`/festivals/${item.id}`}>
                  <FestivalArtwork festival={item} compact />
                  <span>{item.name}</span>
                  <small>{readableCategory(item.category)}</small>
                </Link>
              )) : <p className="festival-muted-note">No nearby observances were returned for this profile.</p>}
            </section>
          </aside>
        </section>
          </>
        )}
      </main>
    </AppChrome>
  );
}

export function RedesignBestTime() {
  const { state } = useTemporalContext();
  const [intent, setIntent] = useState('general');
  const [selectedId, setSelectedId] = useState('');
  const [selectedNotice, setSelectedNotice] = useState('');
  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [status, setStatus] = useState({ loading: true, error: '' });
  const intentOptions = [
    { value: 'general', label: 'General' },
    { value: 'worship', label: 'Worship' },
    { value: 'travel', label: 'Travel' },
    { value: 'business', label: 'Business' },
    { value: 'learning', label: 'Learning' },
  ];
  const windows = useMemo(() => (payload?.blocks || []).map(normalizeMuhurtaWindow), [payload?.blocks]);
  const selected = windows.find((window) => window.id === selectedId) || windows[0] || null;

  useEffect(() => {
    let cancelled = false;
    async function loadMuhurta() {
      await Promise.resolve();
      if (cancelled) return;
      setStatus({ loading: true, error: '' });
      try {
        const envelope = await muhurtaAPI.getHeatmapEnvelope({
          date: state.date,
          lat: state.location?.latitude,
          lon: state.location?.longitude,
          tz: state.timezone,
          type: intent,
          assumptionSet: 'np-mainstream-v2',
        });
        if (cancelled) return;
        setPayload(envelope.data || null);
        setMeta(envelope.meta || null);
        setSelectedId(String(envelope.data?.best_window?.index ?? envelope.data?.blocks?.[0]?.index ?? ''));
        setStatus({ loading: false, error: '' });
      } catch (error) {
        if (cancelled) return;
        setPayload(null);
        setMeta(null);
        setSelectedId('');
        setStatus({ loading: false, error: describeSupportError(error, 'Best-time data could not be loaded.') });
      }
    }
    loadMuhurta();
    return () => {
      cancelled = true;
    };
  }, [intent, state.date, state.location?.latitude, state.location?.longitude, state.timezone]);

  async function useSelectedWindow() {
    if (!selected) return;
    const summary = `${selected.name}: ${selected.time} on ${state.date} for ${readableCategory(intent)}`;
    try {
      await navigator.clipboard?.writeText(summary);
      setSelectedNotice('Copied selected time');
    } catch {
      setSelectedNotice('Selected time ready');
    }
  }

  return (
    <AppChrome>
      <main className="page-shell best-time-page">
        <PageHero
          title="Best Time / Muhurta"
          body="Find auspicious time windows for your important activities."
          action={<div className="hero-actions"><Link to="/panchanga">▣ {state.date}</Link><Link to="/my-place">⌖ {formatCoordinates(state.location)}</Link></div>}
        />
        <section className="planner-shell">
          <aside className="intent-panel">
            <h2>1. Choose your intent</h2>
            {intentOptions.map((item) => (
              <button key={item.value} type="button" className={intent === item.value ? 'is-selected' : ''} onClick={() => setIntent(item.value)}>{item.label}</button>
            ))}
            <p>{meta?.method || 'The backend evaluates panchanga, hora, chaughadia, and avoidance periods.'}</p>
          </aside>
          <section className="timeline-planner">
            <div className="panel-heading">
              <p className="eyebrow">2. Select your time window</p>
              <strong>{status.loading ? 'Loading...' : payload?.assumption_set_id || 'API'}</strong>
            </div>
            <div className="hour-axis"><span>12 AM</span><span>3 AM</span><span>6 AM</span><span>9 AM</span><span>12 PM</span><span>3 PM</span><span>6 PM</span><span>9 PM</span></div>
            <div className="timeline-chart">
              {windows.length ? windows.slice(0, 8).map((window) => (
                <button
                  key={window.id}
                  type="button"
                  className={`chart-row is-${window.type} ${selectedId === window.id ? 'is-selected' : ''}`}
                  onClick={() => setSelectedId(window.id)}
                >
                  <span>{window.name}</span>
                  <i style={{ left: `${window.left}%`, width: `${window.width}%` }}>{window.time}</i>
                </button>
              )) : <p className="festival-muted-note">{status.error || 'No windows were returned by the backend for this query.'}</p>}
              <div className="quality-stripes" aria-label="Day quality heatmap" />
            </div>
            <div className="recommended-windows">
              {windows.filter((window) => window.type === 'good').slice(0, 3).map((window) => (
                <button key={window.id} type="button" onClick={() => setSelectedId(window.id)}>
                  <small>{window.kind}</small>
                  <strong>{window.time}</strong>
                  <span>{window.name}</span>
                  <em>{window.reasonCodes.join(', ') || 'Backend ranked'}</em>
                </button>
              ))}
            </div>
          </section>
          <aside className="selected-window">
            <button type="button" className="close-button" aria-label="Clear selected window" onClick={() => setSelectedId('')}>×</button>
            <p>Selected window</p>
            <h2>{selected?.time || 'Pending'}</h2>
            <ScoreRing value={selected?.score || 0} label={selected?.kind || 'API'} />
            <ul>
              <li>Intent: {readableCategory(intent)}</li>
              <li>Window: {selected?.name || 'No backend window selected'}</li>
              <li>Class: {selected?.kind || 'Pending'}</li>
              <li>Reasons: {selected?.reasonCodes?.join(', ') || 'Returned by backend ranking.'}</li>
            </ul>
            <Confidence value={selected?.score || 0} />
            {selectedNotice ? <small className="selected-window__notice" role="status">{selectedNotice}</small> : null}
            <button type="button" className="primary-button" disabled={!selected} onClick={useSelectedWindow}>Use this time</button>
          </aside>
        </section>
      </main>
    </AppChrome>
  );
}

export function RedesignPanchanga() {
  const { state, setDate: setContextDate } = useTemporalContext();
  const [date, setDate] = useState(state.date);
  const [payload, setPayload] = useState(null);
  const [status, setStatus] = useState({ loading: true, error: '' });
  const calendarDays = useMemo(() => {
    const selected = new Date(`${date}T00:00:00`);
    if (Number.isNaN(selected.getTime())) return [];
    const year = selected.getFullYear();
    const month = selected.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    return Array.from({ length: daysInMonth }, (_, index) => index + 1);
  }, [date]);
  const panchangaItems = buildPanchangaItems({}, payload);
  const bsLabel = payload?.bikram_sambat ? formatBsDate(payload.bikram_sambat) : 'BS date pending';

  useEffect(() => {
    let cancelled = false;
    async function loadPanchanga() {
      await Promise.resolve();
      if (cancelled) return;
      setStatus({ loading: true, error: '' });
      try {
        const data = await calendarAPI.getPanchanga(date);
        if (cancelled) return;
        setPayload(data);
        setContextDate(date);
        setStatus({ loading: false, error: '' });
      } catch (error) {
        if (cancelled) return;
        setPayload(null);
        setStatus({ loading: false, error: describeSupportError(error, 'Panchanga data could not be loaded.') });
      }
    }
    loadPanchanga();
    return () => {
      cancelled = true;
    };
  }, [date, setContextDate]);

  return (
    <AppChrome>
      <main className="page-shell panchanga-page">
        <PageHero title="Date Converter & Panchanga" body="Convert between Gregorian (AD) and Bikram Sambat (BS)." />
        <section className="panchanga-workspace">
          <section className="panel converter-card">
            <h2>Date Converter</h2>
            <label>Gregorian (AD)<input type="date" value={date} onChange={(event) => setDate(event.target.value)} /></label>
            <button type="button" className="swap-button" onClick={() => setDate(todayIso())} aria-label="Reset converter to today">↺</button>
            <label>Bikram Sambat (BS)<input value={bsLabel} readOnly /></label>
            <div className="calendar-grid">
              {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((day) => <span key={day}>{day}</span>)}
              {calendarDays.map((day) => {
                const selectedDay = Number(date.slice(8, 10));
                return <button key={day} type="button" className={day === selectedDay ? 'is-selected' : ''} onClick={() => setDate(`${date.slice(0, 8)}${String(day).padStart(2, '0')}`)}>{day}</button>;
              })}
            </div>
            <Confidence value={payload?.bikram_sambat?.confidence === 'official' ? 100 : 72} label="Conversion confidence" />
          </section>
          <section className="panel panchanga-table">
            <div className="panel-heading">
              <p className="eyebrow">Panchanga for {bsLabel}</p>
              <a className="ghost-button" href={feedAPI.getAllLink(1)}>Add to calendar</a>
            </div>
            {status.loading ? <p className="festival-muted-note">Loading panchanga from the backend...</p> : null}
            {status.error ? <p className="birth-error" role="alert">{status.error}</p> : null}
            {[
              ...panchangaItems,
              { icon: '☼', label: 'Sunrise reference', value: formatTimeReference(payload?.panchanga?.tithi?.sunrise_used), meta: payload?.panchanga?.tithi?.reference_time || 'API' },
              { icon: '✣', label: 'Engine', value: payload?.ephemeris?.mode || 'Pending', meta: payload?.ephemeris?.library || 'API' },
            ].map((item) => (
              <article key={item.label}>
                <span>{item.icon}</span>
                <small>{item.label}</small>
                <strong>{item.value}</strong>
                <em>{item.meta}</em>
              </article>
            ))}
          </section>
          <aside className="panel provenance-card">
            <h2>Provenance</h2>
            <div><span>Primary source</span><strong>{payload?.bikram_sambat?.confidence || 'Pending'}</strong><small>{payload?.bikram_sambat?.source_range || 'Backend lookup'}</small></div>
            <div><span>Secondary source</span><strong>{payload?.panchanga?.confidence || 'Pending'}</strong><small>{payload?.ephemeris?.library || 'Backend panchanga'}</small></div>
            <div><span>Snapshot</span><strong>{payload?.provenance?.snapshot_id || 'Pending'}</strong><small>{payload?.provenance?.canonical_engine_id || 'API provenance'}</small></div>
            <Confidence value={payload?.panchanga?.confidence === 'astronomical' ? 92 : 70} />
          </aside>
        </section>
      </main>
    </AppChrome>
  );
}

function KundaliChart({ payload, selected, onSelect, mode }) {
  const houses = mode === 'd9' ? d9Houses(payload) : payload?.houses || [];
  const grahas = payload?.grahas || {};
  const lagna = payload?.lagna?.rashi_english || 'Unknown';

  return (
    <figure className="sacred-chart" aria-label={`${mode === 'd9' ? 'Navamsha' : 'North Indian'} Kundali chart`}>
      <div className="chart-toolbar">
        <div>
          <span>{mode === 'd9' ? 'D9 Navamsha' : 'D1 Rashi'}</span>
          <strong>{mode === 'd9' ? 'Navamsha Chakra' : `${lagna} Janma Kundali`}</strong>
        </div>
        <small>Interactive chart · click house or graha</small>
      </div>
      <div className="chart-canvas">
        <div className="chart-aura" aria-hidden="true">
          <span />
          <span />
          <span />
          <span />
        </div>
        <svg viewBox="0 0 100 100" className="chart-frame" aria-hidden="true">
          <defs>
            <linearGradient id="kundaliPaper" x1="0" x2="1" y1="0" y2="1">
              <stop offset="0%" stopColor="#fffaf0" />
              <stop offset="50%" stopColor="#fffefd" />
              <stop offset="100%" stopColor="#f4eadc" />
            </linearGradient>
            <radialGradient id="kundaliGlow" cx="50%" cy="50%" r="58%">
              <stop offset="0%" stopColor="#fffaf0" />
              <stop offset="64%" stopColor="#fff8ed" />
              <stop offset="100%" stopColor="#ecdcc8" />
            </radialGradient>
            <filter id="kundaliShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="4" stdDeviation="3" floodColor="#3b2a1b" floodOpacity="0.12" />
            </filter>
          </defs>
          <rect x="4.5" y="4.5" width="91" height="91" rx="8" fill="url(#kundaliPaper)" filter="url(#kundaliShadow)" />
          <rect x="7.5" y="7.5" width="85" height="85" rx="5.5" fill="url(#kundaliGlow)" />
          <path className="chart-grid-major" d="M50 7.5 L92.5 50 L50 92.5 L7.5 50 Z" />
          <path className="chart-grid-major" d="M7.5 7.5 L50 50 L92.5 92.5" />
          <path className="chart-grid-major" d="M92.5 7.5 L50 50 L7.5 92.5" />
          <path className="chart-grid-minor" d="M50 7.5 L50 92.5" />
          <path className="chart-grid-minor" d="M7.5 50 L92.5 50" />
          <circle cx="50" cy="50" r="7.5" />
          <path className="chart-grid-faint" d="M50 16 L84 50 L50 84 L16 50 Z" />
        </svg>
        {houses.map((house) => {
          const position = housePositions[house.house_number] || { x: 50, y: 50 };
          const isActive = selected?.type === 'house' && selected.id === house.house_number;
          return (
            <article
              key={house.house_number}
              className={`chart-house ${isActive ? 'is-active' : ''} ${house.house_number === 1 ? 'is-lagna' : ''}`}
              style={{ '--x': `${position.x}%`, '--y': `${position.y}%` }}
            >
              <button type="button" onClick={() => onSelect({ type: 'house', id: house.house_number, house })}>
                <span>{house.house_number}</span>
                <strong>{signShort[house.rashi_english] || house.rashi_english || 'Sign'}</strong>
                {house.house_number === 1 && mode === 'd1' ? <em>Ascendant</em> : null}
              </button>
              {house.occupants?.length ? (
                <div className="chart-grahas">
                  {house.occupants.map((id) => {
                    const graha = grahas[id] || {};
                    const grahaActive = selected?.type === 'graha' && selected.id === id;
                    return (
                      <button
                        key={id}
                        type="button"
                        className={grahaActive ? 'is-active' : ''}
                        title={`${graha.name_english || titleCase(id)} in ${graha.rashi_english || house.rashi_english || 'sign'}`}
                        onClick={(event) => {
                          event.stopPropagation();
                          onSelect({ type: 'graha', id, graha });
                        }}
                      >
                        {grahaShort[id] || titleCase(id).slice(0, 2)}
                      </button>
                    );
                  })}
                </div>
              ) : null}
            </article>
          );
        })}
        <button type="button" className="chart-center" onClick={() => onSelect(null)}>
          <span>{mode === 'd9' ? 'Navamsha' : 'Lagna'}</span>
          <strong>{mode === 'd9' ? 'D9' : lagna}</strong>
          <small>{selected ? 'Clear focus' : 'Select to inspect'}</small>
        </button>
      </div>
    </figure>
  );
}

function ReadingBrief({ payload, selected }) {
  const moon = payload?.grahas?.moon;
  const lagna = payload?.lagna;
  const dominant = strongestGraha(payload);
  const dasha = currentDasha(payload?.dasha?.timeline || []);
  const focusTitle = selected?.type === 'graha'
    ? selected.graha?.name_english || titleCase(selected.id)
    : selected?.type === 'house'
      ? `House ${selected.id}`
      : 'Opening read';
  const focusBody = selected?.type === 'graha'
    ? `${selected.graha?.name_english || titleCase(selected.id)} is in ${selected.graha?.rashi_english || 'its sign'} at ${Number(selected.graha?.degree_in_rashi || 0).toFixed(2)} degrees, with ${selected.graha?.dignity?.state || 'neutral'} dignity.`
    : selected?.type === 'house'
      ? `House ${selected.id} opens through ${selected.house?.rashi_english || 'this sign'}${selected.house?.occupants?.length ? ` and contains ${selected.house.occupants.map(titleCase).join(', ')}.` : ' and has no listed graha occupants.'}`
      : `This chart begins with ${lagna?.rashi_english || 'unknown'} rising and Moon in ${moon?.rashi_english || 'unknown'}, giving the reading a ${readingTraits[lagna?.rashi_english] || 'layered'} outer rhythm.`;

  return (
    <aside className="panel birth-brief">
      <div className="panel-heading tight">
        <p className="eyebrow">{focusTitle}</p>
        <strong>{selected ? 'Focused detail' : 'Primary anchors'}</strong>
      </div>
      <p>{focusBody}</p>
      <div className="anchor-stack">
        <div><span>Lagna</span><strong>{lagna?.rashi_english || 'Pending'}</strong></div>
        <div><span>Moon</span><strong>{moon?.rashi_english || 'Pending'}</strong></div>
        <div><span>Strongest pull</span><strong>{dominant ? `${dominant.name_english} in ${dominant.rashi_english}` : 'Pending'}</strong></div>
        <div><span>Current dasha</span><strong>{dasha ? titleCase(dasha.lord) : 'Unavailable'}</strong></div>
      </div>
      <Confidence value={86} label="Calculation confidence" />
      <small className="reading-disclaimer">Informational astrology assistance. Birth time precision, timezone, ayanamsha, and tradition affect interpretation.</small>
    </aside>
  );
}

function PlanetTable({ payload, selected, onSelect }) {
  return (
    <section className="panel graha-table-card">
      <div className="panel-heading">
        <p className="eyebrow">Planetary placements</p>
        <strong>Grahas, signs, degrees, and dignity</strong>
      </div>
      <div className="graha-table-wrap">
        <table className="graha-table">
          <thead>
            <tr><th>Graha</th><th>Rashi</th><th>Degree</th><th>D9</th><th>Dignity</th></tr>
          </thead>
          <tbody>
            {Object.entries(payload?.grahas || {}).map(([id, graha]) => (
              <tr key={id} className={selected?.type === 'graha' && selected.id === id ? 'is-active' : undefined}>
                <td><button type="button" onClick={() => onSelect({ type: 'graha', id, graha })}>{graha.name_english || titleCase(id)}</button></td>
                <td>{graha.rashi_english}</td>
                <td>{Number(graha.degree_in_rashi || 0).toFixed(2)}°</td>
                <td>{payload?.d9?.[id]?.navamsa_rashi_english || '—'}</td>
                <td>{titleCase(graha.dignity?.state || 'neutral')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function DashaTimeline({ payload }) {
  const periods = payload?.dasha?.timeline || [];
  const active = currentDasha(periods);
  return (
    <section className="panel dasha-card">
      <div className="panel-heading">
        <p className="eyebrow">Vimshottari dasha</p>
        <strong>{active ? `${titleCase(active.lord)} period is active now` : 'Timeline unavailable'}</strong>
      </div>
      <div className="dasha-rail">
        {periods.slice(0, 7).map((period) => (
          <article key={`${period.lord}-${period.start}`} className={period === active ? 'is-active' : ''}>
            <span>{titleCase(period.lord)}</span>
            <strong>{formatDateTime(period.start)} → {formatDateTime(period.end)}</strong>
            <small>{period.duration_years} years</small>
          </article>
        ))}
      </div>
    </section>
  );
}

function CalculationTrace({ payload, graphPayload }) {
  return (
    <section className="panel trace-card">
      <div className="panel-heading">
        <p className="eyebrow">Verify calculation</p>
        <strong>{payload?.method || 'swiss_ephemeris_sidereal'}</strong>
      </div>
      <div className="trace-grid">
        <div><span>Assumption set</span><strong>{payload?.assumption_set_id || 'np-kundali-v2'}</strong></div>
        <div><span>Trace ID</span><strong>{payload?.calculation_trace_id || graphPayload?.calculation_trace_id || 'Pending'}</strong></div>
        <div><span>Quality band</span><strong>{payload?.quality_band || 'validated'}</strong></div>
        <div><span>Advisory scope</span><strong>{payload?.advisory_scope || 'astrology_assist'}</strong></div>
      </div>
      <p>Swiss Ephemeris-based sidereal placements are used for calculation. Interpretive labels remain tradition-dependent and should stay transparent.</p>
    </section>
  );
}

export function RedesignBirthReading() {
  const { state } = useTemporalContext();
  const [form, setForm] = useState({
    name: '',
    date: '',
    time: '',
    place: '',
    lat: state.location?.latitude || '',
    lon: state.location?.longitude || '',
    tz: state.timezone || 'Asia/Kathmandu',
  });
  const [placeOptions, setPlaceOptions] = useState([]);
  const [placeStatus, setPlaceStatus] = useState({ loading: false, error: '' });
  const [payload, setPayload] = useState(null);
  const [graphPayload, setGraphPayload] = useState(null);
  const [selected, setSelected] = useState(null);
  const [chartMode, setChartMode] = useState('d1');
  const [status, setStatus] = useState({ loading: false, error: '' });
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));

  const applyPlace = (place) => {
    setForm((current) => ({
      ...current,
      place: place.label,
      lat: place.latitude,
      lon: place.longitude,
      tz: place.timezone,
    }));
  };

  useEffect(() => {
    const value = form.place.trim();
    if (value.length < 2) {
      return undefined;
    }
    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      setPlaceStatus({ loading: true, error: '' });
      try {
        const payload = await placesAPI.search({ query: value, limit: 5 });
        if (!cancelled) {
          setPlaceOptions(payload.items || []);
          setPlaceStatus({ loading: false, error: '' });
        }
      } catch (error) {
        if (!cancelled) {
          setPlaceOptions([]);
          setPlaceStatus({ loading: false, error: describeSupportError(error, 'Birth place search failed.') });
        }
      }
    }, 250);
    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [form.place]);

  const generate = async (event) => {
    event.preventDefault();
    setStatus({ loading: true, error: '' });
    setSelected(null);
    try {
      const request = {
        datetime: `${form.date}T${form.time}:00`,
        lat: form.lat,
        lon: form.lon,
        tz: form.tz,
      };
      const [kundali, graphEnvelope] = await Promise.all([
        kundaliAPI.getKundali(request),
        kundaliAPI.getGraphEnvelope(request),
      ]);
      setPayload(kundali);
      setGraphPayload(graphEnvelope.data || null);
    } catch (error) {
      setPayload(null);
      setGraphPayload(null);
      setStatus({ loading: false, error: describeSupportError(error, 'Birth chart generation failed.') });
      return;
    }
    setStatus({ loading: false, error: '' });
  };

  return (
    <AppChrome>
      <main className="page-shell birth-page">
        <PageHero title="Birth Reading" body="A real Kundali instrument: exact birth inputs, Swiss Ephemeris-backed sidereal calculation, interactive D1/D9 charts, dasha timing, and visible provenance." />
        <section className="birth-workspace">
          <form className="panel birth-form" onSubmit={generate}>
            <div className="panel-heading tight">
              <p className="eyebrow">Create chart</p>
              <strong>Birth details</strong>
            </div>
            <label>Profile name<input value={form.name} onChange={(event) => update('name', event.target.value)} /></label>
            <label>Date of birth<input type="date" value={form.date} onChange={(event) => update('date', event.target.value)} /></label>
            <label>Exact birth time<input type="time" value={form.time} onChange={(event) => update('time', event.target.value)} /></label>
            <label>Birth place<input
              value={form.place}
              onChange={(event) => {
                update('place', event.target.value);
                if (event.target.value.trim().length < 2) {
                  setPlaceOptions([]);
                  setPlaceStatus({ loading: false, error: '' });
                }
              }}
              placeholder="Search backend places"
            /></label>
            <div className="place-result-strip">
              {placeStatus.loading ? <span>Searching...</span> : null}
              {placeStatus.error ? <span>{placeStatus.error}</span> : null}
              {placeOptions.map((place) => (
                <button key={`${place.label}-${place.latitude}`} type="button" onClick={() => applyPlace(place)}>
                  {place.label}
                  <small>{formatCoordinates(place)}</small>
                </button>
              ))}
            </div>
            <div className="coordinate-grid">
              <label>Latitude<input value={form.lat} onChange={(event) => update('lat', event.target.value)} /></label>
              <label>Longitude<input value={form.lon} onChange={(event) => update('lon', event.target.value)} /></label>
            </div>
            <label>Timezone<input value={form.tz} onChange={(event) => update('tz', event.target.value)} /></label>
            <div className="method-strip">
              <span>Method</span>
              <strong>Lahiri-style sidereal / Swiss Ephemeris</strong>
            </div>
            {status.error ? <p className="birth-error" role="alert">{status.error}</p> : null}
            <button type="submit" className="primary-button" disabled={status.loading || !form.date || !form.time || !form.lat || !form.lon}>
              {status.loading ? 'Calculating Kundali...' : 'Generate Kundali'}
            </button>
          </form>

          <section className="panel kundali-card" aria-label="Interactive Kundali chart">
            <div className="birth-chart-switch" role="tablist" aria-label="Chart type">
              <button type="button" className={chartMode === 'd1' ? 'is-active' : ''} onClick={() => setChartMode('d1')}>D1 Rashi</button>
              <button type="button" className={chartMode === 'd9' ? 'is-active' : ''} onClick={() => setChartMode('d9')}>D9 Navamsha</button>
            </div>
            {payload ? (
              <KundaliChart payload={payload} graphPayload={graphPayload} selected={selected} onSelect={setSelected} mode={chartMode} />
            ) : (
              <div className="chart-loading">
                <strong>{status.loading ? 'Calculating chart...' : 'Chart will appear here'}</strong>
                <p>Enter exact birth details to generate the Kundali.</p>
              </div>
            )}
          </section>

          {payload ? <ReadingBrief payload={payload} selected={selected} /> : (
            <aside className="panel birth-brief">
              <p className="eyebrow">Reading brief</p>
              <h2>Waiting for calculation</h2>
              <p>The interpretation appears only after real chart data is returned.</p>
            </aside>
          )}
        </section>

        {payload ? (
          <section className="birth-analysis-grid">
            <PlanetTable payload={payload} selected={selected} onSelect={setSelected} />
            <DashaTimeline payload={payload} />
            <CalculationTrace payload={payload} graphPayload={graphPayload} />
          </section>
        ) : null}
      </main>
    </AppChrome>
  );
}

export function RedesignIntegrations() {
  const [payload, setPayload] = useState(null);
  const [status, setStatus] = useState({ loading: true, error: '' });

  useEffect(() => {
    let cancelled = false;
    feedAPI.getCatalog({ years: 2, lang: 'en' })
      .then((data) => {
        if (!cancelled) {
          setPayload(data);
          setStatus({ loading: false, error: '' });
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setPayload(null);
          setStatus({ loading: false, error: describeSupportError(error, 'Integration catalog could not be loaded.') });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const presetCards = payload?.presets || [];
  const platformCards = Object.entries(payload?.platforms || {});

  return (
    <AppChrome>
      <main className="page-shell simple-grid">
        <PageHero title="Integrations" body="Feeds, widgets, calendar exports, and public API entry points." />
        {status.loading ? <article className="panel"><h2>Loading integrations</h2><p>Fetching feed catalog from the backend.</p></article> : null}
        {status.error ? <article className="panel"><h2>Integrations unavailable</h2><p>{status.error}</p></article> : null}
        {presetCards.map((item) => (
          <article className="panel" key={item.key || item.title}>
            <p className="eyebrow">Feed preset</p>
            <h2>{item.title}</h2>
            <p>{item.description}</p>
            <a className="text-link" href={item.feed_url}>Open feed</a>
          </article>
        ))}
        {platformCards.map(([key, item]) => (
          <article className="panel" key={key}>
            <p className="eyebrow">Calendar platform</p>
            <h2>{item.title}</h2>
            <p>{item.recommended_action}</p>
            <small>{item.sync_expectation}</small>
          </article>
        ))}
      </main>
    </AppChrome>
  );
}

function trustValue(value, fallback = 'Unavailable') {
  if (value === 0) return '0';
  if (value === false) return 'No';
  if (value === true) return 'Yes';
  if (value === undefined || value === null || value === '') return fallback;
  return String(value);
}

function formatBytes(value) {
  const bytes = Number(value);
  if (!Number.isFinite(bytes) || bytes <= 0) return 'Unavailable';
  if (bytes > 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  if (bytes > 1024) return `${Math.round(bytes / 1024)} KB`;
  return `${bytes} B`;
}

function useTrustSurface() {
  const [payload, setPayload] = useState({
    runtime: null,
    policy: null,
    benchmark: null,
    queue: null,
    boundary: null,
    differential: null,
    slo: null,
    playbooks: [],
  });
  const [status, setStatus] = useState({ loading: true, error: '' });

  useEffect(() => {
    let cancelled = false;
    Promise.allSettled([
      reliabilityAPI.getStatus(),
      policyAPI.get(),
      reliabilityAPI.getBenchmarkManifest(),
      reliabilityAPI.getSourceReviewQueue(),
      reliabilityAPI.getBoundarySuite(),
      reliabilityAPI.getDifferentialManifest(),
      reliabilityAPI.getSlos(),
      reliabilityAPI.getPlaybooks(),
    ]).then(([runtime, policy, benchmark, queue, boundary, differential, slo, playbooks]) => {
      if (cancelled) return;
      const rejected = [runtime, policy, benchmark, queue, boundary, differential, slo, playbooks]
        .filter((item) => item.status === 'rejected');
      const runtimeData = runtime.status === 'fulfilled' ? runtime.value : null;
      const policyData = policy.status === 'fulfilled' ? policy.value : null;
      setPayload({
        runtime: runtimeData?.runtime || null,
        policy: policyData?.policy || runtimeData?.policy || null,
        benchmark: benchmark.status === 'fulfilled' ? benchmark.value?.benchmark : null,
        queue: queue.status === 'fulfilled' ? queue.value?.queue : null,
        boundary: boundary.status === 'fulfilled' ? boundary.value?.boundary_suite : null,
        differential: differential.status === 'fulfilled' ? differential.value?.differential : null,
        slo: slo.status === 'fulfilled' ? slo.value?.slo : null,
        playbooks: playbooks.status === 'fulfilled' ? playbooks.value?.playbooks || [] : [],
      });
      setStatus({
        loading: false,
        error: rejected.length === 8
          ? describeSupportError(rejected[0].reason, 'Trust data could not be loaded from the backend.')
          : '',
      });
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return { ...payload, loading: status.loading, error: status.error };
}

function TrustNav({ current }) {
  const items = [
    { id: 'trust', label: 'Trust', to: '/trust' },
    { id: 'methodology', label: 'Methodology', to: '/methodology' },
    { id: 'truth', label: 'Truth Lab', to: '/truth-lab' },
    { id: 'about', label: 'About', to: '/about' },
    { id: 'policy', label: 'API Policy', to: '/policy' },
  ];
  return (
    <nav className="trust-nav" aria-label="Trust pages">
      {items.map((item) => (
        <NavLink key={item.id} to={item.to} className={item.id === current ? 'is-current' : undefined}>
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}

function TrustLoading({ loading, error }) {
  if (loading) {
    return (
      <article className="trust-alert">
        <span aria-hidden="true" />
        <div>
          <strong>Loading backend trust surfaces</strong>
          <p>Policy, reliability, benchmark, source review, and boundary data are being fetched live.</p>
        </div>
      </article>
    );
  }
  if (error) {
    return (
      <article className="trust-alert is-error">
        <span aria-hidden="true" />
        <div>
          <strong>Trust data unavailable</strong>
          <p>{error}</p>
        </div>
      </article>
    );
  }
  return null;
}

function TrustMetricCard({ eyebrow, title, value, detail, actionTo, actionLabel }) {
  return (
    <article className="trust-metric-card">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <strong>{value}</strong>
      <p>{detail}</p>
      {actionTo ? <Link className="text-link" to={actionTo}>{actionLabel || 'Open'}</Link> : null}
    </article>
  );
}

function TrustPageFrame({ current, eyebrow, title, body, action, children }) {
  return (
    <AppChrome>
      <main className="page-shell trust-page-shell">
        <PageHero eyebrow={eyebrow} title={title} body={body} action={action} />
        <TrustNav current={current} />
        {children}
      </main>
    </AppChrome>
  );
}

export function RedesignTrust() {
  const trust = useTrustSurface();
  const runtime = trust.runtime || {};
  const ephemeris = runtime.ephemeris || {};
  const queue = trust.queue || {};
  const policy = trust.policy || {};
  const endpoints = runtime.metrics?.endpoints || [];

  return (
    <TrustPageFrame
      current="trust"
      eyebrow="Trust Center"
      title="A calmer way to see what the engine knows."
      body="Every major surface is backed by API status, policy metadata, source inventory, and provenance-oriented reliability checks."
      action={<Link className="primary-button" to="/truth-lab">Inspect live evidence</Link>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="trust-hero-grid">
        <TrustMetricCard
          eyebrow="Runtime"
          title="Service state"
          value={readableCategory(runtime.status || 'Unavailable')}
          detail={`${endpoints.length} API surfaces have runtime metrics in the reliability feed.`}
          actionTo="/truth-lab"
          actionLabel="Open Truth Lab"
        />
        <TrustMetricCard
          eyebrow="Ephemeris"
          title="Calculation engine"
          value={trustValue(ephemeris.mode)}
          detail={`${trustValue(ephemeris.ayanamsa)} ayanamsa, ${trustValue(ephemeris.coordinate_system)} coordinates.`}
          actionTo="/methodology"
          actionLabel="Read methodology"
        />
        <TrustMetricCard
          eyebrow="Policy"
          title="Usage posture"
          value={readableCategory(policy.usage || 'Unavailable')}
          detail={trustValue(policy.advisory)}
          actionTo="/policy"
          actionLabel="Open policy"
        />
        <TrustMetricCard
          eyebrow="Source review"
          title="Promotion queue"
          value={trustValue(queue.total_items)}
          detail={`${trustValue(queue.summary?.ready_for_promotion, '0')} sources ready for review, ${trustValue(queue.summary?.high, '0')} high priority.`}
          actionTo="/truth-lab"
          actionLabel="Review sources"
        />
      </section>
      <section className="trust-feature-band">
        <div>
          <p className="eyebrow">What this means</p>
          <h2>Parva should show confidence without pretending certainty.</h2>
        </div>
        <p>
          Ritual dates and time windows can vary by authority, location, and boundary conditions. The app keeps those constraints visible instead of burying them behind decorative confidence language.
        </p>
      </section>
      <section className="trust-link-grid">
        {[
          ['Methodology', 'How date, place, source, and risk state become a result.', '/methodology'],
          ['Truth Lab', 'Live reliability status, benchmark manifests, source review queues, and boundary suites.', '/truth-lab'],
          ['API Policy', 'The exact advisory policy returned by the backend for consumers and integrators.', '/policy'],
          ['About', 'What Parva is, what it is not, and how to use it responsibly.', '/about'],
        ].map(([title, body, to]) => (
          <Link key={title} to={to}>
            <span>{title}</span>
            <p>{body}</p>
          </Link>
        ))}
      </section>
    </TrustPageFrame>
  );
}

export function RedesignMethodology() {
  const trust = useTrustSurface();
  const runtime = trust.runtime || {};
  const ephemeris = runtime.ephemeris || {};
  const cache = runtime.cache || {};
  const boundary = trust.boundary || {};
  const benchmark = trust.benchmark || {};
  const steps = [
    ['Context first', 'Date, timezone, latitude, longitude, and requested surface are normalized before interpretation.'],
    ['Compute openly', `${trustValue(ephemeris.library)} powers the current sidereal calculation path when the backend is healthy.`],
    ['Compare and classify', 'Festival and timing outputs carry support tiers, authority mode, quality band, and boundary sensitivity.'],
    ['Expose provenance', 'Policy, request IDs, source status, cache state, and benchmark signals stay close to the result.'],
  ];

  return (
    <TrustPageFrame
      current="methodology"
      eyebrow="Methodology"
      title="Evidence-led calculations, not decorative certainty."
      body="The method is designed around explicit inputs, source confidence, authority comparison, and visible limits."
      action={<Link className="ghost-button" to="/truth-lab">See live checks</Link>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="methodology-steps">
        {steps.map(([title, body], index) => (
          <article key={title}>
            <span>{String(index + 1).padStart(2, '0')}</span>
            <h2>{title}</h2>
            <p>{body}</p>
          </article>
        ))}
      </section>
      <section className="trust-evidence-grid">
        <article>
          <p className="eyebrow">Engine path</p>
          <h2>{trustValue(ephemeris.mode)}</h2>
          <dl>
            <div><dt>Ayanamsa</dt><dd>{trustValue(ephemeris.ayanamsa)}</dd></div>
            <div><dt>Accuracy</dt><dd>{trustValue(ephemeris.accuracy)}</dd></div>
            <div><dt>Library</dt><dd>{trustValue(ephemeris.library)}</dd></div>
          </dl>
        </article>
        <article>
          <p className="eyebrow">Cache and benchmark</p>
          <h2>{trustValue(cache.file_count)} artifacts</h2>
          <dl>
            <div><dt>Cache bytes</dt><dd>{formatBytes(cache.total_bytes)}</dd></div>
            <div><dt>Boundary samples</dt><dd>{trustValue(boundary.total_samples || benchmark.total_samples)}</dd></div>
            <div><dt>Manifest</dt><dd>{trustValue(benchmark.manifest_id || benchmark.version)}</dd></div>
          </dl>
        </article>
      </section>
    </TrustPageFrame>
  );
}

export function RedesignTruthLab() {
  const trust = useTrustSurface();
  const runtime = trust.runtime || {};
  const cache = runtime.cache || {};
  const benchmark = trust.benchmark || {};
  const boundary = trust.boundary || {};
  const differential = trust.differential || {};
  const queue = trust.queue || {};
  const endpoints = runtime.metrics?.endpoints || [];
  const endpointCards = endpoints.slice(0, 6);

  return (
    <TrustPageFrame
      current="truth"
      eyebrow="Truth Lab"
      title="Live evidence from the backend."
      body="Reliability status, benchmark manifests, source review queues, and endpoint health in one inspectable surface."
      action={<a className="ghost-button" href="/v3/api/reliability/status">Open JSON</a>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="truth-dashboard">
        <TrustMetricCard eyebrow="Runtime" title="Status" value={readableCategory(runtime.status)} detail={`${trustValue(runtime.warnings?.length, '0')} warnings reported.`} />
        <TrustMetricCard eyebrow="Cache" title="Artifacts" value={trustValue(cache.file_count)} detail={`${formatBytes(cache.total_bytes)} available for precomputed surfaces.`} />
        <TrustMetricCard eyebrow="Benchmark" title="Manifest" value={trustValue(benchmark.manifest_id || benchmark.version)} detail={`${trustValue(boundary.total_samples || benchmark.total_samples)} boundary or benchmark samples exposed.`} />
        <TrustMetricCard eyebrow="Sources" title="Review queue" value={trustValue(queue.total_items)} detail={`${trustValue(queue.summary?.ready_for_promotion, '0')} ready for promotion.`} />
      </section>
      <section className="truth-table-panel">
        <div className="panel-heading tight">
          <p className="eyebrow">Endpoint health</p>
          <strong>{endpointCards.length} surfaces</strong>
        </div>
        <div className="truth-endpoint-list">
          {endpointCards.map((item) => (
            <article key={item.path}>
              <span>{item.path}</span>
              <strong>{trustValue(item.p95_latency_ms)} ms</strong>
              <em>{trustValue(item.requests, '0')} requests · {trustValue(item.errors, '0')} errors</em>
            </article>
          ))}
          {!endpointCards.length ? <p className="festival-muted-note">No endpoint metrics were returned by the reliability API.</p> : null}
        </div>
      </section>
      <section className="trust-evidence-grid">
        <article>
          <p className="eyebrow">Boundary suite</p>
          <h2>{trustValue(boundary.status || boundary.generated_at)}</h2>
          <p>{trustValue(boundary.summary || 'Boundary results are exposed when the backend publishes this suite.')}</p>
        </article>
        <article>
          <p className="eyebrow">Differential manifest</p>
          <h2>{trustValue(differential.manifest_id || differential.version)}</h2>
          <p>{trustValue(differential.summary || 'Differential checks are loaded from the reliability manifest when available.')}</p>
        </article>
      </section>
    </TrustPageFrame>
  );
}

export function RedesignAbout() {
  const trust = useTrustSurface();
  const policy = trust.policy || {};
  const runtime = trust.runtime || {};

  return (
    <TrustPageFrame
      current="about"
      eyebrow="About Parva"
      title="A source-aware time layer for Nepal."
      body="Parva brings daily panchanga, festivals, muhurta windows, place context, and birth-reading tools into a single public reference interface."
      action={<Link className="primary-button" to="/today">Open today</Link>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="about-statement">
        <div>
          <p className="eyebrow">Product stance</p>
          <h2>Beautiful enough to use daily, careful enough to question.</h2>
        </div>
        <p>
          The app is intentionally advisory. It can compute, compare, and explain, but it should not replace trusted local authorities for ritual-critical decisions.
        </p>
      </section>
      <section className="trust-link-grid">
        {[
          ['Daily time', 'Today, panchanga signals, sunlight, and current timing windows.', '/today'],
          ['Festival calendar', 'A backend-backed list with computed, provisional, and inventory source states.', '/festivals'],
          ['Best time', 'Muhurta windows with score, class, and reason codes from the API.', '/best-time'],
          ['Birth reading', 'Kundali and graph surfaces tied to explicit place and time inputs.', '/birth-reading'],
        ].map(([title, body, to]) => (
          <Link key={title} to={to}>
            <span>{title}</span>
            <p>{body}</p>
          </Link>
        ))}
      </section>
      <section className="trust-evidence-grid">
        <article>
          <p className="eyebrow">Backend</p>
          <h2>{readableCategory(runtime.status || 'Unavailable')}</h2>
          <p>{trustValue(runtime.ephemeris?.notes, 'Runtime notes are loaded from the reliability endpoint.')}</p>
        </article>
        <article>
          <p className="eyebrow">Policy</p>
          <h2>Version {trustValue(policy.version)}</h2>
          <p>{trustValue(policy.advisory)}</p>
        </article>
      </section>
    </TrustPageFrame>
  );
}

export function RedesignApiPolicy() {
  const trust = useTrustSurface();
  const policy = trust.policy || {};
  const playbooks = trust.playbooks || [];

  return (
    <TrustPageFrame
      current="policy"
      eyebrow="API Policy"
      title="The contract should be visible before anyone builds on it."
      body="This page mirrors the backend policy endpoint and shows how Parva frames usage, advisory limits, and operational recovery."
      action={<a className="primary-button" href="/v3/api/policy">Open policy JSON</a>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="policy-contract">
        <article>
          <span>Usage</span>
          <strong>{readableCategory(policy.usage || 'Unavailable')}</strong>
          <p>Returned by `/v3/api/policy` for API consumers.</p>
        </article>
        <article>
          <span>Version</span>
          <strong>{trustValue(policy.version)}</strong>
          <p>Policy metadata version from the backend.</p>
        </article>
        <article>
          <span>Advisory</span>
          <strong>{policy.advisory ? 'Active' : 'Unavailable'}</strong>
          <p>{trustValue(policy.advisory)}</p>
        </article>
      </section>
      <section className="truth-table-panel">
        <div className="panel-heading tight">
          <p className="eyebrow">Reliability playbooks</p>
          <strong>{playbooks.length} backend playbooks</strong>
        </div>
        <div className="truth-endpoint-list">
          {playbooks.map((item) => (
            <article key={item.id}>
              <span>{readableCategory(item.id)}</span>
              <strong>{item.doc}</strong>
              <em>{item.summary}</em>
            </article>
          ))}
          {!playbooks.length ? <p className="festival-muted-note">No playbooks were returned by the reliability API.</p> : null}
        </div>
      </section>
    </TrustPageFrame>
  );
}

export function RedesignProfileSaved() {
  const { state } = useTemporalContext();

  return (
    <AppChrome>
      <main className="page-shell simple-grid">
        <PageHero title="Profile & Saved" body="Saved places, festivals, birth readings, and integrations." />
        <article className="panel"><h2>Current place</h2><p>{formatCoordinates(state.location)} · {state.timezone}</p><Link className="text-link" to="/my-place">Load place data</Link></article>
        <article className="panel"><h2>Saved festivals</h2><p>No saved festival backend is configured for this reference frontend.</p><Link className="text-link" to="/festivals">Browse API festivals</Link></article>
        <article className="panel"><h2>Calendar export</h2><p>Feed options are loaded from the backend integration catalog.</p><Link className="text-link" to="/integrations">Open integrations</Link></article>
      </main>
    </AppChrome>
  );
}
