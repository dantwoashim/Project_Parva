import { Braces } from 'lucide-react';
import {
  startTransition,
  useCallback,
  useEffect,
  useRef,
  useState,
} from 'react';
import { useTemporalContext } from '../../context/useTemporalContext';
import {
  calendarAPI,
  enterpriseAPI,
  festivalAPI,
  futureAPI,
} from '../../services/api';
import { describeSupportError } from '../../services/errorFormatting';
import { AppChrome } from '../experience/ExperienceCommon';
import { useParvaToast } from '../motion/ParvaToastContext';
import { endpointCatalog } from './endpointCatalog';
import {
  ApiInspector,
  ConverterTool,
  EndpointAtlas,
  EndpointAtlasPlaceholder,
  FestivalsTool,
  FiscalTool,
  FutureTool,
  PanchangaTool,
  RequestStatusIcon,
  WorkbenchHeader,
  requestStatusLabel,
  requestedWorkbenchTool,
  toolDefinitions,
} from './WorkspaceTools';

export function RedesignHome() {
  const { notify } = useParvaToast();
  const { state } = useTemporalContext();
  const [activeTool, setActiveTool] = useState(requestedWorkbenchTool);
  const [inspectorOpen, setInspectorOpen] = useState(false);
  const [selectedEndpoint, setSelectedEndpoint] = useState(endpointCatalog[0]);
  const [activity, setActivity] = useState([]);
  const [atlasReady, setAtlasReady] = useState(false);
  const requestCounter = useRef(0);
  const loadedTools = useRef(new Set());

  const [converterMode, setConverterMode] = useState('ad-bs');
  const [adDate, setAdDate] = useState(state.date);
  const [bsDate, setBsDate] = useState({
    year: String(new Date(`${state.date}T00:00:00`).getFullYear() + 57),
    month: '1',
    day: '1',
  });
  const [conversion, setConversion] = useState(null);
  const [conversionLoading, setConversionLoading] = useState(false);
  const [conversionError, setConversionError] = useState('');

  const [panchangaDate, setPanchangaDate] = useState(state.date);
  const [panchanga, setPanchanga] = useState(null);
  const [panchangaLoading, setPanchangaLoading] = useState(false);
  const [panchangaError, setPanchangaError] = useState('');

  const [festivals, setFestivals] = useState([]);
  const [festivalsLoading, setFestivalsLoading] = useState(false);
  const [festivalsError, setFestivalsError] = useState('');

  const [fiscalYear, setFiscalYear] = useState(String(new Date(`${state.date}T00:00:00`).getFullYear() + 57));
  const [fiscal, setFiscal] = useState(null);
  const [months, setMonths] = useState(null);
  const [fiscalLoading, setFiscalLoading] = useState(false);
  const [fiscalError, setFiscalError] = useState('');

  const [futureCapabilities, setFutureCapabilities] = useState(null);
  const [modelRiskCapabilities, setModelRiskCapabilities] = useState(null);
  const [futureLoading, setFutureLoading] = useState(false);
  const [futureError, setFutureError] = useState('');

  const trackRequest = useCallback(async ({ method, path, title, description, request }) => {
    const id = ++requestCounter.current;
    const started = performance.now();
    const pending = { id, method, path, title, description, status: 'loading' };
    setActivity((current) => [pending, ...current].slice(0, 6));
    setSelectedEndpoint((current) => (
      current.method === method
      && current.path === path
      && current.title === title
      && current.description === description
        ? current
        : { method, path, title, description }
    ));

    try {
      const payload = await request();
      const durationMs = Math.max(0, Math.round(performance.now() - started));
      setActivity((current) => current.map((item) => (
        item.id === id ? { ...item, status: 'success', durationMs, payload } : item
      )));
      return payload;
    } catch (error) {
      const durationMs = Math.max(0, Math.round(performance.now() - started));
      const message = describeSupportError(error, 'The API request could not be completed.');
      setActivity((current) => current.map((item) => (
        item.id === id ? { ...item, status: 'error', durationMs, error: message } : item
      )));
      throw error;
    }
  }, []);

  const runConversion = useCallback(async (mode = converterMode) => {
    setConversionLoading(true);
    setConversionError('');
    try {
      const isAdToBs = mode === 'ad-bs';
      const payload = await trackRequest({
        method: isAdToBs ? 'GET' : 'POST',
        path: isAdToBs ? '/v3/api/calendar/convert' : '/v3/api/calendar/bs-to-gregorian',
        title: isAdToBs ? 'AD to BS conversion' : 'BS to AD conversion',
        description: isAdToBs
          ? 'Convert a Gregorian date into Bikram Sambat.'
          : 'Convert a Bikram Sambat date into Gregorian.',
        request: () => (isAdToBs
          ? calendarAPI.convertGregorian(adDate)
          : calendarAPI.convertBsToGregorian({
            year: Number(bsDate.year),
            month: Number(bsDate.month),
            day: Number(bsDate.day),
          })),
      });
      setConversion(payload);
    } catch (error) {
      setConversion(null);
      setConversionError(describeSupportError(error, 'Date conversion is temporarily unavailable.'));
    } finally {
      setConversionLoading(false);
    }
  }, [adDate, bsDate.day, bsDate.month, bsDate.year, converterMode, trackRequest]);

  const runPanchanga = useCallback(async () => {
    setPanchangaLoading(true);
    setPanchangaError('');
    try {
      const payload = await trackRequest({
        method: 'GET',
        path: '/v3/api/calendar/panchanga',
        title: 'Panchanga',
        description: 'Calculate the sunrise-based day state.',
        request: () => calendarAPI.getPanchanga(panchangaDate, 'strict'),
      });
      setPanchanga(payload);
    } catch (error) {
      setPanchanga(null);
      setPanchangaError(describeSupportError(error, 'Panchanga is temporarily unavailable.'));
    } finally {
      setPanchangaLoading(false);
    }
  }, [panchangaDate, trackRequest]);

  const runFestivals = useCallback(async () => {
    setFestivalsLoading(true);
    setFestivalsError('');
    try {
      const payload = await trackRequest({
        method: 'GET',
        path: '/v3/api/festivals/upcoming',
        title: 'Upcoming festivals',
        description: 'Load source-qualified observances in the next 120 days.',
        request: () => festivalAPI.getUpcoming(120, 'computed'),
      });
      setFestivals(Array.isArray(payload?.festivals) ? payload.festivals : []);
    } catch (error) {
      setFestivals([]);
      setFestivalsError(describeSupportError(error, 'Upcoming festivals are temporarily unavailable.'));
    } finally {
      setFestivalsLoading(false);
    }
  }, [trackRequest]);

  const runFiscal = useCallback(async () => {
    setFiscalLoading(true);
    setFiscalError('');
    try {
      const [fiscalPayload, monthsPayload] = await Promise.all([
        trackRequest({
          method: 'GET',
          path: `/v3/api/enterprise/fiscal-year/${fiscalYear}`,
          title: 'Fiscal-year boundaries',
          description: `Resolve fiscal-year ${fiscalYear}.`,
          request: () => enterpriseAPI.getFiscalYear(fiscalYear),
        }),
        trackRequest({
          method: 'GET',
          path: `/v3/api/enterprise/bs-months/${fiscalYear}`,
          title: 'Published BS months',
          description: `Load all month lengths for ${fiscalYear} BS.`,
          request: () => enterpriseAPI.getBsMonths(fiscalYear),
        }),
      ]);
      setFiscal(fiscalPayload);
      setMonths(monthsPayload);
    } catch (error) {
      setFiscal(null);
      setMonths(null);
      setFiscalError(describeSupportError(error, 'Fiscal-year data is temporarily unavailable.'));
    } finally {
      setFiscalLoading(false);
    }
  }, [fiscalYear, trackRequest]);

  const runFuture = useCallback(async () => {
    setFutureLoading(true);
    setFutureError('');
    try {
      const [futurePayload, riskPayload] = await Promise.all([
        trackRequest({
          method: 'GET',
          path: '/v4/api/future-bs/capabilities',
          title: 'Future-BS capability',
          description: 'Load the public research scope and claim boundary.',
          request: () => futureAPI.getCapabilities(),
        }),
        trackRequest({
          method: 'GET',
          path: '/v5/api/calendar-model-risk/capabilities',
          title: 'Calendar model risk',
          description: 'Load public calendar model-risk capability metadata.',
          request: () => futureAPI.getModelRiskCapabilities(),
        }),
      ]);
      setFutureCapabilities(futurePayload);
      setModelRiskCapabilities(riskPayload);
    } catch (error) {
      setFutureCapabilities(null);
      setModelRiskCapabilities(null);
      setFutureError(describeSupportError(error, 'Future-BS capability metadata is temporarily unavailable.'));
    } finally {
      setFutureLoading(false);
    }
  }, [trackRequest]);

  useEffect(() => {
    let cancelled = false;
    let revealed = false;
    const revealAtlas = () => {
      if (cancelled || revealed) return;
      revealed = true;
      startTransition(() => setAtlasReady(true));
    };
    const timeoutId = window.setTimeout(revealAtlas, 80);
    const idleId = window.requestIdleCallback?.(revealAtlas, { timeout: 300 });
    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
      if (idleId != null) window.cancelIdleCallback?.(idleId);
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    queueMicrotask(() => {
      if (cancelled || loadedTools.current.has('convert')) return;
      loadedTools.current.add('convert');
      void runConversion('ad-bs');
    });
    return () => {
      cancelled = true;
    };
  }, [runConversion]);

  useEffect(() => {
    let cancelled = false;
    queueMicrotask(() => {
      if (cancelled || loadedTools.current.has(activeTool)) return;
      loadedTools.current.add(activeTool);
      if (activeTool === 'panchanga') void runPanchanga();
      if (activeTool === 'festivals') void runFestivals();
      if (activeTool === 'fiscal') void runFiscal();
      if (activeTool === 'future') void runFuture();
    });
    return () => {
      cancelled = true;
    };
  }, [activeTool, runFestivals, runFiscal, runFuture, runPanchanga]);

  const handleEndpointSelect = useCallback((endpoint) => {
    setSelectedEndpoint(endpoint);
    if (endpoint.tool) {
      setActiveTool(endpoint.tool);
      document.querySelector('.workbench-shell')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }, []);

  const handleCopy = async (value) => {
    try {
      await navigator.clipboard?.writeText(value);
      notify('Copied to clipboard', { detail: 'The API value is ready to paste.' });
    } catch {
      // Clipboard support is optional; the visible path remains selectable.
      notify('Clipboard unavailable', { detail: 'Select the visible value and copy it manually.', tone: 'warning' });
    }
  };

  const locationLabel = state.location?.label || 'Kathmandu, Nepal';
  const latestRequest = activity[0];
  const requestPath = selectedEndpoint?.path || latestRequest?.path || endpointCatalog[0].path;
  const requestStatus = latestRequest?.path === requestPath ? latestRequest.status : 'ready';

  return (
    <AppChrome>
      <main className="workspace-page">
        <WorkbenchHeader conversion={conversion} date={state.date} location={locationLabel} />

        <section className="workbench-shell" data-active-tool={activeTool} aria-label="Temporal API workbench">
          <nav className="tool-switcher" aria-label="Workbench tools">
            {toolDefinitions.map((tool) => {
              const Icon = tool.icon;
              return (
                <button
                  type="button"
                  key={tool.id}
                  className={activeTool === tool.id ? 'is-active' : ''}
                  onClick={() => setActiveTool(tool.id)}
                  aria-pressed={activeTool === tool.id}
                >
                  <Icon aria-hidden="true" />
                  <span>
                    <strong>{tool.label}</strong>
                    <small>{tool.description}</small>
                  </span>
                </button>
              );
            })}
          </nav>

          <div className="tool-canvas" data-active-tool={activeTool}>
            {activeTool === 'convert' ? (
              <ConverterTool
                mode={converterMode}
                setMode={setConverterMode}
                adDate={adDate}
                setAdDate={setAdDate}
                bsDate={bsDate}
                setBsDate={setBsDate}
                loading={conversionLoading}
                error={conversionError}
                result={conversion}
                onSubmit={(event) => {
                  event.preventDefault();
                  void runConversion();
                }}
              />
            ) : null}
            {activeTool === 'panchanga' ? (
              <PanchangaTool
                date={panchangaDate}
                setDate={setPanchangaDate}
                loading={panchangaLoading}
                error={panchangaError}
                result={panchanga}
                onSubmit={(event) => {
                  event.preventDefault();
                  void runPanchanga();
                }}
              />
            ) : null}
            {activeTool === 'festivals' ? (
              <FestivalsTool
                loading={festivalsLoading}
                error={festivalsError}
                festivals={festivals}
                onRefresh={() => void runFestivals()}
              />
            ) : null}
            {activeTool === 'fiscal' ? (
              <FiscalTool
                year={fiscalYear}
                setYear={setFiscalYear}
                loading={fiscalLoading}
                error={fiscalError}
                fiscal={fiscal}
                months={months}
                onSubmit={(event) => {
                  event.preventDefault();
                  void runFiscal();
                }}
              />
            ) : null}
            {activeTool === 'future' ? (
              <FutureTool
                loading={futureLoading}
                error={futureError}
                capabilities={futureCapabilities}
                modelRisk={modelRiskCapabilities}
                onRefresh={() => void runFuture()}
              />
            ) : null}
          </div>
          <div className="request-dock">
            <div>
              <RequestStatusIcon status={requestStatus} />
              <span>{requestStatusLabel(requestStatus)}</span>
              <code>{requestPath}</code>
            </div>
            <button
              type="button"
              onClick={() => setInspectorOpen((current) => !current)}
              aria-expanded={inspectorOpen}
            >
              <Braces aria-hidden="true" />
              {inspectorOpen ? 'Hide response' : 'Inspect response'}
            </button>
          </div>
          {inspectorOpen ? (
            <ApiInspector selected={selectedEndpoint} activity={activity} onCopy={handleCopy} />
          ) : null}
        </section>

        {atlasReady ? (
          <EndpointAtlas selected={selectedEndpoint} onSelect={handleEndpointSelect} />
        ) : (
          <EndpointAtlasPlaceholder />
        )}
      </main>
    </AppChrome>
  );
}
