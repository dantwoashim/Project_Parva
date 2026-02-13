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
import './App.css';
import './index.css';

function TopNav() {
  return (
    <header className="app-shell__header">
      <div className="app-shell__brand">
        <h1>Project Parva</h1>
        <p>Nepali Festival Intelligence Platform</p>
      </div>

      <nav className="app-shell__nav" aria-label="Primary">
        <NavLink to="/" end className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          Explorer
        </NavLink>
        <NavLink to="/panchanga" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          Panchanga
        </NavLink>
        <NavLink to="/feeds" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          iCal Feeds
        </NavLink>
        <NavLink to="/dashboard" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
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
