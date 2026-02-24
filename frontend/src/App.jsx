import { NavLink, Navigate, Route, Routes } from 'react-router-dom';
import { ErrorBoundary } from './components/UI/ErrorBoundary';
import { ModeSwitch } from './components/Mode/ModeSwitch';
import { TemporalProvider } from './context/TemporalContext';
import { TemporalCompassPage } from './pages/TemporalCompassPage';
import { ParvaPage } from './pages/ParvaPage';
import { FestivalExplorerPage } from './pages/FestivalExplorerPage';
import { FestivalDetailPage } from './pages/FestivalDetailPage';
import { PanchangaPage } from './pages/PanchangaPage';
import { FeedSubscriptionsPage } from './pages/FeedSubscriptionsPage';
import { PersonalPanchangaPage } from './pages/PersonalPanchangaPage';
import { MuhurtaPage } from './pages/MuhurtaPage';
import { KundaliPage } from './pages/KundaliPage';
import './index.css';
import './styles/tokens.css';
import './styles/interactions.css';
import './components/Mode/ModeSwitch.css';
import './pages/TemporalCompassPage.css';
import './App.css';

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
