import { Suspense, useEffect } from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { ErrorBoundary } from './components/UI/ErrorBoundary';
import { TemporalProvider } from './context/TemporalContext';
import { MemberProvider } from './context/MemberContext';
import { useTemporalContext } from './context/useTemporalContext';
import { resolveDocumentLanguage } from './i18n/locale';
import { trackEvent } from './services/analytics';
import {
  RedesignBestTime,
  RedesignBenchmark,
  RedesignBirthReading,
  RedesignDevelopers,
  RedesignEnterprise,
  RedesignFestivalDetail,
  RedesignFestivals,
  RedesignFutureBsResearch,
  RedesignHome,
  RedesignIntegrations,
  RedesignMyPlace,
  RedesignPanchanga,
  RedesignProfileSaved,
  RedesignAbout,
  RedesignApiPricing,
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

const routeSeo = {
  '/': {
    title: 'Project Parva - Nepali temporal infrastructure',
    description: 'Project Parva provides BS/AD conversion, fiscal-year logic, panchanga computation, festivals, and source-aware calendar validation for Nepali software systems.',
  },
  '/today': {
    title: 'Today - Parva',
    description: 'Today on Parva: BS/AD context, panchanga signals, observances, timing windows, and visible source evidence.',
  },
  '/my-place': {
    title: 'My Place - Parva',
    description: 'Set a private calculation place for sunrise, panchanga, festivals, and best-time windows.',
  },
  '/festivals': {
    title: 'Festivals - Parva',
    description: 'Browse source-aware Nepal festivals with calendar subscription and evidence export.',
  },
  '/best-time': {
    title: 'Best Time - Parva',
    description: 'Plan with ranked muhurta windows, caution periods, confidence, and plain-language method evidence.',
  },
  '/benchmark': {
    title: 'Benchmark - Project Parva',
    description: 'Nepali Time Reliability Benchmark v0 results for deterministic calendar behavior, source awareness, uncertainty handling, and review gates.',
  },
  '/birth-reading': {
    title: 'Birth Reading - Parva',
    description: 'Create a privacy-aware Kundali reading with visible assumptions, sample preview, and calculation trace.',
  },
  '/panchanga': {
    title: 'Panchanga - Parva',
    description: 'Convert dates, inspect panchanga signals, and review source-aware calendar evidence from Parva.',
  },
  '/trust': {
    title: 'Trust - Parva',
    description: 'Inspect Parva reliability, source coverage, method limits, policy, and live trust posture.',
  },
  '/methodology': {
    title: 'Methodology - Parva',
    description: 'Learn how Parva turns date, place, source, and risk state into calendar and timing results.',
  },
  '/truth-lab': {
    title: 'Truth Lab - Parva',
    description: 'Review live reliability, benchmark, source-review, and boundary evidence for Parva.',
  },
  '/policy': {
    title: 'API Policy - Parva',
    description: 'Read Parva advisory policy, API posture, and usage boundaries.',
  },
  '/developers': {
    title: 'Developers - Project Parva',
    description: 'API guidance for BS/AD conversion, fiscal-year logic, panchanga computation, festivals, and source-aware calendar validation.',
  },
  '/enterprise': {
    title: 'Enterprise - Project Parva',
    description: 'Calendar-risk validation for fiscal reports, schedules, transaction records, and Nepali software systems.',
  },
  '/future-bs': {
    title: 'Future BS Risk Research - Project Parva',
    description: 'Public-safe methodology for controlled future-BS month-length risk research with computed_prediction_not_official claim boundaries.',
  },
  '/pricing': {
    title: 'API Pricing - Parva',
    description: 'Create Parva API keys, start Khalti or eSewa checkout, request Payoneer invoices, and inspect quota usage.',
  },
};

function setMetaDescription(description) {
  let meta = document.querySelector('meta[name="description"]');
  if (!meta) {
    meta = document.createElement('meta');
    meta.setAttribute('name', 'description');
    document.head.appendChild(meta);
  }
  meta.setAttribute('content', description);
}

function seoForPath(pathname) {
  const festivalDetail = pathname.startsWith('/festivals/') ? routeSeo['/festivals'] : null;
  return routeSeo[pathname] || festivalDetail || {
    title: 'Project Parva - Nepali temporal infrastructure',
    description: 'Project Parva provides BS/AD conversion, fiscal-year logic, panchanga computation, festivals, and source-aware calendar validation for Nepali software systems.',
  };
}

function AppRoutes() {
  return (
    <Suspense fallback={<div className="app-loading">Loading Parva...</div>}>
      <Routes>
        <Route path="/" element={<RedesignHome />} />
        <Route path="/today" element={<RedesignToday />} />
        <Route path="/best-time" element={<RedesignBestTime />} />
        <Route path="/benchmark" element={<RedesignBenchmark />} />
        <Route path="/festivals" element={<RedesignFestivals />} />
        <Route path="/festivals/:festivalId" element={<RedesignFestivalDetail />} />
        <Route path="/my-place" element={<RedesignMyPlace />} />
        <Route path="/birth-reading" element={<RedesignBirthReading />} />
        <Route path="/time-lab" element={<Navigate to="/panchanga" replace />} />
        <Route path="/saved" element={<RedesignProfileSaved />} />
        <Route path="/profile" element={<RedesignProfileSaved />} />
        <Route path="/integrations" element={<RedesignIntegrations />} />
        <Route path="/developers" element={<RedesignDevelopers />} />
        <Route path="/enterprise" element={<RedesignEnterprise />} />
        <Route path="/future-bs" element={<RedesignFutureBsResearch />} />
        <Route path="/trust" element={<RedesignTrust />} />
        <Route path="/methodology" element={<RedesignMethodology />} />
        <Route path="/truth-lab" element={<RedesignTruthLab />} />
        <Route path="/about" element={<RedesignAbout />} />
        <Route path="/policy" element={<RedesignApiPolicy />} />
        <Route path="/policy/" element={<RedesignApiPolicy />} />
        <Route path="/pricing" element={<RedesignApiPricing />} />
        <Route path="/pricing/*" element={<RedesignApiPricing />} />
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
    const seo = seoForPath(location.pathname);
    document.title = seo.title;
    setMetaDescription(seo.description);
    trackEvent('route_viewed', {
      path: location.pathname,
      title: seo.title,
    });
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
