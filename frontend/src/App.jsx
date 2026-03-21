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
import { resolveDocumentLanguage } from './i18n/locale';
import { useCopy } from './i18n/useCopy';
import { useDialogA11y } from './hooks/useDialogA11y';
import { useViewportWidth } from './hooks/useViewportWidth';
import {
  getActiveLaunchSection,
  getBottomNavItems,
  getFooterGroups,
  getPrimaryNavItems,
  getSideRailItems,
  getSupportNavItems,
  getSurfaceDescriptor,
} from './navigation/routeManifest';
import './styles/tokens.css';
import './index.css';
import './styles/layouts.css';
import './styles/interactions.css';
import './pages/TemporalCompassPage.css';
import './App.css';

const ConsumerHome = lazy(() => import('./pages/ConsumerHome').then((m) => ({ default: m.ConsumerHome })));
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

function ShellNavigation({ links, activeSectionId, onNavigate, initialFocusIndex = -1 }) {
  return (
    <>
      {links.map((link, index) => (
        <NavLink
          key={link.id}
          to={link.to}
          className={({ isActive }) => `nav-link ${(isActive || activeSectionId === link.id) ? 'active' : ''}`.trim()}
          onClick={onNavigate}
          data-dialog-initial-focus={index === initialFocusIndex ? 'true' : undefined}
        >
          {link.label}
        </NavLink>
      ))}
    </>
  );
}

function TopNav({
  compactHeader,
  navOpen,
  activeSectionId,
  onToggleNav,
  onOpenSearch,
  onOpenSettings,
  onCloseNav,
}) {
  const { state } = useTemporalContext();
  const { state: memberState } = useMemberContext();
  const { copy } = useCopy();
  const navDialogOpen = compactHeader && navOpen;
  const { dialogRef } = useDialogA11y(navDialogOpen, onCloseNav);
  const activePreset = useMemo(() => findPresetByLocation(state.location), [state.location]);
  const primaryNavItems = useMemo(() => getPrimaryNavItems(copy), [copy]);
  const supportNavItems = useMemo(() => getSupportNavItems(copy), [copy]);
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
        <span className="app-shell__brand-wordmark">Parva</span>
      </Link>

      <div className="app-shell__nav-shell">
        <nav className="app-shell__nav" aria-label="Primary">
          <ShellNavigation links={primaryNavItems} activeSectionId={activeSectionId} />
        </nav>
      </div>

      <div className="app-shell__actions">
        {!compactHeader ? <button type="button" className="app-shell__search-chip" onClick={onOpenSearch}>{copy('common.search')}</button> : null}
        {!compactHeader ? (
          <>
            <button type="button" className="app-shell__icon-btn" onClick={onOpenSettings} aria-label={copy('shell.place')}>
              <span className="material-symbols-outlined">location_on</span>
            </button>
            <Link className={`app-shell__icon-btn ${hasLocalState ? 'has-saved-state' : ''}`.trim()} to="/profile" aria-label={copy('shell.profile')}>
              <span className="material-symbols-outlined">account_circle</span>
            </Link>
            <div className="app-shell__location-summary">
              <span>{copy('shell.place')}</span>
              <strong>{activePreset?.label || 'Custom place'}</strong>
            </div>
          </>
        ) : (
          <button
            type="button"
            className="app-shell__menu-btn"
            style={{ display: 'inline-flex' }}
            onClick={onToggleNav}
          >
            {navDialogOpen ? copy('common.close') : copy('shell.menu')}
          </button>
        )}
      </div>

      {navDialogOpen ? (
        <div className="app-shell__mobile-nav" role="presentation" style={{ display: 'block' }} onClick={onCloseNav}>
          <div
            ref={dialogRef}
            className="app-shell__mobile-nav-inner"
            role="dialog"
            aria-modal="true"
            aria-label={copy('shell.mobileMenu')}
            onClick={(event) => event.stopPropagation()}
          >
            <ShellNavigation
              links={primaryNavItems}
              activeSectionId={activeSectionId}
              onNavigate={onCloseNav}
              initialFocusIndex={0}
            />
            <button type="button" className="nav-link" onClick={() => { onCloseNav(); onOpenSettings(); }}>
              {copy('shell.place')}
            </button>
            <p className="app-shell__mobile-section-title">{copy('shell.supportSection')}</p>
            {supportNavItems.map((item) => (
              <Link key={item.id} className="nav-link" to={item.to} onClick={onCloseNav}>
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      ) : null}
    </header>
  );
}

function SideRail({ activeSectionId }) {
  const { copy } = useCopy();
  const items = useMemo(() => getSideRailItems(copy), [copy]);
  return (
    <aside className="app-shell__side-rail" aria-label="Editorial quick links">
      <div className="app-shell__side-head">
        <div className="app-shell__side-avatar">
          <span className="material-symbols-outlined">spa</span>
        </div>
        <div className="app-shell__side-copy">
          <span className="app-shell__side-label">{copy('shell.quickPaths')}</span>
          <strong>Parva</strong>
        </div>
      </div>
      <nav className="app-shell__side-nav">
        {items.map((item) => (
          <NavLink
            key={item.id}
            to={item.to}
            className={({ isActive }) => `app-shell__side-link ${(isActive || activeSectionId === item.id) ? 'active' : ''}`.trim()}
            aria-label={item.label}
          >
            <span className="material-symbols-outlined app-shell__side-link-icon">{item.icon}</span>
            <span className="app-shell__side-link-label">{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

function BottomNav({ activeSectionId }) {
  const { copy } = useCopy();
  const items = useMemo(() => getBottomNavItems(copy), [copy]);
  return (
    <nav className="app-shell__bottom-nav" aria-label="Mobile tabs" style={{ display: 'grid' }}>
      {items.map((link) => (
        <NavLink
          key={link.id}
          to={link.to}
          className={({ isActive }) => `app-shell__bottom-link ${(isActive || activeSectionId === link.id) ? 'active' : ''}`.trim()}
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}

function SurfaceTierBanner({ surface }) {
  if (!surface) return null;

  return (
    <section className={`app-shell__surface-note app-shell__surface-note--${surface.tier}`.trim()}>
      <div className="app-shell__surface-note-copy">
        <p className="app-shell__surface-note-eyebrow">{surface.title}</p>
        <p>{surface.body}</p>
      </div>
      <nav className="app-shell__surface-note-links" aria-label={surface.title}>
        {surface.links.map((link) => (
          <Link key={link.to} to={link.to}>
            {link.label}
          </Link>
        ))}
      </nav>
    </section>
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
        <Route path="/" element={<ConsumerHome />} />
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
  const { copy } = useCopy();
  const viewportWidth = useViewportWidth();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [navOpen, setNavOpen] = useState(false);
  const footerGroups = useMemo(() => getFooterGroups(copy), [copy]);
  const compactHeader = viewportWidth <= 1180;
  const showBottomNav = viewportWidth <= 760;
  const showSideRail = viewportWidth > 1180;
  const activeSectionId = getActiveLaunchSection(location.pathname);
  const surfaceDescriptor = useMemo(
    () => getSurfaceDescriptor(location.pathname, copy),
    [copy, location.pathname],
  );

  const handleOpenSearch = () => {
    setSearchOpen(true);
  };

  useEffect(() => {
    const activeTheme = state.theme || 'warm-paper';
    document.documentElement.setAttribute('data-theme', activeTheme);
    document.documentElement.style.colorScheme = activeTheme === 'ink-black' ? 'dark' : 'light';
    document.documentElement.lang = resolveDocumentLanguage(state.language);
  }, [state.language, state.theme]);

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
    <div
      className={`app-shell app-shell--consumer ${showSideRail ? 'app-shell--with-rail' : ''}`.trim()}
      data-theme={state.theme || 'warm-paper'}
    >
      <TopNav
        compactHeader={compactHeader}
        navOpen={navOpen}
        activeSectionId={activeSectionId}
        onToggleNav={() => setNavOpen((value) => !value)}
        onOpenSearch={handleOpenSearch}
        onOpenSettings={() => setSettingsOpen(true)}
        onCloseNav={() => setNavOpen(false)}
      />
      {showSideRail ? <SideRail activeSectionId={activeSectionId} /> : null}
      <MemberNoticeBar notice={memberState.notice} onDismiss={clearNotice} />
      <main className="app-shell__content">
        <SurfaceTierBanner surface={surfaceDescriptor} />
        <AppRoutes />
      </main>
      <footer className="app-shell__footer">
        <div className="app-shell__footer-copy">
          <strong>Parva</strong>
          <span>Sacred Wisdom for the Digital Era.</span>
        </div>
        <div className="app-shell__footer-links">
          {footerGroups.map((group) => (
            <div key={group.title} className="app-shell__footer-group">
              <span className="app-shell__footer-title">{group.title}</span>
              <div className="app-shell__footer-group-links">
                {group.links.map((link) => (
                  <NavLink key={link.to} to={link.to}>{link.label}</NavLink>
                ))}
              </div>
            </div>
          ))}
          <div className="app-shell__footer-group">
            <span className="app-shell__footer-title">{copy('footer.support')}</span>
            <div className="app-shell__footer-group-links">
              <a href="mailto:hello@parva.app">{copy('common.contact')}</a>
              <a href="/developers/index.html">{copy('common.forDevelopers')}</a>
            </div>
          </div>
        </div>
      </footer>
      {showBottomNav ? <BottomNav activeSectionId={activeSectionId} /> : null}
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
