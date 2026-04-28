import { Suspense, useEffect } from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { ErrorBoundary } from './components/UI/ErrorBoundary';
import { TemporalProvider } from './context/TemporalContext';
import { MemberProvider } from './context/MemberContext';
import { useTemporalContext } from './context/useTemporalContext';
import { resolveDocumentLanguage } from './i18n/locale';
import {
  RedesignBestTime,
  RedesignBirthReading,
  RedesignFestivalDetail,
  RedesignFestivals,
  RedesignIntegrations,
  RedesignMyPlace,
  RedesignPanchanga,
  RedesignProfileSaved,
  RedesignAbout,
  RedesignApiPolicy,
  RedesignMethodology,
  RedesignToday,
  RedesignTrust,
  RedesignTruthLab,
} from './redesign/ParvaRedesign.jsx';
import './styles/tokens.css';
import './index.css';
import './styles/layouts.css';
import './styles/interactions.css';
import './App.css';

function AppRoutes() {
  return (
    <Suspense fallback={<div className="app-loading">Loading Parva...</div>}>
      <Routes>
        <Route path="/" element={<Navigate to="/today" replace />} />
        <Route path="/today" element={<RedesignToday />} />
        <Route path="/best-time" element={<RedesignBestTime />} />
        <Route path="/festivals" element={<RedesignFestivals />} />
        <Route path="/festivals/:festivalId" element={<RedesignFestivalDetail />} />
        <Route path="/my-place" element={<RedesignMyPlace />} />
        <Route path="/birth-reading" element={<RedesignBirthReading />} />
        <Route path="/time-lab" element={<Navigate to="/panchanga" replace />} />
        <Route path="/saved" element={<RedesignProfileSaved />} />
        <Route path="/profile" element={<RedesignProfileSaved />} />
        <Route path="/integrations" element={<RedesignIntegrations />} />
        <Route path="/trust" element={<RedesignTrust />} />
        <Route path="/methodology" element={<RedesignMethodology />} />
        <Route path="/truth-lab" element={<RedesignTruthLab />} />
        <Route path="/about" element={<RedesignAbout />} />
        <Route path="/policy" element={<RedesignApiPolicy />} />
        <Route path="/policy/" element={<RedesignApiPolicy />} />
        <Route path="/panchanga" element={<RedesignPanchanga />} />
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

  useEffect(() => {
    const activeTheme = state.theme || 'warm-paper';
    document.documentElement.setAttribute('data-theme', activeTheme);
    document.documentElement.style.colorScheme = 'light';
    document.documentElement.lang = resolveDocumentLanguage(state.language);
  }, [state.language, state.theme]);

  useEffect(() => {
    setLastViewed(location.pathname);
  }, [location.pathname, setLastViewed]);

  return (
    <div className="app-shell app-shell--consumer" data-theme={state.theme || 'warm-paper'}>
      <AppRoutes />
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
