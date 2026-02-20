/**
 * Project Parva - Main App Router
 */

import { NavLink, Navigate, Route, Routes } from 'react-router-dom';
import { ErrorBoundary } from './components/UI/ErrorBoundary';
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
import './App.css';

function TopNav() {
  return (
    <header className="app-shell__header">
      <div className="app-shell__brand">
        <h1>Project Parva</h1>
        <p>Nepal&apos;s Temporal Authority Interface</p>
      </div>

      <nav className="app-shell__nav" aria-label="Primary">
        <NavLink to="/" end className={({ isActive }) => `nav-link interactive-surface interactive-press interactive-focus-ring ${isActive ? 'active' : ''}`}>
          Explorer
        </NavLink>
        <NavLink to="/panchanga" className={({ isActive }) => `nav-link interactive-surface interactive-press interactive-focus-ring ${isActive ? 'active' : ''}`}>
          Panchanga
        </NavLink>
        <NavLink to="/personal" className={({ isActive }) => `nav-link interactive-surface interactive-press interactive-focus-ring ${isActive ? 'active' : ''}`}>
          Personal
        </NavLink>
        <NavLink to="/muhurta" className={({ isActive }) => `nav-link interactive-surface interactive-press interactive-focus-ring ${isActive ? 'active' : ''}`}>
          Muhurta
        </NavLink>
        <NavLink to="/kundali" className={({ isActive }) => `nav-link interactive-surface interactive-press interactive-focus-ring ${isActive ? 'active' : ''}`}>
          Kundali
        </NavLink>
        <NavLink to="/feeds" className={({ isActive }) => `nav-link interactive-surface interactive-press interactive-focus-ring ${isActive ? 'active' : ''}`}>
          iCal Feeds
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => `nav-link interactive-surface interactive-press interactive-focus-ring ${isActive ? 'active' : ''}`}>
          Dashboard
        </NavLink>
      </nav>
    </header>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <div className="app-shell">
        <TopNav />
        <main className="app-shell__content">
          <Routes>
            <Route path="/" element={<FestivalExplorerPage />} />
            <Route path="/festivals/:festivalId" element={<FestivalDetailPage />} />
            <Route path="/panchanga" element={<PanchangaPage />} />
            <Route path="/personal" element={<PersonalPanchangaPage />} />
            <Route path="/muhurta" element={<MuhurtaPage />} />
            <Route path="/kundali" element={<KundaliPage />} />
            <Route path="/feeds" element={<FeedSubscriptionsPage />} />
            <Route path="/dashboard" element={<ParvaPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;
