import {
  Activity,
  ArrowLeftRight,
  ArrowRight,
  Braces,
  Building2,
  CalendarDays,
  CalendarRange,
  Check,
  CheckCircle2,
  CircleAlert,
  Clock3,
  Code2,
  Copy,
  ExternalLink,
  FileJson2,
  FlaskConical,
  Landmark,
  LoaderCircle,
  Play,
  Search,
  ShieldCheck,
  Sun,
} from 'lucide-react';
import {
  memo,
  startTransition,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { Link } from 'react-router-dom';
import { useTemporalContext } from '../../context/useTemporalContext';
import { DEFAULT_PUBLIC_DOCS_URL } from '../../config/publicEndpoints';
import {
  calendarAPI,
  enterpriseAPI,
  festivalAPI,
  futureAPI,
} from '../../services/api';
import { describeSupportError } from '../../services/errorFormatting';
import {
  formatBsDate,
  formatIsoDate,
  readableCategory,
} from '../formatters';
import { AppChrome } from '../experience/ExperienceCommon';
import { useParvaToast } from '../motion/ParvaToastContext';
import { endpointCatalog, endpointGroups } from './endpointCatalog';

const toolDefinitions = [
  { id: 'convert', label: 'Convert', description: 'AD and BS', icon: ArrowLeftRight },
  { id: 'panchanga', label: 'Panchanga', description: 'Day signals', icon: Sun },
  { id: 'festivals', label: 'Festivals', description: 'Upcoming', icon: CalendarDays },
  { id: 'fiscal', label: 'Fiscal', description: 'Business rules', icon: Landmark },
  { id: 'future', label: 'Future BS', description: 'Model risk', icon: FlaskConical },
];

function requestedWorkbenchTool() {
  if (typeof window === 'undefined') return 'convert';
  const requested = new URLSearchParams(window.location.search).get('tool');
  return toolDefinitions.some((tool) => tool.id === requested) ? requested : 'convert';
}

const bsMonths = [
  'Baishakh',
  'Jestha',
  'Ashar',
  'Shrawan',
  'Bhadra',
  'Ashwin',
  'Kartik',
  'Mangsir',
  'Poush',
  'Magh',
  'Falgun',
  'Chaitra',
];

function safeJson(value) {
  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return '';
  }
}

function requestStatusLabel(status) {
  if (status === 'loading') return 'Running';
  if (status === 'success') return 'Complete';
  if (status === 'error') return 'Failed';
  return 'Ready';
}

function RequestStatusIcon({ status }) {
  if (status === 'loading') return <LoaderCircle className="is-spinning" aria-hidden="true" />;
  if (status === 'success') return <CheckCircle2 aria-hidden="true" />;
  if (status === 'error') return <CircleAlert aria-hidden="true" />;
  return <Code2 aria-hidden="true" />;
}

function methodClass(method) {
  return String(method || 'GET').toLowerCase();
}

function formatAdDate(value) {
  if (!value) return 'Date unavailable';
  return formatIsoDate(String(value).slice(0, 10), {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

function conversionView(payload, mode) {
  if (!payload || typeof payload !== 'object') return null;
  if (mode === 'bs-ad') {
    const bs = payload.bs || {};
    return {
      label: 'Gregorian date',
      primary: formatAdDate(payload.gregorian),
      secondary: bs.year ? formatBsDate(bs) : 'Bikram Sambat input',
      confidence: bs.confidence || payload.support_tier || 'computed',
      source: bs.source_range
        || payload.provenance?.calendar_context?.source_status
        || payload.provenance?.manifest_version
        || payload.engine_path
        || 'Parva calendar engine',
    };
  }

  const bs = payload.bikram_sambat || {};
  return {
    label: 'Bikram Sambat date',
    primary: bs.year ? formatBsDate(bs) : 'Result unavailable',
    secondary: formatAdDate(payload.gregorian),
    confidence: bs.confidence || payload.support_tier || 'computed',
    source: bs.source_range
      || payload.provenance?.calendar_context?.source_status
      || payload.provenance?.manifest_version
      || payload.engine_path
      || 'Parva calendar engine',
  };
}

function panchangaValue(payload, key, fallback = 'Pending') {
  const item = payload?.panchanga?.[key] || payload?.[key];
  if (typeof item === 'string' || typeof item === 'number') return String(item);
  return item?.name || item?.tithi_name || item?.name_english || item?.value || fallback;
}

function timeValue(value) {
  if (!value) return 'Pending';
  if (typeof value === 'string') {
    const match = value.match(/T(\d{2}:\d{2})/);
    return match ? match[1] : value;
  }
  return value.local_time || value.time || timeValue(value.local || value.utc);
}

function formatFestivalDate(value) {
  if (!value) return 'Date pending';
  return formatIsoDate(String(value).slice(0, 10), {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function WorkbenchHeader({ conversion, date, location }) {
  const bs = conversion?.bikram_sambat || {};
  const bsLabel = bs.year ? formatBsDate(bs) : 'BS date loading';

  return (
    <section className="workspace-masthead">
      <div className="workspace-heading">
        <div className="workspace-status">
          <span aria-hidden="true" />
          Nepal calendar workspace
        </div>
        <h1>Project Parva</h1>
        <p>Convert dates, inspect Panchanga, track festivals, and apply Nepali fiscal rules.</p>
      </div>
      <dl className="workspace-now" aria-label={`${formatAdDate(date)}, ${bsLabel}`}>
        <div><dt>BS</dt><dd>{bsLabel}</dd></div>
        <div><dt>AD</dt><dd>{formatAdDate(date)}</dd></div>
        <div><dt>Place</dt><dd>{location}</dd></div>
      </dl>
    </section>
  );
}

function ConverterTool({
  mode,
  setMode,
  adDate,
  setAdDate,
  bsDate,
  setBsDate,
  loading,
  error,
  result,
  onSubmit,
}) {
  const view = conversionView(result, mode);
  const path = mode === 'ad-bs'
    ? '/v3/api/calendar/convert'
    : '/v3/api/calendar/bs-to-gregorian';
  const method = mode === 'ad-bs' ? 'GET' : 'POST';

  return (
    <div className="tool-panel converter-tool">
      <div className="tool-heading">
        <div>
          <p className="tool-kicker">Calendar conversion</p>
          <h2>Convert a date</h2>
        </div>
        <div className="endpoint-inline">
          <span className={`method-badge is-${methodClass(method)}`}>{method}</span>
          <code>{path}</code>
        </div>
      </div>

      <div className="segmented-control" aria-label="Conversion direction">
        <button
          type="button"
          className={mode === 'ad-bs' ? 'is-active' : ''}
          onClick={() => setMode('ad-bs')}
          aria-pressed={mode === 'ad-bs'}
        >
          AD to BS
        </button>
        <button
          type="button"
          className={mode === 'bs-ad' ? 'is-active' : ''}
          onClick={() => setMode('bs-ad')}
          aria-pressed={mode === 'bs-ad'}
        >
          BS to AD
        </button>
      </div>

      <form className="converter-form" onSubmit={onSubmit}>
        {mode === 'ad-bs' ? (
          <label className="field-control field-control--wide">
            <span>Gregorian date</span>
            <input
              type="date"
              value={adDate}
              onChange={(event) => setAdDate(event.target.value)}
              required
            />
          </label>
        ) : (
          <div className="bs-date-fields">
            <label className="field-control">
              <span>Year</span>
              <input
                type="number"
                min="1900"
                max="2200"
                value={bsDate.year}
                onChange={(event) => setBsDate((current) => ({ ...current, year: event.target.value }))}
                required
              />
            </label>
            <label className="field-control">
              <span>Month</span>
              <select
                value={bsDate.month}
                onChange={(event) => setBsDate((current) => ({ ...current, month: event.target.value }))}
              >
                {bsMonths.map((month, index) => (
                  <option key={month} value={index + 1}>{index + 1}. {month}</option>
                ))}
              </select>
            </label>
            <label className="field-control">
              <span>Day</span>
              <input
                type="number"
                min="1"
                max="32"
                value={bsDate.day}
                onChange={(event) => setBsDate((current) => ({ ...current, day: event.target.value }))}
                required
              />
            </label>
          </div>
        )}
        <button className="run-button" type="submit" disabled={loading}>
          {loading ? <LoaderCircle className="is-spinning" aria-hidden="true" /> : <Play aria-hidden="true" />}
          {loading ? 'Converting' : 'Convert'}
        </button>
      </form>

      <div className={`result-stage${error ? ' is-error' : ''}`} aria-live="polite">
        {error ? (
          <>
            <CircleAlert aria-hidden="true" />
            <div>
              <small>Request failed</small>
              <strong>{error}</strong>
            </div>
          </>
        ) : view ? (
          <>
            <div className="result-mark"><Check aria-hidden="true" /></div>
            <div className="result-copy">
              <small>{view.label}</small>
              <strong>{view.primary}</strong>
              <span>{view.secondary}</span>
            </div>
            <dl className="result-meta">
              <div><dt>Confidence</dt><dd>{readableCategory(view.confidence)}</dd></div>
              <div><dt>Source</dt><dd>{readableCategory(view.source)}</dd></div>
            </dl>
          </>
        ) : (
          <div className="result-placeholder">
            <ArrowLeftRight aria-hidden="true" />
            <span>Choose a date and run the conversion.</span>
          </div>
        )}
      </div>
    </div>
  );
}

function PanchangaTool({ date, setDate, loading, error, result, onSubmit }) {
  const fields = [
    ['Tithi', panchangaValue(result, 'tithi')],
    ['Nakshatra', panchangaValue(result, 'nakshatra')],
    ['Yoga', panchangaValue(result, 'yoga')],
    ['Karana', panchangaValue(result, 'karana')],
  ];
  const sunrise = timeValue(result?.ephemeris?.sunrise || result?.sunrise);
  const sunset = timeValue(result?.ephemeris?.sunset || result?.sunset);

  return (
    <div className="tool-panel panchanga-tool">
      <div className="tool-heading">
        <div>
          <p className="tool-kicker">Sunrise-based day state</p>
          <h2>Inspect Panchanga</h2>
        </div>
        <div className="endpoint-inline">
          <span className="method-badge is-get">GET</span>
          <code>/v3/api/calendar/panchanga</code>
        </div>
      </div>
      <form className="inline-run-form" onSubmit={onSubmit}>
        <label className="field-control">
          <span>Gregorian date</span>
          <input type="date" value={date} onChange={(event) => setDate(event.target.value)} required />
        </label>
        <button className="run-button" type="submit" disabled={loading}>
          {loading ? <LoaderCircle className="is-spinning" aria-hidden="true" /> : <Play aria-hidden="true" />}
          Calculate
        </button>
      </form>
      {error ? <p className="tool-error" role="alert">{error}</p> : null}
      <div className="panchanga-readout" aria-live="polite">
        {fields.map(([label, value]) => (
          <div key={label}>
            <small>{label}</small>
            <strong>{value}</strong>
          </div>
        ))}
      </div>
      <div className="sun-track" aria-label={`Sunrise ${sunrise}, sunset ${sunset}`}>
        <span><Sun aria-hidden="true" /> Sunrise <strong>{sunrise}</strong></span>
        <i aria-hidden="true"><b /></i>
        <span><Clock3 aria-hidden="true" /> Sunset <strong>{sunset}</strong></span>
      </div>
      <div className="tool-actions">
        <Link to="/panchanga">Open full Panchanga <ArrowRight aria-hidden="true" /></Link>
        <Link to="/methodology">Read calculation method</Link>
      </div>
    </div>
  );
}

function FestivalsTool({ loading, error, festivals, onRefresh }) {
  return (
    <div className="tool-panel festival-tool">
      <div className="tool-heading">
        <div>
          <p className="tool-kicker">Source-qualified observances</p>
          <h2>Upcoming festivals</h2>
        </div>
        <button className="icon-action" type="button" onClick={onRefresh} disabled={loading} aria-label="Refresh festivals">
          <Activity className={loading ? 'is-spinning' : ''} aria-hidden="true" />
        </button>
      </div>
      <div className="festival-rail" aria-live="polite">
        {error ? <p className="tool-error" role="alert">{error}</p> : null}
        {!error && loading && !festivals.length ? (
          Array.from({ length: 4 }, (_, index) => <span className="festival-skeleton" key={index} />)
        ) : null}
        {festivals.slice(0, 5).map((festival, index) => (
          <Link key={festival.id || `${festival.name}-${index}`} to={`/festivals/${festival.id}`}>
            <span className="festival-index">{String(index + 1).padStart(2, '0')}</span>
            <div>
              <strong>{festival.display_name || festival.name || festival.id}</strong>
              <small>{readableCategory(festival.category || festival.quality_band || 'Festival')}</small>
            </div>
            <time>{formatFestivalDate(festival.start_date || festival.date)}</time>
            <ArrowRight aria-hidden="true" />
          </Link>
        ))}
        {!loading && !error && !festivals.length ? (
          <div className="empty-tool-state">
            <CalendarDays aria-hidden="true" />
            <p>No upcoming festivals were returned for this window.</p>
          </div>
        ) : null}
      </div>
      <div className="tool-actions">
        <Link to="/festivals">Explore festival calendar <ArrowRight aria-hidden="true" /></Link>
        <Link to="/integrations">Subscribe by calendar feed</Link>
      </div>
    </div>
  );
}

function FiscalTool({
  year,
  setYear,
  loading,
  error,
  fiscal,
  months,
  onSubmit,
}) {
  return (
    <div className="tool-panel fiscal-tool">
      <div className="tool-heading">
        <div>
          <p className="tool-kicker">Nepali business calendar</p>
          <h2>Fiscal year and month lengths</h2>
        </div>
        <div className="endpoint-inline">
          <span className="method-badge is-get">GET</span>
          <code>/v3/api/enterprise/*</code>
        </div>
      </div>
      <form className="inline-run-form" onSubmit={onSubmit}>
        <label className="field-control">
          <span>BS year</span>
          <input
            type="number"
            min="1900"
            max="2200"
            value={year}
            onChange={(event) => setYear(event.target.value)}
            required
          />
        </label>
        <button className="run-button" type="submit" disabled={loading}>
          {loading ? <LoaderCircle className="is-spinning" aria-hidden="true" /> : <Play aria-hidden="true" />}
          Load year
        </button>
      </form>
      {error ? <p className="tool-error" role="alert">{error}</p> : null}
      <div className="fiscal-summary">
        <div>
          <small>Fiscal year</small>
          <strong>{fiscal?.fiscal_year || `${year}/${String(Number(year) + 1).slice(-2)}`}</strong>
        </div>
        <div>
          <small>Starts</small>
          <strong>{fiscal?.start?.bs || 'Pending'}</strong>
          <span>{formatAdDate(fiscal?.start?.ad)}</span>
        </div>
        <ArrowRight aria-hidden="true" />
        <div>
          <small>Ends</small>
          <strong>{fiscal?.end?.bs || 'Pending'}</strong>
          <span>{formatAdDate(fiscal?.end?.ad)}</span>
        </div>
      </div>
      <div className="month-length-chart" aria-label={`BS month lengths for ${year}`}>
        {(months?.months || []).map((month) => (
          <div key={month.month || month.name}>
            <span>{String(month.month).padStart(2, '0')}</span>
            <i aria-hidden="true"><b style={{ width: `${Math.max(18, (Number(month.days) - 27) * 18)}%` }} /></i>
            <strong>{month.days}d</strong>
          </div>
        ))}
        {!months?.months?.length ? (
          <div className="month-chart-placeholder">Run the year to inspect all 12 month lengths.</div>
        ) : null}
      </div>
      <div className="tool-actions">
        <Link to="/enterprise">Open business-rule overview <ArrowRight aria-hidden="true" /></Link>
        <a href={DEFAULT_PUBLIC_DOCS_URL}>View request schemas <ExternalLink aria-hidden="true" /></a>
      </div>
    </div>
  );
}

function FutureTool({ loading, error, capabilities, modelRisk, onRefresh }) {
  const status = capabilities?.status || capabilities?.maturity || 'research preview';
  const publicationStatus = capabilities?.publication_status || 'computed_prediction_not_official';
  const modelStatus = modelRisk?.status || modelRisk?.maturity || 'controlled capability';

  return (
    <div className="tool-panel future-tool">
      <div className="tool-heading">
        <div>
          <p className="tool-kicker">Controlled calendar research</p>
          <h2>Future BS model risk</h2>
        </div>
        <button className="icon-action" type="button" onClick={onRefresh} disabled={loading} aria-label="Refresh future BS capabilities">
          <Activity className={loading ? 'is-spinning' : ''} aria-hidden="true" />
        </button>
      </div>
      {error ? <p className="tool-error" role="alert">{error}</p> : null}
      <div className="future-boundary">
        <div className="future-status-mark" aria-hidden="true">
          <FlaskConical />
        </div>
        <div>
          <span className="research-state"><ShieldCheck aria-hidden="true" /> {readableCategory(status)}</span>
          <strong>{publicationStatus}</strong>
          <p>Future outputs are computational research. Review remains required before operational use.</p>
        </div>
      </div>
      <div className="capability-pair">
        <article>
          <span><Braces aria-hidden="true" /> V4</span>
          <strong>Future-BS capability</strong>
          <small>{readableCategory(status)}</small>
        </article>
        <article>
          <span><Building2 aria-hidden="true" /> V5</span>
          <strong>Calendar model risk</strong>
          <small>{readableCategory(modelStatus)}</small>
        </article>
      </div>
      <div className="tool-actions">
        <Link to="/future-bs">Review research boundary <ArrowRight aria-hidden="true" /></Link>
        <Link to="/methodology">Read the methodology</Link>
      </div>
    </div>
  );
}

function ApiInspector({ selected, activity, onCopy }) {
  const latest = activity[0];
  const current = selected || latest || endpointCatalog[0];
  const latestMatchesSelection = latest?.path === current.path;
  const status = latestMatchesSelection ? latest?.status || 'ready' : 'ready';
  const payload = latestMatchesSelection ? latest?.payload : null;
  const preview = payload ? safeJson(payload).slice(0, 1800) : '';

  return (
    <aside className="api-inspector" aria-label="API request inspector">
      <div className="inspector-heading">
        <div>
          <p className="tool-kicker">API inspector</p>
          <h2>Live request</h2>
        </div>
        <span className={`request-state is-${status}`}>
          <RequestStatusIcon status={status} />
          {requestStatusLabel(status)}
        </span>
      </div>
      <div className="request-line">
        <span className={`method-badge is-${methodClass(current.method)}`}>{current.method}</span>
        <code>{current.path}</code>
        <button type="button" onClick={() => onCopy(current.path)} aria-label="Copy endpoint path">
          <Copy aria-hidden="true" />
        </button>
      </div>
      <p className="request-description">
        {latest?.error || current.description || 'Select an endpoint to inspect it here.'}
      </p>
      <dl className="request-metrics">
        <div><dt>Status</dt><dd>{requestStatusLabel(status)}</dd></div>
        <div><dt>Duration</dt><dd>{latest?.durationMs != null ? `${latest.durationMs} ms` : '--'}</dd></div>
        <div><dt>Transport</dt><dd>JSON / HTTPS</dd></div>
      </dl>
      <div className="response-preview">
        <div>
          <span><FileJson2 aria-hidden="true" /> Response</span>
          <small>{preview ? 'JSON preview' : 'Waiting for request'}</small>
        </div>
        <pre>{preview || '{\n  "status": "ready"\n}'}</pre>
      </div>
      <div className="inspector-actions">
        <a href={DEFAULT_PUBLIC_DOCS_URL}>Open API docs <ExternalLink aria-hidden="true" /></a>
        <Link to="/trust">Trust controls</Link>
      </div>
      {activity.length > 1 ? (
        <div className="request-history">
          <p>Recent</p>
          <ul>
            {activity.slice(1, 4).map((item) => (
              <li key={item.id}>
                <RequestStatusIcon status={item.status} />
                <span>{item.title}</span>
                <small>{item.durationMs != null ? `${item.durationMs} ms` : requestStatusLabel(item.status)}</small>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </aside>
  );
}

function EndpointRowContent({ endpoint }) {
  const RowIcon = endpoint.docsOnly ? ExternalLink : ArrowRight;
  return (
    <>
      <span className={`method-badge is-${methodClass(endpoint.method)}`}>{endpoint.method}</span>
      <div>
        <strong>{endpoint.title}</strong>
        <code>{endpoint.path}</code>
      </div>
      <p>{endpoint.description}</p>
      <RowIcon aria-hidden="true" />
    </>
  );
}

const EndpointAtlas = memo(function EndpointAtlas({ selected, onSelect }) {
  const [query, setQuery] = useState('');
  const [group, setGroup] = useState('calendar');
  const filtered = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return endpointCatalog.filter((endpoint) => {
      const inGroup = normalizedQuery ? true : endpoint.group === group;
      const searchable = `${endpoint.method} ${endpoint.path} ${endpoint.title} ${endpoint.description}`.toLowerCase();
      return inGroup && (!normalizedQuery || searchable.includes(normalizedQuery));
    });
  }, [group, query]);

  return (
    <section className="endpoint-atlas" aria-labelledby="endpoint-atlas-title">
      <div className="atlas-heading">
        <div>
          <p className="tool-kicker">Developer API</p>
          <h2 id="endpoint-atlas-title">API explorer</h2>
          <p>25 public routes across seven groups.</p>
        </div>
        <a href={DEFAULT_PUBLIC_DOCS_URL}>Open Swagger <ExternalLink aria-hidden="true" /></a>
      </div>
      <div className="atlas-controls">
        <label className="atlas-search">
          <Search aria-hidden="true" />
          <span className="sr-only">Search endpoints</span>
          <input
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search endpoints"
          />
          <kbd>{filtered.length}</kbd>
        </label>
        <div className="atlas-groups" aria-label="Filter endpoint group">
          {endpointGroups.map((item) => (
            <button
              type="button"
              key={item.id}
              className={group === item.id ? 'is-active' : ''}
              onClick={() => setGroup(item.id)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>
      <div className="endpoint-list" aria-live="polite">
        {filtered.map((endpoint) => {
          const active = selected?.path === endpoint.path;
          let control;
          if (endpoint.tool) {
            control = (
              <button type="button" className="endpoint-select" onClick={() => onSelect(endpoint)}>
                <EndpointRowContent endpoint={endpoint} />
              </button>
            );
          } else if (endpoint.route) {
            control = (
              <Link className="endpoint-select" to={endpoint.route}>
                <EndpointRowContent endpoint={endpoint} />
              </Link>
            );
          } else {
            control = (
              <a className="endpoint-select" href={DEFAULT_PUBLIC_DOCS_URL}>
                <EndpointRowContent endpoint={endpoint} />
              </a>
            );
          }
          return (
            <article key={`${endpoint.method}-${endpoint.path}`} className={active ? 'is-selected' : ''}>
              {control}
            </article>
          );
        })}
        {!filtered.length ? (
          <div className="atlas-empty">
            <Search aria-hidden="true" />
            <strong>No endpoint matches that search.</strong>
            <button type="button" onClick={() => { setQuery(''); setGroup('calendar'); }}>Clear filters</button>
          </div>
        ) : null}
      </div>
    </section>
  );
});

function EndpointAtlasPlaceholder() {
  return (
    <section className="endpoint-atlas endpoint-atlas--loading" aria-busy="true">
      <div className="atlas-heading">
        <div>
          <p className="tool-kicker">Developer API</p>
          <h2>API explorer</h2>
          <p>Preparing the public route catalog.</p>
        </div>
      </div>
      <div className="atlas-loading-grid">
        {Array.from({ length: 5 }, (_, index) => <span key={index} />)}
      </div>
    </section>
  );
}

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
