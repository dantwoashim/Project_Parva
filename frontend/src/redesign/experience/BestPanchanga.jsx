import {
  useEffect,
  useMemo,
  useState,
  Link,
  calendarAPI,
  feedAPI,
  muhurtaAPI,
  todayIso,
  useTemporalContext,
  describeSupportError,
  formatBsDate,
  formatIsoDate,
  formatTimeReference,
  humanMethodLabel,
  normalizeMuhurtaWindow,
  placeLabelFromLocation,
  readableCategory,
  sourceFreshness,
  supportReference,
  Confidence,
  ScoreRing,
  addDaysToIsoDate,
  panchangaProofUrl,
  buildPanchangaItems,
  AppChrome,
  PageHero,
} from './ExperienceCommon.jsx';
import {
  readableReason,
} from './festival/FestivalUtils.jsx';
import {
  CalendarDays,
  Copy,
  MapPin,
  RotateCcw,
  Sparkles,
  Sun,
  X,
} from 'lucide-react';
import { useParvaToast } from '../motion/ParvaToastContext.js';

export function RedesignBestTime() {
  const { notify } = useParvaToast();
  const { state } = useTemporalContext();
  const [intent, setIntent] = useState('general');
  const [selectedId, setSelectedId] = useState('');
  const [selectedNotice, setSelectedNotice] = useState('');
  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [status, setStatus] = useState({ loading: true, error: '' });
  const intentOptions = [
    { value: 'general', label: 'General' },
    { value: 'worship', label: 'Worship' },
    { value: 'travel', label: 'Travel' },
    { value: 'business', label: 'Business' },
    { value: 'learning', label: 'Learning' },
  ];
  const windows = useMemo(() => (payload?.blocks || []).map(normalizeMuhurtaWindow), [payload?.blocks]);
  const selected = windows.find((window) => window.id === selectedId) || windows[0] || null;
  const avoidWindow = windows.find((window) => window.type === 'bad');
  const viableWindows = windows.filter((window) => window.type === 'good');
  const cautionWindows = windows.filter((window) => window.type !== 'good');
  const strongestScore = viableWindows[0]?.score || selected?.score || 0;
  const confidenceLabel = strongestScore >= 80 ? 'High confidence' : strongestScore >= 55 ? 'Use with context' : 'Low confidence';
  const confidenceCaution = strongestScore < 55;
  const recommendationLabel = confidenceCaution ? 'Best available, low confidence' : 'Recommended first';
  const selectedGuidance = selected
    ? confidenceCaution
      ? `${selected.name} is the best available returned window for ${readableCategory(intent).toLowerCase()} in ${placeLabelFromLocation(state.location)}. Treat it as a cautious planning input.`
      : `${selected.name} is the strongest returned window for ${readableCategory(intent).toLowerCase()} in ${placeLabelFromLocation(state.location)}.`
    : 'Parva is checking the ranked muhurta response for this place and date.';
  const copyActionLabel = confidenceCaution ? 'Copy cautious result' : 'Copy result';

  useEffect(() => {
    let cancelled = false;
    async function loadMuhurta() {
      if (cancelled) return;
      setStatus({ loading: true, error: '' });
      try {
        const envelope = await muhurtaAPI.getHeatmapEnvelope({
          date: state.date,
          lat: state.location?.latitude,
          lon: state.location?.longitude,
          tz: state.timezone,
          type: intent,
          assumptionSet: 'np-mainstream-v2',
        });
        if (cancelled) return;
        setPayload(envelope.data || null);
        setMeta(envelope.meta || null);
        setSelectedId(String(envelope.data?.best_window?.index ?? envelope.data?.blocks?.[0]?.index ?? ''));
        setStatus({ loading: false, error: '' });
      } catch (error) {
        if (cancelled) return;
        setPayload(null);
        setMeta(null);
        setSelectedId('');
        setStatus({ loading: false, error: describeSupportError(error, 'Best-time data could not be loaded.') });
      }
    }
    loadMuhurta();
    return () => {
      cancelled = true;
    };
  }, [intent, state.date, state.location?.latitude, state.location?.longitude, state.timezone]);

  async function useSelectedWindow() {
    if (!selected) return;
    const summary = `${selected.name}: ${selected.time} on ${state.date} for ${readableCategory(intent)}`;
    try {
      await navigator.clipboard?.writeText(summary);
      setSelectedNotice('Copied selected time');
      notify('Time window copied', { detail: `${selected.name} - ${selected.time}` });
    } catch {
      setSelectedNotice('Selected time ready');
      notify('Clipboard unavailable', { detail: summary, tone: 'warning' });
    }
  }

  return (
    <AppChrome>
      <main className="page-shell best-time-page">
        <PageHero
          title="Best Time"
          body="Pick an intent, see the best available window, avoid the wrong one, and understand the confidence before acting."
          action={(
            <div className="hero-actions">
              <Link to="/panchanga"><CalendarDays aria-hidden="true" /> {formatIsoDate(state.date)}</Link>
              <Link to="/my-place"><MapPin aria-hidden="true" /> {placeLabelFromLocation(state.location)}</Link>
            </div>
          )}
        />
        <section className="best-answer-grid" aria-label="Best Time answer">
          <article className="best-answer-card">
            <p className={`eyebrow ${confidenceCaution ? 'is-caution' : ''}`}>{recommendationLabel}</p>
            <h2>{selected?.time || 'Checking today'}</h2>
            <p>{selectedGuidance}</p>
            <div>
              <span><strong>{selected?.score || 0}</strong><small>score</small></span>
              <span><strong>{readableCategory(intent)}</strong><small>intent</small></span>
              <span><strong>{humanMethodLabel(meta?.method, 'Ranked model')}</strong><small>method</small></span>
            </div>
            <button type="button" className="primary-button" disabled={!selected} onClick={useSelectedWindow}>
              <Copy aria-hidden="true" />
              {copyActionLabel}
            </button>
            <div className="best-next-actions" aria-label="Best Time next actions">
              <button type="button" onClick={() => setIntent('worship')}>Try worship</button>
              <Link to="/panchanga">Check date context</Link>
              <button type="button" onClick={() => setSelectedId(avoidWindow?.id || '')} disabled={!avoidWindow}>Show avoid window</button>
            </div>
          </article>
          <article className="best-constraint-card">
            <p className="eyebrow">Constraint to respect</p>
            <h2>{avoidWindow?.name || 'Avoid window pending'}</h2>
            <p>{avoidWindow ? `${avoidWindow.time} is marked as ${avoidWindow.kind.toLowerCase()}. Keep it visible when planning.` : 'No avoid window was returned yet. The timeline will show caution periods when available.'}</p>
            <Link className="ghost-button" to="/methodology">Review rules</Link>
          </article>
        </section>
        <section className="planner-validation-strip" aria-label="Best Time confidence and source status">
          <div>
            <span>Viable windows</span>
            <strong>{viableWindows.length ? `${viableWindows.length} found` : 'None found'}</strong>
            <small>{confidenceCaution ? 'No strong recommendation yet.' : viableWindows.length ? 'Use the selected window first.' : 'No window crossed the safe planning threshold.'}</small>
          </div>
          <div>
            <span>Caution windows</span>
            <strong>{cautionWindows.length}</strong>
            <small>Visible in the timeline before you commit.</small>
          </div>
          <div>
            <span>Confidence</span>
            <strong>{confidenceLabel}</strong>
            <small>{humanMethodLabel(meta?.method, 'Ranked muhurta model')}</small>
          </div>
          <div>
            <span>Fallback</span>
            <strong>{status.error ? 'Backend unavailable' : 'Live calculation'}</strong>
            <small>{status.error || sourceFreshness(meta, 'Fresh for this request')}</small>
          </div>
        </section>
        <section className="planner-shell">
          <aside className="intent-panel">
            <h2>1. Choose your intent</h2>
            {intentOptions.map((item) => (
              <button key={item.value} type="button" className={intent === item.value ? 'is-selected' : ''} onClick={() => setIntent(item.value)}>{item.label}</button>
            ))}
            <p>{humanMethodLabel(meta?.method, 'Parva weighs panchanga, hora, chaughadia, and avoidance periods for the selected intent.')}</p>
          </aside>
          <section className="timeline-planner">
            <div className="panel-heading">
              <p className="eyebrow">2. Select your time window</p>
              <strong>{status.loading ? 'Loading...' : humanMethodLabel(payload?.assumption_set_id, 'Nepal mainstream rules')}</strong>
            </div>
            <div className="hour-axis"><span>12 AM</span><span>3 AM</span><span>6 AM</span><span>9 AM</span><span>12 PM</span><span>3 PM</span><span>6 PM</span><span>9 PM</span></div>
            <div className="timeline-chart">
              {windows.length ? windows.slice(0, 8).map((window) => (
                <button
                  key={window.id}
                  type="button"
                  className={`chart-row is-${window.type} ${selectedId === window.id ? 'is-selected' : ''}`}
                  aria-label={`${window.name}, ${window.time}, ${window.kind}, score ${window.score}`}
                  aria-pressed={selectedId === window.id}
                  onClick={() => setSelectedId(window.id)}
                >
                  <span>{window.name}</span>
                  <i style={{ left: `${window.left}%`, width: `${window.width}%` }}>{window.time}</i>
                </button>
              )) : <p className="festival-muted-note">{status.error || 'No windows were returned by the backend for this query.'}</p>}
              <div className="quality-stripes" aria-label="Day quality heatmap" />
            </div>
            <div className="recommended-windows">
              {windows.filter((window) => window.type === 'good').slice(0, 3).map((window) => (
                <button key={window.id} type="button" aria-pressed={selectedId === window.id} onClick={() => setSelectedId(window.id)}>
                  <small>{window.kind}</small>
                  <strong>{window.time}</strong>
                  <span>{window.name}</span>
                  <em>{window.reasonCodes.map(readableReason).join(', ') || 'Recommended'}</em>
                </button>
              ))}
              {!viableWindows.length ? (
                <article className="no-window-card" role="status">
                  <strong>No safe window crossed threshold</strong>
                  <span>Try another date, loosen the intent, or review the caution periods before acting.</span>
                </article>
              ) : null}
            </div>
          </section>
          <aside className="selected-window">
            <button type="button" className="close-button" aria-label="Clear selected window" onClick={() => setSelectedId('')}>
              <X aria-hidden="true" />
            </button>
            <p>Selected window</p>
            <h2>{selected?.time || 'Choose a window'}</h2>
            <ScoreRing value={selected?.score || 0} label={selected?.kind || 'API'} />
            <ul>
              <li>Intent: {readableCategory(intent)}</li>
              <li>Window: {selected?.name || 'No backend window selected'}</li>
              <li>Class: {selected?.kind || 'Not selected'}</li>
              <li>Confidence: {confidenceLabel}</li>
              <li>Reasons: {selected?.reasonCodes?.map(readableReason).join(', ') || 'Recommended for the selected intent.'}</li>
            </ul>
            <Confidence value={selected?.score || 0} />
            {selectedNotice ? <small className="selected-window__notice" role="status">{selectedNotice}</small> : null}
            <button type="button" className="primary-button" disabled={!selected} onClick={useSelectedWindow}>
              <Copy aria-hidden="true" />
              Copy time details
            </button>
          </aside>
        </section>
      </main>
    </AppChrome>
  );
}

export function RedesignPanchanga() {
  const { state, setDate: setContextDate } = useTemporalContext();
  const [date, setDate] = useState(state.date);
  const [payload, setPayload] = useState(null);
  const [meta, setMeta] = useState(null);
  const [status, setStatus] = useState({ loading: true, error: '' });
  const calendarDays = useMemo(() => {
    const selected = new Date(`${date}T00:00:00`);
    if (Number.isNaN(selected.getTime())) return [];
    const year = selected.getFullYear();
    const month = selected.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    return Array.from({ length: daysInMonth }, (_, index) => index + 1);
  }, [date]);
  const panchangaItems = buildPanchangaItems({}, payload);
  const bsLabel = payload?.bikram_sambat ? formatBsDate(payload.bikram_sambat) : 'BS date pending';

  useEffect(() => {
    let cancelled = false;
    async function loadPanchanga() {
      await Promise.resolve();
      if (cancelled) return;
      setStatus({ loading: true, error: '' });
      try {
        const envelope = await calendarAPI.getPanchangaEnvelope(date, 'strict');
        if (cancelled) return;
        setPayload(envelope.data || null);
        setMeta(envelope.meta || null);
        setContextDate(date);
        setStatus({ loading: false, error: '' });
      } catch (error) {
        if (cancelled) return;
        setPayload(null);
        setMeta(null);
        setStatus({ loading: false, error: describeSupportError(error, 'Panchanga data could not be loaded.') });
      }
    }
    loadPanchanga();
    return () => {
      cancelled = true;
    };
  }, [date, setContextDate]);

  return (
    <AppChrome>
      <main className="page-shell panchanga-page">
        <PageHero
          title="Panchanga"
          body="Convert dates, inspect the almanac signals, and keep the calculation source visible before using the result."
          action={<div className="hero-actions"><a href={panchangaProofUrl(date)}>Export evidence</a><Link to="/methodology">How dates work</Link></div>}
        />
        <section className="date-semantics-strip" aria-label="Selected date semantics">
          <div>
            <span>Gregorian date</span>
            <strong>{formatIsoDate(date, { weekday: 'long' })}</strong>
            <small>Input date used by the API.</small>
          </div>
          <div>
            <span>Bikram Sambat</span>
            <strong>{bsLabel}</strong>
            <small>{humanMethodLabel(payload?.bikram_sambat?.confidence, 'Calendar conversion')}</small>
          </div>
          <div>
            <span>Place basis</span>
            <strong>{placeLabelFromLocation(state.location)}</strong>
            <small>{state.timezone}</small>
          </div>
          <div>
            <span>Source freshness</span>
            <strong>{status.loading ? 'Checking' : status.error ? 'Unavailable' : 'Fresh'}</strong>
            <small>{status.error || sourceFreshness(meta, 'Fresh for this request')}</small>
          </div>
        </section>
        <section className="panchanga-workspace">
          <section className="panel converter-card">
            <h2>Date Converter</h2>
            <label>Gregorian (AD)<input type="date" value={date} onChange={(event) => setDate(event.target.value)} /></label>
            <button type="button" className="swap-button" onClick={() => setDate(todayIso())} aria-label="Reset converter to today">
              <RotateCcw aria-hidden="true" />
            </button>
            <label>Bikram Sambat (BS)<input value={bsLabel} readOnly /></label>
            <div className="calendar-grid">
              {['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'].map((day) => <span key={day}>{day}</span>)}
              {calendarDays.map((day) => {
                const selectedDay = Number(date.slice(8, 10));
                const nextDate = `${date.slice(0, 8)}${String(day).padStart(2, '0')}`;
                return (
                  <button
                    key={day}
                    type="button"
                    className={day === selectedDay ? 'is-selected' : ''}
                    aria-label={`${formatIsoDate(nextDate)}${day === selectedDay ? ', selected' : ''}`}
                    aria-pressed={day === selectedDay}
                    onClick={() => setDate(nextDate)}
                    onKeyDown={(event) => {
                      const offsets = { ArrowLeft: -1, ArrowRight: 1, ArrowUp: -7, ArrowDown: 7 };
                      if (!(event.key in offsets)) return;
                      event.preventDefault();
                      setDate(addDaysToIsoDate(nextDate, offsets[event.key]));
                    }}
                  >
                    {day}
                  </button>
                );
              })}
            </div>
            <Confidence value={payload?.bikram_sambat?.confidence === 'official' ? 100 : 72} label="Conversion confidence" />
          </section>
          <section className="panel panchanga-table">
            <div className="panel-heading">
              <p className="eyebrow">Panchanga for {bsLabel}</p>
              <a className="ghost-button" href={feedAPI.getAllLink(1)}>Add to calendar</a>
            </div>
            {status.loading ? <p className="festival-muted-note">Loading panchanga for this date...</p> : null}
            {status.error ? <p className="birth-error" role="alert">{status.error}</p> : null}
            {[
              ...panchangaItems,
              { icon: <Sun aria-hidden="true" />, label: 'Sunrise reference', value: formatTimeReference(payload?.panchanga?.tithi?.sunrise_used), meta: humanMethodLabel(payload?.panchanga?.tithi?.reference_time, 'Local sunrise') },
              { icon: <Sparkles aria-hidden="true" />, label: 'Calculation', value: humanMethodLabel(payload?.ephemeris?.mode, 'Astronomical calculation'), meta: humanMethodLabel(payload?.ephemeris?.library, 'Ephemeris source') },
            ].map((item) => (
              <article key={item.label}>
                <span>{item.icon}</span>
                <small>{item.label}</small>
                <strong>{item.value}</strong>
                <em>{item.meta}</em>
              </article>
            ))}
          </section>
          <aside className="panel provenance-card">
            <h2>Provenance</h2>
            <div><span>Primary source</span><strong>{humanMethodLabel(payload?.bikram_sambat?.confidence, 'Verified calendar')}</strong><small>{payload?.bikram_sambat?.source_range || 'Source range pending'}</small></div>
            <div><span>Secondary source</span><strong>{humanMethodLabel(payload?.panchanga?.confidence, 'Astronomical calculation')}</strong><small>{humanMethodLabel(payload?.ephemeris?.library, 'Ephemeris source')}</small></div>
            <div><span>Evidence</span><strong>{supportReference(payload?.provenance?.snapshot_id || meta?.request_id)}</strong><small>{humanMethodLabel(payload?.provenance?.canonical_engine_id || meta?.method, 'Canonical engine')}</small></div>
            <Confidence value={payload?.panchanga?.confidence === 'astronomical' ? 92 : 70} />
            <a className="text-link" href={panchangaProofUrl(date)}>Export panchanga proof capsule</a>
          </aside>
        </section>
      </main>
    </AppChrome>
  );
}

