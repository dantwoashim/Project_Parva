import { Suspense, lazy, useEffect, useMemo, useState } from 'react';
import { Link, NavLink, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { ErrorBoundary } from './components/UI/ErrorBoundary';
import { AdvancedSettingsDrawer } from './components/UI/AdvancedSettingsDrawer';
import { SearchSheet } from './components/UI/SearchSheet';
import { MemberNoticeBar } from './components/UI/MemberNoticeBar';
import { TemporalProvider } from './context/TemporalContext';
import { MemberProvider } from './context/MemberContext';
import { useTemporalContext } from './context/useTemporalContext';
import { useMemberContext } from './context/useMemberContext';
import { findPresetByLocation } from './data/locationPresets';
import './index.css';
import './styles/tokens.css';
import './styles/interactions.css';
import './pages/TemporalCompassPage.css';
import './App.css';

const LandingPage = lazy(() => import('./pages/LandingPage').then((m) => ({ default: m.LandingPage })));
const AboutPage = lazy(() => import('./pages/AboutPage').then((m) => ({ default: m.AboutPage })));
const TemporalCompassPage = lazy(() => import('./pages/TemporalCompassPage').then((m) => ({ default: m.TemporalCompassPage })));
const FestivalExplorerPage = lazy(() => import('./pages/FestivalExplorerPage').then((m) => ({ default: m.FestivalExplorerPage })));
const FestivalDetailPage = lazy(() => import('./pages/FestivalDetailPage').then((m) => ({ default: m.FestivalDetailPage })));
const PanchangaPage = lazy(() => import('./pages/PanchangaPage').then((m) => ({ default: m.PanchangaPage })));
const FeedSubscriptionsPage = lazy(() => import('./pages/FeedSubscriptionsPage').then((m) => ({ default: m.FeedSubscriptionsPage })));
const PersonalPanchangaPage = lazy(() => import('./pages/PersonalPanchangaPage').then((m) => ({ default: m.PersonalPanchangaPage })));
const MuhurtaPage = lazy(() => import('./pages/MuhurtaPage').then((m) => ({ default: m.MuhurtaPage })));
const KundaliPage = lazy(() => import('./pages/KundaliPage').then((m) => ({ default: m.KundaliPage })));
const SavedPage = lazy(() => import('./pages/SavedPage').then((m) => ({ default: m.SavedPage })));
const ProfilePage = lazy(() => import('./pages/ProfilePage').then((m) => ({ default: m.ProfilePage })));
const MethodologyPage = lazy(() => import('./pages/MethodologyPage').then((m) => ({ default: m.MethodologyPage })));

const PRIMARY_LINKS = [
  { to: '/today', label: 'Today' },
  { to: '/best-time', label: 'Best Time' },
  { to: '/festivals', label: 'Festivals' },
  { to: '/birth-reading', label: 'Birth Reading' },
  { to: '/saved', label: 'Saved' },
];

const MOBILE_MENU_LINKS = [
  ...PRIMARY_LINKS,
  { to: '/my-place', label: 'My Place' },
  { to: '/profile', label: 'Profile' },
  { to: '/integrations', label: 'Integrations' },
  { to: '/methodology', label: 'Methodology' },
  { to: '/about', label: 'About' },
];

const BOTTOM_NAV_LINKS = [
  { to: '/today', label: 'Today' },
  { to: '/best-time', label: 'Best Time' },
  { to: '/festivals', label: 'Festivals' },
  { to: '/saved', label: 'Saved' },
  { to: '/profile', label: 'Profile' },
];

function ShellNavigation({ links, onNavigate }) {
  return (
    <>
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`.trim()}
          onClick={onNavigate}
        >
          {link.label}
        </NavLink>
      ))}
    </>
  );
}

function TopNav({ navOpen, onToggleNav, onOpenSearch, onOpenSettings, onCloseNav }) {
  const { state } = useTemporalContext();
  const { state: memberState } = useMemberContext();
  const activePreset = useMemo(() => findPresetByLocation(state.location), [state.location]);
  const hasLocalState = Boolean(
    memberState.savedPlaces.length
    || memberState.savedFestivals.length
    || memberState.savedReadings.length
    || memberState.reminders.length
    || memberState.integrations.length,
  );

  return (
    <header className="app-shell__header">
      <Link className="app-shell__brand" to="/">
        <span className="app-shell__brand-mark" aria-hidden="true" />
        <div>
          <h1>Parva</h1>
          <p>Calm guide to Nepal&apos;s sacred time</p>
        </div>
      </Link>

      <div className="app-shell__nav-shell">
        <nav className="app-shell__nav" aria-label="Primary">
          <ShellNavigation links={PRIMARY_LINKS} />
        </nav>
      </div>

      <div className="app-shell__actions">
        <button type="button" className="app-shell__utility-btn" onClick={onOpenSearch}>
          Search
        </button>
        <button type="button" className="app-shell__location-chip" onClick={onOpenSettings}>
          <span>Place</span>
          <strong>{activePreset?.label || 'Custom place'}</strong>
        </button>
        <Link className={`app-shell__profile-btn ${hasLocalState ? 'has-saved-state' : ''}`.trim()} to="/profile">
          Profile
        </Link>
        <button type="button" className="app-shell__menu-btn" onClick={onToggleNav}>
          {navOpen ? 'Close' : 'Menu'}
        </button>
      </div>

      {navOpen ? (
        <div className="app-shell__mobile-nav" role="dialog" aria-modal="true">
          <div className="app-shell__mobile-nav-inner">
            <ShellNavigation links={MOBILE_MENU_LINKS} onNavigate={onCloseNav} />
          </div>
        </div>
      ) : null}
    </header>
  );
}

function BottomNav() {
  return (
    <nav className="app-shell__bottom-nav" aria-label="Mobile primary">
      {BOTTOM_NAV_LINKS.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) => `app-shell__bottom-link ${isActive ? 'active' : ''}`.trim()}
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}

function AppRoutes() {
  return (
    <Suspense
      fallback={(
        <div className="glass-panel" style={{ minHeight: 240, display: 'grid', placeItems: 'center' }}>
          Loading Parva...
        </div>
      )}
    >
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/today" element={<TemporalCompassPage />} />
        <Route path="/best-time" element={<MuhurtaPage />} />
        <Route path="/festivals" element={<FestivalExplorerPage />} />
        <Route path="/festivals/:festivalId" element={<FestivalDetailPage />} />
        <Route path="/my-place" element={<PersonalPanchangaPage />} />
        <Route path="/birth-reading" element={<KundaliPage />} />
        <Route path="/saved" element={<SavedPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/integrations" element={<FeedSubscriptionsPage />} />
        <Route path="/methodology" element={<MethodologyPage />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/panchanga" element={<PanchangaPage />} />
        <Route path="/muhurta" element={<Navigate to="/best-time" replace />} />
        <Route path="/personal" element={<Navigate to="/my-place" replace />} />
        <Route path="/kundali" element={<Navigate to="/birth-reading" replace />} />
        <Route path="/feeds" element={<Navigate to="/integrations" replace />} />
        <Route path="/dashboard" element={<Navigate to="/today" replace />} />
        <Route path="/legacy-dashboard" element={<Navigate to="/today" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}

function AppFrame() {
  const location = useLocation();
  const { state, setLastViewed } = useTemporalContext();
  const { state: memberState, clearNotice } = useMemberContext();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [navOpen, setNavOpen] = useState(false);

  useEffect(() => {
    setLastViewed(location.pathname);
    const frame = window.requestAnimationFrame(() => {
      setSettingsOpen(false);
      setSearchOpen(false);
      setNavOpen(false);
    });

    return () => {
      window.cancelAnimationFrame(frame);
    };
  }, [location.pathname, setLastViewed]);

  return (
    <div className="app-shell app-shell--consumer" data-theme={state.theme}>
      <TopNav
        navOpen={navOpen}
        onToggleNav={() => setNavOpen((value) => !value)}
        onOpenSearch={() => setSearchOpen(true)}
        onOpenSettings={() => setSettingsOpen(true)}
        onCloseNav={() => setNavOpen(false)}
      />
      <MemberNoticeBar notice={memberState.notice} onDismiss={clearNotice} />
      <main className="app-shell__content">
        <AppRoutes />
      </main>
      <footer className="app-shell__footer">
        <div className="app-shell__footer-copy">
          <strong>Parva</strong>
          <span>A calm guide to Nepal&apos;s sacred time, with method available when you want it.</span>
        </div>
        <div className="app-shell__footer-links">
          <NavLink to="/about">About</NavLink>
          <NavLink to="/methodology">Methodology</NavLink>
          <NavLink to="/integrations">Integrations</NavLink>
          <a href="mailto:hello@parva.app">Contact</a>
          <a href="/developers/index.html">For developers</a>
        </div>
      </footer>
      <BottomNav />
      <SearchSheet open={searchOpen} onClose={() => setSearchOpen(false)} />
      <AdvancedSettingsDrawer open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <TemporalProvider>
        <MemberProvider>
          <AppFrame />
        </MemberProvider>
      </TemporalProvider>
    </ErrorBoundary>
  );
}

export default App;
