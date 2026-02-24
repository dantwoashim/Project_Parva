import { Suspense, lazy } from 'react';
import { NavLink, Navigate, Route, Routes } from 'react-router-dom';
import { ErrorBoundary } from './components/UI/ErrorBoundary';
import { ModeSwitch } from './components/Mode/ModeSwitch';
import { TemporalProvider } from './context/TemporalContext';
import './index.css';
import './styles/tokens.css';
import './styles/interactions.css';
import './components/Mode/ModeSwitch.css';
import './pages/TemporalCompassPage.css';
import './App.css';

const TemporalCompassPage = lazy(() => import('./pages/TemporalCompassPage').then((m) => ({ default: m.TemporalCompassPage })));
const ParvaPage = lazy(() => import('./pages/ParvaPage').then((m) => ({ default: m.ParvaPage })));
const FestivalExplorerPage = lazy(() => import('./pages/FestivalExplorerPage').then((m) => ({ default: m.FestivalExplorerPage })));
const FestivalDetailPage = lazy(() => import('./pages/FestivalDetailPage').then((m) => ({ default: m.FestivalDetailPage })));
const PanchangaPage = lazy(() => import('./pages/PanchangaPage').then((m) => ({ default: m.PanchangaPage })));
const FeedSubscriptionsPage = lazy(() => import('./pages/FeedSubscriptionsPage').then((m) => ({ default: m.FeedSubscriptionsPage })));
const PersonalPanchangaPage = lazy(() => import('./pages/PersonalPanchangaPage').then((m) => ({ default: m.PersonalPanchangaPage })));
const MuhurtaPage = lazy(() => import('./pages/MuhurtaPage').then((m) => ({ default: m.MuhurtaPage })));
const KundaliPage = lazy(() => import('./pages/KundaliPage').then((m) => ({ default: m.KundaliPage })));

function FloatingParticles() {
  return (
    <div className="particles" aria-hidden="true">
      {Array.from({ length: 8 }).map((_, i) => (
        <div key={i} className="particle" />
      ))}
    </div>
  );
}

function TopNav() {
  return (
    <header className="app-shell__header">
      <div className="app-shell__brand">
        <div>
          <h1>Project Parva</h1>
          <p>Nepal&apos;s Temporal Authority Interface</p>
        </div>
      </div>

      <nav className="app-shell__nav" aria-label="Primary">
        <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Compass</NavLink>
        <NavLink to="/festivals" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Explorer</NavLink>
        <NavLink to="/panchanga" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Panchanga</NavLink>
        <NavLink to="/personal" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Personal</NavLink>
        <NavLink to="/muhurta" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Muhurta</NavLink>
        <NavLink to="/kundali" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Kundali</NavLink>
        <NavLink to="/feeds" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>Feeds</NavLink>
      </nav>

      <ModeSwitch compact />
    </header>
  );
}

function AppRoutes() {
  return (
    <Suspense
      fallback={(
        <div className="glass-panel" style={{ minHeight: 240, display: 'grid', placeItems: 'center' }}>
          Loading temporal view...
        </div>
      )}
    >
      <Routes>
        <Route path="/" element={<TemporalCompassPage />} />
        <Route path="/festivals" element={<FestivalExplorerPage />} />
        <Route path="/festivals/:festivalId" element={<FestivalDetailPage />} />
        <Route path="/panchanga" element={<PanchangaPage />} />
        <Route path="/personal" element={<PersonalPanchangaPage />} />
        <Route path="/muhurta" element={<MuhurtaPage />} />
        <Route path="/kundali" element={<KundaliPage />} />
        <Route path="/feeds" element={<FeedSubscriptionsPage />} />
        <Route path="/dashboard" element={<ParvaPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Suspense>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <TemporalProvider>
        <div className="app-shell">
          <FloatingParticles />
          <TopNav />
          <main className="app-shell__content">
            <AppRoutes />
          </main>
        </div>
      </TemporalProvider>
    </ErrorBoundary>
  );
}

export default App;
