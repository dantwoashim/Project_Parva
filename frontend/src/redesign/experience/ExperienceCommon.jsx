/* eslint-disable react-refresh/only-export-components */
import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, NavLink, useParams } from 'react-router-dom';
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
  footerGroups,
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

function addDaysToIsoDate(value, offset) {
  return addDaysWithFallback(value, offset, todayIso());
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

function AppChrome({ children }) {
  const [searchOpen, setSearchOpen] = useState(false);
  const capabilities = useBackendCapabilities();
  const { state } = useTemporalContext();
  const [summary, setSummary] = useState(null);
  const visibleNavItems = useMemo(() => capabilities.filterRoutes(navItems), [capabilities]);
  const visibleFooterGroups = useMemo(
    () => footerGroups
      .map((group) => ({
        ...group,
        links: capabilities.filterRoutes(group.links),
      }))
      .filter((group) => group.links.length > 0),
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

  return (
    <div className="parva-app">
      <header className="parva-topbar">
        <Link className="brand-mark" to="/" aria-label="Parva home">
          <span className="brand-symbol" aria-hidden="true"><span /></span>
          <span>Parva</span>
        </Link>
        <Link className="mobile-inline-context" to="/my-place" aria-label={`Current context ${bsLabel}, ${placeLabel}`}>
          <span>{bsLabel}</span>
          <strong>{placeLabel}</strong>
        </Link>
        <button type="button" className="mobile-inline-search" onClick={() => setSearchOpen(true)} aria-label="Search Parva">
          ⌕
        </button>
        <nav className="top-nav" aria-label="Primary navigation">
          {visibleNavItems.map((item) => (
            <NavLink key={item.to} to={item.to} aria-label={item.label}>
              <span className="nav-label-full">{item.label}</span>
              <span className="nav-label-short" aria-hidden="true">{item.shortLabel || item.label}</span>
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
            <small>Private workspace</small>
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
            <Link className="brand-mark footer-logo" to="/" aria-label="Parva home">
              <span className="brand-symbol" aria-hidden="true"><span /></span>
              <span>Parva</span>
            </Link>
            <p>
              Source-aware Nepal time, festival, panchanga, muhurta, and kundali tools.
              Built for daily clarity, visible provenance, and careful decisions.
            </p>
            <div className="footer-status" aria-label="Service status">
              <span><i aria-hidden="true" /> Verified API</span>
              <span>AGPL-3.0-or-later</span>
            </div>
          </div>
          <div className="footer-link-grid">
            {visibleFooterGroups.map((group) => (
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
          <span>Informational use only; verify ritual decisions with local authorities or a trusted panchang.</span>
          <span>© 2026 Parva. Source-aware temporal tools for Nepal.</span>
        </section>
      </footer>
      <nav className="bottom-nav" aria-label="Mobile navigation">
        {visibleNavItems.slice(0, 5).map((item) => (
          <NavLink key={item.to} to={item.to}>
            {item.shortLabel || item.label}
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
  footerGroups,
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
  AppChrome,
  PageHero,
};
