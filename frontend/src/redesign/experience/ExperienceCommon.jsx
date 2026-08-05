/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { Link, NavLink, useLocation, useParams } from '@parva/router';
import { m as Motion } from 'motion/react';
import {
  ArrowLeftRight,
  Bookmark,
  CalendarDays,
  CalendarRange,
  CircleHelp,
  Code2,
  FlaskConical,
  Gauge,
  Landmark,
  Library,
  MapPin,
  Menu,
  Search,
  Scale,
  ShieldCheck,
  Sparkles,
  Sun,
  UserRound,
  X,
} from 'lucide-react';
import {
  billingAPI,
  calendarAPI,
  feedAPI,
  festivalAPI,
  kundaliAPI,
  muhurtaAPI,
  placesAPI,
  policyAPI,
  reliabilityAPI,
  temporalAPI,
} from '../../services/api';
import { todayIso } from '../../context/temporalContextState';
import { useTemporalContext } from '../../context/useTemporalContext';
import { useFestivalDetail } from '../../hooks/useFestivals';
import useBackendCapabilities from '../../hooks/useBackendCapabilities';
import usePersonalPlaceBundle from '../../hooks/usePersonalPlaceBundle';
import useTodayBundle from '../../hooks/useTodayBundle';
import { apiHref } from '../../services/apiBase';
import { describeSupportError } from '../../services/errorFormatting';
import {
  categoryVisualMeta,
  defaultFestivalFilters,
  fallbackFestivalCategories,
  fallbackFestivalRegions,
  festivalMonths,
  festivalQualityOptions,
  festivalSortOptions,
  festivalVisualMeta,
  grahaShort,
  housePositions,
  manualPaymentMethods,
  navItems,
  pricingPlans,
  readingTraits,
  sampleBirthProfile,
  signShort,
  sourceDots,
} from '../redesignStaticData';
import {
  addDaysToIsoDate as addDaysWithFallback,
  formatBsDate,
  formatCoordinates,
  formatDateTime,
  formatIsoDate,
  formatTimeRange,
  formatTimeReference,
  humanMethodLabel,
  normalizeMuhurtaWindow,
  placeLabelFromLocation,
  readableCategory,
  sourceFreshness,
  supportReference,
  titleCase,
} from '../formatters';
import {
  Confidence,
  InfoCell,
  ScoreRing,
  SourceDots,
  TimelineList,
  VerificationStrip,
} from '../components/VerificationComponents';
import '../ParvaRedesign.css';
import '../ParvaPolish.css';

const AppChromeNestingContext = createContext(false);

function addDaysToIsoDate(value, offset) {
  return addDaysWithFallback(value, offset, todayIso());
}

function routeFamily(pathname = '/') {
  if (pathname.startsWith('/festivals')) return 'festival';
  if (pathname === '/today' || pathname === '/panchanga' || pathname === '/best-time') return 'day';
  if (pathname === '/my-place') return 'place';
  if (pathname === '/birth-reading') return 'birth';
  if (pathname === '/future-bs') return 'future';
  if (pathname === '/developers' || pathname === '/integrations' || pathname === '/pricing' || pathname === '/licensing') return 'developer';
  if (
    pathname === '/trust'
    || pathname === '/truth-lab'
    || pathname === '/methodology'
    || pathname === '/policy'
    || pathname === '/benchmark'
    || pathname === '/proof'
  ) return 'trust';
  if (pathname === '/enterprise') return 'enterprise';
  return 'workspace';
}

function panchangaProofUrl(date) {
  const params = new URLSearchParams({ date: String(date || todayIso()).slice(0, 10), risk_mode: 'strict' });
  return apiHref(`/calendar/panchanga/proof-capsule?${params.toString()}`);
}

function buildPanchangaItems(compass = {}, panchangaPayload = null) {
  const compassData = compass || {};
  const signals = compassData.signals || {};
  const panchanga = panchangaPayload?.panchanga || {};
  const primary = compassData.primary_readout || panchanga.tithi || {};
  return [
    { icon: 'T', label: 'Tithi', value: primary.tithi_name || primary.name || 'Awaiting calculation', meta: primary.paksha ? readableCategory(primary.paksha) : 'Computed for sunrise' },
    { icon: 'P', label: 'Paksha', value: readableCategory(primary.paksha || panchanga.tithi?.paksha || 'Awaiting calculation'), meta: primary.tithi_number || panchanga.tithi?.number ? `Tithi ${primary.tithi_number || panchanga.tithi.number}` : 'Computed for date' },
    { icon: 'N', label: 'Nakshatra', value: signals.nakshatra?.name || panchanga.nakshatra?.name || 'Awaiting calculation', meta: signals.nakshatra?.pada ? `Pada ${signals.nakshatra.pada}` : 'Computed lunar position' },
    { icon: 'Y', label: 'Yoga', value: signals.yoga?.name || panchanga.yoga?.name || 'Awaiting calculation', meta: 'Computed solar-lunar angle' },
    { icon: 'K', label: 'Karana', value: signals.karana?.name || panchanga.karana?.name || 'Awaiting calculation', meta: 'Derived from tithi state' },
  ];
}

function buildDayFacts(compass = {}) {
  const horizon = (compass || {}).horizon || {};
  return [
    ['Sunrise', formatTimeReference(horizon.sunrise)],
    ['Sunset', formatTimeReference(horizon.sunset)],
    ['Rahu Kalam', horizon.rahu_kalam ? formatTimeRange(horizon.rahu_kalam.start, horizon.rahu_kalam.end) : 'Awaiting calculation'],
    ['Current window', horizon.current_muhurta?.name || 'Awaiting calculation'],
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

const shellIconByPath = {
  '/': ArrowLeftRight,
  '/today': Sun,
  '/my-place': MapPin,
  '/festivals': CalendarDays,
  '/benchmark': Gauge,
  '/best-time': Sparkles,
  '/birth-reading': UserRound,
  '/panchanga': CalendarRange,
  '/developers': Code2,
  '/enterprise': Landmark,
  '/future-bs': FlaskConical,
  '/integrations': Library,
  '/licensing': Scale,
  '/trust': ShieldCheck,
  '/saved': Bookmark,
};

function ShellNavLink({ item, onNavigate }) {
  const Icon = shellIconByPath[item.to] || CircleHelp;
  return (
    <NavLink to={item.to} end={item.to === '/'} aria-label={item.label} onClick={onNavigate}>
      <Icon aria-hidden="true" />
      <span>{item.label}</span>
    </NavLink>
  );
}

function NavigationMenu({ primaryItems, platformItems, onClose }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const previousActiveElement = document.activeElement;
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        onClose();
        return;
      }
      if (event.key !== 'Tab') return;

      const focusable = [...(dialogRef.current?.querySelectorAll(
        'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])',
      ) || [])];
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    };
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    window.addEventListener('keydown', handleKeyDown);
    dialogRef.current?.querySelector('button[aria-label="Close navigation"]')?.focus();
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener('keydown', handleKeyDown);
      previousActiveElement?.focus?.();
    };
  }, [onClose]);

  return (
    <div className="navigation-layer">
      <Motion.button
        type="button"
        className="navigation-scrim"
        aria-label="Close navigation"
        onClick={onClose}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.16 }}
      />
      <Motion.section
        id="parva-navigation-menu"
        ref={dialogRef}
        className="navigation-menu"
        role="dialog"
        aria-modal="true"
        aria-label="Project Parva navigation"
        initial={{ opacity: 0, y: -10, scale: 0.985 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -7, scale: 0.99 }}
        transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
      >
        <header>
          <div>
            <span className="brand-symbol" aria-hidden="true"><span /></span>
            <strong>Project Parva</strong>
          </div>
          <button type="button" className="close-button" onClick={onClose} aria-label="Close navigation">
            <X aria-hidden="true" />
          </button>
        </header>
        <div className="navigation-menu__groups">
          <section>
            <p>Product</p>
            <nav aria-label="Primary navigation">
              {primaryItems.map((item) => (
                <ShellNavLink key={item.to} item={item} onNavigate={onClose} />
              ))}
            </nav>
          </section>
          <section>
            <p>Platform</p>
            <nav aria-label="Platform navigation">
              {platformItems.map((item) => (
                <ShellNavLink key={item.to} item={item} onNavigate={onClose} />
              ))}
            </nav>
          </section>
        </div>
        <footer>
          <a href="https://api.prabinghimire1.com.np/docs">API reference</a>
          <Link to="/methodology" onClick={onClose}>Methodology</Link>
          <Link to="/policy" onClick={onClose}>Policy</Link>
        </footer>
      </Motion.section>
    </div>
  );
}

export function AppChrome({ children }) {
  const nested = useContext(AppChromeNestingContext);
  if (nested) return children;
  return <AppChromeRoot>{children}</AppChromeRoot>;
}

function AppChromeRoot({ children }) {
  const location = useLocation();
  const [searchOpen, setSearchOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const menuTriggerRef = useRef(null);
  const searchTriggerRef = useRef(null);
  const capabilities = useBackendCapabilities();
  const { state } = useTemporalContext();
  const [summary, setSummary] = useState(null);
  const visibleNavItems = useMemo(
    () => [
      { label: 'Workbench', to: '/' },
      ...capabilities.filterRoutes(navItems),
    ],
    [capabilities],
  );
  const platformNavItems = useMemo(
    () => capabilities.filterRoutes([
      { label: 'Developers', to: '/developers', requiredCapability: 'developerPreview' },
      { label: 'Enterprise', to: '/enterprise' },
      { label: 'Future BS', to: '/future-bs', requiredCapability: 'futureBsMethodology' },
      { label: 'Integrations', to: '/integrations', requiredCapability: 'integrationsPreview' },
      { label: 'Licensing', to: '/licensing' },
      { label: 'Saved', to: '/saved' },
      { label: 'Trust center', to: '/trust', requiredCapability: 'trustPreview' },
    ]),
    [capabilities],
  );
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

  useEffect(() => {
    const handleShortcut = (event) => {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k') {
        event.preventDefault();
        setSearchOpen(true);
      }
    };
    window.addEventListener('keydown', handleShortcut);
    return () => window.removeEventListener('keydown', handleShortcut);
  }, []);

  const closeMenu = useCallback(() => {
    setMenuOpen(false);
    menuTriggerRef.current?.focus();
  }, []);
  const closeSearch = useCallback(() => {
    setSearchOpen(false);
    searchTriggerRef.current?.focus();
  }, []);

  return (
    <AppChromeNestingContext.Provider value>
      <div className="parva-app" data-route-family={routeFamily(location.pathname)}>
        <div className="parva-main">
        <header className="parva-topbar">
          <div className="topbar-brand-cluster">
            <Link className="topbar-brand" to="/" aria-label="Parva home">
              <span className="brand-symbol" aria-hidden="true"><span /></span>
              <strong>Parva</strong>
            </Link>
            <button
              ref={menuTriggerRef}
              type="button"
              className="menu-trigger"
              onClick={() => setMenuOpen(true)}
              aria-label="Open navigation"
              aria-expanded={menuOpen}
              aria-controls="parva-navigation-menu"
              aria-haspopup="dialog"
            >
              <Menu aria-hidden="true" />
              <span>Menu</span>
            </button>
          </div>
          <div className="topbar-context-group">
            <Link className="topbar-context" to="/today" aria-label={`Current context ${bsLabel}, ${placeLabel}`}>
              <CalendarDays aria-hidden="true" />
              <span>
                <strong>{bsLabel}</strong>
                <small>{formatIsoDate(state.date, { month: 'short', day: 'numeric', year: 'numeric' })}</small>
              </span>
            </Link>
            <Link className="topbar-place" to="/my-place" aria-label={`Current place ${placeLabel}`}>
              <MapPin aria-hidden="true" />
              <span><strong>{placeLabel}</strong><small>{state.timezone}</small></span>
            </Link>
          </div>
          <div className="top-actions">
            <button
              ref={searchTriggerRef}
              type="button"
              className="search-trigger"
              onClick={() => setSearchOpen(true)}
            >
              <Search aria-hidden="true" />
              <span>Search</span>
              <kbd>Ctrl K</kbd>
            </button>
            <a
              className="docs-trigger"
              href="https://api.prabinghimire1.com.np/docs"
              aria-label="Open API documentation"
            >
              <Code2 aria-hidden="true" />
              <span>API docs</span>
            </a>
            <Link className="icon-button" to="/trust" aria-label="Open trust center">
              <ShieldCheck aria-hidden="true" />
            </Link>
          </div>
        </header>

        <div className="parva-stage">{children}</div>

        <footer className="parva-footer">
          <span>Project Parva</span>
          <nav aria-label="Footer links">
            <Link to="/methodology">Methodology</Link>
            <Link to="/policy">Policy</Link>
            <Link to="/licensing">Licensing</Link>
            <a href="https://github.com/dantwoashim/Project_Parva">Source</a>
          </nav>
          <small>AGPL-3.0-or-later</small>
        </footer>
      </div>

        {menuOpen ? (
          <NavigationMenu
            primaryItems={visibleNavItems}
            platformItems={platformNavItems}
            onClose={closeMenu}
          />
        ) : null}
        {searchOpen ? <SearchDialog onClose={closeSearch} /> : null}
      </div>
    </AppChromeNestingContext.Provider>
  );
}

function SearchDialog({ onClose }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const capabilities = useBackendCapabilities();
  const fromDate = useMemo(() => todayIso('Asia/Kathmandu'), []);
  const toDate = useMemo(() => addDaysToIsoDate(fromDate, 365), [fromDate]);
  const quickCommands = useMemo(() => [
    { label: 'Today', meta: 'Daily panchanga, source status, and best window', to: '/today', requiredCapability: 'coreCalendar' },
    { label: 'Best Time', meta: 'Ranked muhurta planner', to: '/best-time', requiredCapability: 'muhurtaPublic' },
    { label: 'Panchanga', meta: 'Date converter and almanac signals', to: '/panchanga', requiredCapability: 'panchangaPublic' },
    { label: 'My Place', meta: 'Private calculation context', to: '/my-place', requiredCapability: 'placeSearch' },
    { label: 'Birth Reading', meta: 'Privacy-aware Kundali workflow', to: '/birth-reading', requiredCapability: 'kundaliPreview' },
    { label: 'Trust', meta: 'Reliability, limits, and source evidence', to: '/trust', requiredCapability: 'trustPreview' },
  ].filter((item) => capabilities.isRouteVisible(item)), [capabilities]);

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
      let cancelled = false;
      queueMicrotask(() => {
        if (cancelled) return;
        setResults([]);
        setLoading(false);
      });
      return () => {
        cancelled = true;
      };
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
          ? (timeline.value.data?.groups || [])
            .flatMap((group) => group.items || [])
            .slice(0, 6)
            .map((item) => ({
              label: item.display_name || item.name || item.id,
              meta: `Festival result ${item.start_date || 'calendar result'}`,
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
          { label: 'Tithi', meta: 'Panchanga term · lunar day', to: '/panchanga' },
          { label: 'Nakshatra', meta: 'Panchanga term · lunar mansion', to: '/panchanga' },
          { label: 'Rahu Kalam', meta: 'Timing term · caution window', to: '/today' },
          { label: 'Swiss Ephemeris', meta: 'Method term · calculation engine', to: '/methodology' },
        ].filter((item) => `${item.label} ${item.meta}`.toLowerCase().includes(value.toLowerCase()));
        const commandRows = quickCommands
          .filter((item) => `${item.label} ${item.meta}`.toLowerCase().includes(value.toLowerCase()))
          .map((item) => ({ ...item, meta: `Command · ${item.meta}` }));
        setResults([...commandRows, ...supportRows, ...festivalRows, ...placeRows]);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }, 250);

    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [fromDate, query, quickCommands, toDate]);

  return (
    <Motion.div
      className="modal-layer"
      role="dialog"
      aria-modal="true"
      aria-label="Search Parva"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.16 }}
    >
      <Motion.button
        type="button"
        className="modal-scrim"
        onClick={onClose}
        aria-label="Close search"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
      />
      <Motion.section
        className="search-dialog"
        initial={{ opacity: 0, y: -14, scale: 0.985 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: -8, scale: 0.99 }}
        transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
      >
        <div className="search-input-row">
          <Search aria-hidden="true" />
          <input
            autoFocus
            aria-label="Search Parva"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search festivals, places, timings..."
          />
          <button type="button" onClick={onClose}>Close</button>
        </div>
        <div className="search-results">
          {loading ? <p className="festival-muted-note">Searching live calendar and place data...</p> : null}
          {!loading && query.trim().length < 2 ? (
            <>
              <p className="festival-muted-note">Type at least two characters to search live festival, place, method, and support data.</p>
              <div className="search-command-grid" aria-label="Quick commands">
                {quickCommands.map((item) => (
                  <Link key={item.to} to={item.to} onClick={onClose}>
                    <span>{item.label}</span>
                    <small>{item.meta}</small>
                  </Link>
                ))}
              </div>
            </>
          ) : null}
          {!loading && query.trim().length >= 2 && !results.length ? <p className="festival-muted-note">No matches found. Try a festival name, place, or topic like “trust”.</p> : null}
          {results.map((result) => (
            <Link key={result.to} to={result.to} onClick={onClose}>
              <span>{result.label}</span>
              <small>{result.meta}</small>
            </Link>
          ))}
        </div>
      </Motion.section>
    </Motion.div>
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

export {
  useEffect,
  useMemo,
  useRef,
  useState,
  Link,
  NavLink,
  useParams,
  billingAPI,
  calendarAPI,
  feedAPI,
  festivalAPI,
  kundaliAPI,
  muhurtaAPI,
  placesAPI,
  policyAPI,
  reliabilityAPI,
  temporalAPI,
  todayIso,
  useTemporalContext,
  useFestivalDetail,
  useBackendCapabilities,
  usePersonalPlaceBundle,
  useTodayBundle,
  apiHref,
  describeSupportError,
  categoryVisualMeta,
  defaultFestivalFilters,
  fallbackFestivalCategories,
  fallbackFestivalRegions,
  festivalMonths,
  festivalQualityOptions,
  festivalSortOptions,
  festivalVisualMeta,
  grahaShort,
  housePositions,
  manualPaymentMethods,
  navItems,
  pricingPlans,
  readingTraits,
  sampleBirthProfile,
  signShort,
  sourceDots,
  addDaysWithFallback,
  formatBsDate,
  formatCoordinates,
  formatDateTime,
  formatIsoDate,
  formatTimeRange,
  formatTimeReference,
  humanMethodLabel,
  normalizeMuhurtaWindow,
  placeLabelFromLocation,
  readableCategory,
  sourceFreshness,
  supportReference,
  titleCase,
  Confidence,
  InfoCell,
  ScoreRing,
  SourceDots,
  TimelineList,
  VerificationStrip,
  addDaysToIsoDate,
  panchangaProofUrl,
  buildPanchangaItems,
  buildDayFacts,
  currentDasha,
  strongestGraha,
  d9Houses,
  PageHero,
};
