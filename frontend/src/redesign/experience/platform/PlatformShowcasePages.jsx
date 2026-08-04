import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from '@parva/router';
import {
  ArrowRight,
  Braces,
  Building2,
  CalendarCheck2,
  CalendarRange,
  Check,
  CircleAlert,
  ClipboardCheck,
  Clock3,
  Code2,
  Copy,
  Database,
  ExternalLink,
  FileCheck2,
  FlaskConical,
  Gauge,
  GitCompareArrows,
  LoaderCircle,
  Play,
  ReceiptText,
  RefreshCw,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { calendarAPI, futureAPI } from '../../../services/api.js';
import { DEFAULT_PUBLIC_DOCS_URL } from '../../../config/publicEndpoints.js';
import { useParvaToast } from '../../motion/ParvaToastContext.js';
import {
  AppChrome,
  PageHero,
  apiHref,
  describeSupportError,
  readableCategory,
  todayIso,
} from '../ExperienceCommon.jsx';

const developerRoutes = [
  ['GET', '/v3/api/calendar/convert', 'AD to BS'],
  ['POST', '/v3/api/calendar/bs-to-gregorian', 'BS to AD'],
  ['GET', '/v3/api/enterprise/bs-months/{year}', 'Month lengths'],
  ['GET', '/v3/api/festivals/upcoming', 'Upcoming festivals'],
  ['GET', '/v3/api/calendar/panchanga', 'Panchanga'],
  ['GET', '/v4/api/future-bs/forecast/2084', 'Future BS forecast'],
];

const futurePipeline = [
  {
    icon: Database,
    step: '01',
    title: 'Published anchors',
    body: 'Known BS years establish year starts, month boundaries, and the validation baseline.',
  },
  {
    icon: Sparkles,
    step: '02',
    title: 'Solar ingress',
    body: 'The engine computes successive sidereal solar transitions in Nepal time.',
  },
  {
    icon: GitCompareArrows,
    step: '03',
    title: 'Candidate months',
    body: 'Boundary differences become candidate month lengths and complete year patterns.',
  },
  {
    icon: ShieldCheck,
    step: '04',
    title: 'Risk review',
    body: 'Backtests, boundary checks, and source conflicts determine the review label.',
  },
];

function absoluteUrl(path) {
  if (typeof window === 'undefined') return path;
  return new URL(path, window.location.origin).href;
}

function DeveloperConsole() {
  const initialDate = useMemo(() => todayIso('Asia/Kathmandu'), []);
  const [date, setDate] = useState(initialDate);
  const [payload, setPayload] = useState(null);
  const [status, setStatus] = useState({
    loading: true,
    error: '',
    code: null,
    elapsed: null,
  });
  const { notify } = useParvaToast();

  const requestPath = `/calendar/convert?date=${encodeURIComponent(date)}`;
  const publicPath = apiHref(requestPath);
  const curl = `curl "${absoluteUrl(publicPath)}"`;

  const runRequest = useCallback(async () => {
    setStatus({ loading: true, error: '', code: null, elapsed: null });
    const started = performance.now();
    try {
      const result = await calendarAPI.convertGregorian(date);
      setPayload(result);
      setStatus({
        loading: false,
        error: '',
        code: 200,
        elapsed: Math.max(1, Math.round(performance.now() - started)),
      });
    } catch (error) {
      setPayload(null);
      setStatus({
        loading: false,
        error: describeSupportError(error, 'The conversion request could not be completed.'),
        code: error?.status || null,
        elapsed: Math.max(1, Math.round(performance.now() - started)),
      });
    }
  }, [date]);

  useEffect(() => {
    let cancelled = false;
    const started = performance.now();
    calendarAPI.convertGregorian(initialDate)
      .then((result) => {
        if (cancelled) return;
        setPayload(result);
        setStatus({
          loading: false,
          error: '',
          code: 200,
          elapsed: Math.max(1, Math.round(performance.now() - started)),
        });
      })
      .catch((error) => {
        if (cancelled) return;
        setPayload(null);
        setStatus({
          loading: false,
          error: describeSupportError(error, 'The conversion request could not be completed.'),
          code: error?.status || null,
          elapsed: Math.max(1, Math.round(performance.now() - started)),
        });
      });
    return () => {
      cancelled = true;
    };
  }, [initialDate]);

  const copyCurl = async () => {
    await navigator.clipboard?.writeText(curl);
    notify('cURL command copied', {
      detail: 'Paste it into a terminal to replay the same request.',
    });
  };

  const responseText = payload
    ? JSON.stringify(payload, null, 2)
    : status.error
      ? JSON.stringify({ error: status.error, status: status.code || 'request_failed' }, null, 2)
      : '{\n  "status": "waiting"\n}';

  return (
    <section className="developer-console" aria-labelledby="live-api-title">
      <header className="developer-console__header">
        <div>
          <p className="eyebrow">Live API request</p>
          <h2 id="live-api-title">Run the same call your application would make.</h2>
        </div>
        <div className="developer-console__status" aria-live="polite">
          <span className={status.error ? 'is-error' : status.code ? 'is-ready' : ''} />
          {status.loading
            ? 'Requesting'
            : status.code
              ? `${status.code} in ${status.elapsed} ms`
              : 'Ready'}
        </div>
      </header>

      <form
        className="developer-request-form"
        onSubmit={(event) => {
          event.preventDefault();
          runRequest();
        }}
      >
        <span className="method-badge is-get">GET</span>
        <code>/v3/api/calendar/convert</code>
        <label>
          <span>Date</span>
          <input type="date" value={date} onChange={(event) => setDate(event.target.value)} required />
        </label>
        <button type="submit" className="primary-button" disabled={status.loading}>
          {status.loading ? <LoaderCircle className="is-spinning" aria-hidden="true" /> : <Play aria-hidden="true" />}
          {status.loading ? 'Running' : 'Run request'}
        </button>
      </form>

      <div className="developer-console__grid">
        <section className="developer-code-pane is-request">
          <header>
            <span>Request</span>
            <button type="button" onClick={copyCurl} aria-label="Copy cURL request">
              <Copy aria-hidden="true" />
              Copy
            </button>
          </header>
          <pre><code>{curl}</code></pre>
          <footer>
            <Clock3 aria-hidden="true" />
            <span>Runs against the configured Parva API base.</span>
          </footer>
        </section>
        <section className={`developer-code-pane is-response${status.error ? ' has-error' : ''}`}>
          <header>
            <span>JSON response</span>
            <strong>{status.code || '---'}</strong>
          </header>
          <pre aria-live="polite"><code>{responseText}</code></pre>
          <footer>
            {status.error ? <CircleAlert aria-hidden="true" /> : <Check aria-hidden="true" />}
            <span>{status.error ? 'The error is shown exactly as returned.' : 'Live data, source metadata, and claim state stay together.'}</span>
          </footer>
        </section>
      </div>
    </section>
  );
}

export function RedesignDevelopers() {
  return (
    <AppChrome>
      <main className="page-shell platform-showcase developer-showcase">
        <PageHero
          eyebrow="Developer API"
          title="Build with Nepal's calendar, not around it."
          body="Use one API for BS and AD conversion, published month lengths, Panchanga, festivals, and explicit source status."
          action={(
            <div className="public-cta-row">
              <a className="primary-button" href={DEFAULT_PUBLIC_DOCS_URL}>
                <Code2 aria-hidden="true" />
                Open API docs
              </a>
              <a className="ghost-button" href="https://github.com/dantwoashim/Project_Parva">
                GitHub
                <ExternalLink aria-hidden="true" />
              </a>
            </div>
          )}
        />

        <section className="platform-value-strip" aria-label="API qualities">
          <article>
            <Braces aria-hidden="true" />
            <div><span>Structured JSON</span><small>Consistent request and response shapes</small></div>
          </article>
          <article>
            <Database aria-hidden="true" />
            <div><span>Source status</span><small>Method and publication state in the response</small></div>
          </article>
          <article>
            <ShieldCheck aria-hidden="true" />
            <div><span>Visible limits</span><small>Uncertainty stays close to the result</small></div>
          </article>
          <article>
            <CalendarCheck2 aria-hidden="true" />
            <div><span>Calendar feeds</span><small>ICS output for supported observances</small></div>
          </article>
        </section>

        <DeveloperConsole />

        <section className="developer-route-map" aria-labelledby="route-map-title">
          <header>
            <div>
              <p className="eyebrow">Focused public surface</p>
              <h2 id="route-map-title">The routes worth demonstrating.</h2>
            </div>
            <Link to="/?tool=convert">Open full workbench <ArrowRight aria-hidden="true" /></Link>
          </header>
          <div>
            {developerRoutes.map(([method, path, label], index) => (
              <article key={path} style={{ '--route-index': index }}>
                <span className={`method-badge is-${method.toLowerCase()}`}>{method}</span>
                <div><strong>{label}</strong><code>{path}</code></div>
              </article>
            ))}
          </div>
        </section>
      </main>
    </AppChrome>
  );
}

function FutureCapabilityPanel() {
  const [payload, setPayload] = useState(null);
  const [status, setStatus] = useState({ loading: true, error: '' });

  const load = useCallback(async () => {
    setStatus({ loading: true, error: '' });
    try {
      const result = await futureAPI.getCapabilities();
      setPayload(result);
      setStatus({ loading: false, error: '' });
    } catch (error) {
      setPayload(null);
      setStatus({
        loading: false,
        error: describeSupportError(error, 'The Future BS capability contract could not be loaded.'),
      });
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    futureAPI.getCapabilities()
      .then((result) => {
        if (cancelled) return;
        setPayload(result);
        setStatus({ loading: false, error: '' });
      })
      .catch((error) => {
        if (cancelled) return;
        setPayload(null);
        setStatus({
          loading: false,
          error: describeSupportError(error, 'The Future BS capability contract could not be loaded.'),
        });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const publicSurface = payload?.public_surface || [];
  const publicationStatus = payload?.publication_status || 'computed_prediction_not_official';

  return (
    <section className="future-contract" aria-labelledby="future-contract-title">
      <header>
        <div>
          <p className="eyebrow">Live capability contract</p>
          <h2 id="future-contract-title">What the public engine promises today.</h2>
        </div>
        <button type="button" className="icon-action" onClick={load} disabled={status.loading} aria-label="Refresh Future BS capability">
          <RefreshCw className={status.loading ? 'is-spinning' : ''} aria-hidden="true" />
        </button>
      </header>

      {status.error ? <p className="tool-error" role="alert">{status.error}</p> : null}
      <div className="future-contract__status">
        <div className="future-contract__mark"><FlaskConical aria-hidden="true" /></div>
        <div>
          <span>{status.loading ? 'Loading live contract' : readableCategory(payload?.maturity || 'Research preview')}</span>
          <strong>{publicationStatus}</strong>
          <p>Every computed future result keeps this publication label attached.</p>
        </div>
      </div>
      <dl className="future-contract__facts">
        <div><dt>Review</dt><dd>{payload?.review_required === false ? 'Optional' : 'Required'}</dd></div>
        <div><dt>Release</dt><dd>{payload?.release_id || 'Loading'}</dd></div>
        <div><dt>Claim boundary</dt><dd>{readableCategory(payload?.claim_boundary || 'Loading')}</dd></div>
      </dl>
      <div className="future-contract__surface">
        <span>Public surface</span>
        <div>
          {(publicSurface.length ? publicSurface : ['methodology_summary', 'claim_boundary', 'risk_label_taxonomy'])
            .map((item) => <em key={item}>{readableCategory(item)}</em>)}
        </div>
      </div>
      <footer>
        <code>GET /v4/api/future-bs/capabilities</code>
        <a href={apiHref('/v4/api/future-bs/capabilities')}>Open JSON <ExternalLink aria-hidden="true" /></a>
      </footer>
    </section>
  );
}

function FutureForecastPanel() {
  const [year, setYear] = useState('2084');
  const [payload, setPayload] = useState(null);
  const [selectedMonth, setSelectedMonth] = useState(1);
  const [status, setStatus] = useState({ loading: true, error: '' });

  const loadForecast = useCallback(async (requestedYear) => {
    const parsedYear = Number(requestedYear);
    if (!Number.isInteger(parsedYear) || parsedYear < 2084 || parsedYear > 2200) {
      setStatus({ loading: false, error: 'Choose a BS year from 2084 through 2200.' });
      return;
    }

    setStatus({ loading: true, error: '' });
    try {
      const result = await futureAPI.getForecast(parsedYear);
      setPayload(result);
      setSelectedMonth(1);
      setYear(String(parsedYear));
      setStatus({ loading: false, error: '' });
    } catch (error) {
      setStatus({
        loading: false,
        error: describeSupportError(error, 'The forecast snapshot could not be loaded.'),
      });
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    futureAPI.getForecast(2084)
      .then((result) => {
        if (cancelled) return;
        setPayload(result);
        setStatus({ loading: false, error: '' });
      })
      .catch((error) => {
        if (cancelled) return;
        setStatus({
          loading: false,
          error: describeSupportError(error, 'The forecast snapshot could not be loaded.'),
        });
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const activeMonth = payload?.months?.find((month) => month.month === selectedMonth) || null;
  const replay = payload?.validation?.official_window_replay;
  const confidencePercent = Math.round((payload?.heuristic_confidence_score || 0) * 100);

  const submit = (event) => {
    event.preventDefault();
    loadForecast(year);
  };

  return (
    <section className="future-forecast" aria-labelledby="future-forecast-title">
      <header>
        <div>
          <p className="eyebrow">Public research snapshot</p>
          <h2 id="future-forecast-title">Explore the selected solar-civil forecast.</h2>
        </div>
        <form onSubmit={submit} className="future-year-control">
          <label htmlFor="future-bs-year">BS year</label>
          <input
            id="future-bs-year"
            type="number"
            min="2084"
            max="2200"
            value={year}
            onChange={(event) => setYear(event.target.value)}
          />
          <button type="submit" className="primary-button" disabled={status.loading}>
            {status.loading ? <LoaderCircle className="is-spinning" aria-hidden="true" /> : <Play aria-hidden="true" />}
            Run
          </button>
        </form>
      </header>

      {status.error ? <p className="tool-error" role="alert">{status.error}</p> : null}

      <div className="future-forecast__summary" aria-live="polite">
        <div><span>Forecast year</span><strong>{payload?.bs_year || '...'}</strong></div>
        <div><span>Year length</span><strong>{payload ? `${payload.year_total_days} days` : '...'}</strong></div>
        <div><span>Heuristic score</span><strong>{payload ? `${confidencePercent}%` : '...'}</strong></div>
        <div>
          <span>Calibrated replay</span>
          <strong>{replay ? `${replay.exact_month_matches}/${replay.month_cases}` : '...'}</strong>
        </div>
      </div>

      <div className="future-month-grid" aria-label={`Month-length forecast for ${payload?.bs_year || year} BS`}>
        {(payload?.months || []).map((month) => (
          <button
            key={month.month}
            type="button"
            className={month.month === selectedMonth ? 'is-selected' : ''}
            data-risk={month.risk_label.toLowerCase()}
            onClick={() => setSelectedMonth(month.month)}
            aria-pressed={month.month === selectedMonth}
          >
            <span>{month.month_name}</span>
            <strong>{month.predicted_days}</strong>
            <small>{month.risk_label}</small>
          </button>
        ))}
      </div>

      <div className="future-forecast__detail">
        <div className="future-forecast__detail-mark"><CalendarRange aria-hidden="true" /></div>
        <div>
          <span>Selected month</span>
          <strong>{activeMonth ? `${activeMonth.month_name}: ${activeMonth.predicted_days} days` : 'Loading month data'}</strong>
          <p>{activeMonth ? `Model agreement ${activeMonth.model_agreement}; 95% prediction set ${activeMonth.prediction_set_95.join(' or ')} days.` : 'The month-level evidence will appear here.'}</p>
        </div>
        <dl>
          <div><dt>Boundary distance</dt><dd>{activeMonth?.boundary_distance_minutes ?? '...'} min</dd></div>
          <div><dt>Review state</dt><dd>{activeMonth?.risk_label || '...'}</dd></div>
        </dl>
      </div>

      <footer>
        <div>
          <strong>Computed research</strong>
          <span>Calibration fit only; independent broad validation remains pending.</span>
        </div>
        <a href={apiHref(`/v4/api/future-bs/forecast/${payload?.bs_year || 2084}`)}>
          Open forecast JSON <ExternalLink aria-hidden="true" />
        </a>
      </footer>
    </section>
  );
}

export function RedesignFutureBsResearch() {
  return (
    <AppChrome>
      <main className="page-shell platform-showcase future-showcase">
        <PageHero
          eyebrow="Future BS engine"
          title="Future dates need a risk label."
          body="Parva separates published calendar data from computed month-length research, then keeps review state attached to every future result."
          action={(
            <div className="public-cta-row">
              <Link className="primary-button" to="/?tool=future">
                <FlaskConical aria-hidden="true" />
                Inspect capability
              </Link>
              <Link className="ghost-button" to="/methodology">Read the method</Link>
            </div>
          )}
        />

        <section className="future-state-strip" aria-label="Future BS claim state">
          <article className="is-published">
            <FileCheck2 aria-hidden="true" />
            <span>Published years</span>
            <strong>Source-backed</strong>
          </article>
          <ArrowRight aria-hidden="true" />
          <article className="is-computed">
            <FlaskConical aria-hidden="true" />
            <span>Future years</span>
            <strong>Computed</strong>
          </article>
          <ArrowRight aria-hidden="true" />
          <article className="is-reviewed">
            <ClipboardCheck aria-hidden="true" />
            <span>Operational use</span>
            <strong>Human review</strong>
          </article>
        </section>

        <FutureForecastPanel />

        <section className="future-workspace">
          <div className="future-pipeline">
            <header>
              <p className="eyebrow">Calculation path</p>
              <h2>From known boundaries to a reviewable candidate.</h2>
            </header>
            <ol>
              {futurePipeline.map((item) => {
                const PipelineIcon = item.icon;
                return (
                  <li key={item.step}>
                    <span>{item.step}</span>
                    <i><PipelineIcon aria-hidden="true" /></i>
                    <div><strong>{item.title}</strong><p>{item.body}</p></div>
                  </li>
                );
              })}
            </ol>
          </div>
          <FutureCapabilityPanel />
        </section>

        <section className="risk-taxonomy" aria-labelledby="risk-title">
          <header>
            <p className="eyebrow">Review language</p>
            <h2 id="risk-title">One result, three clear decisions.</h2>
          </header>
          <div>
            <article className="is-green">
              <span>Green</span>
              <strong>Stable candidate</strong>
              <p>Backtests and boundary checks agree. The result still remains computed research.</p>
            </article>
            <article className="is-amber">
              <span>Amber</span>
              <strong>Review before use</strong>
              <p>A boundary or source difference can move the result. Inspect the evidence.</p>
            </article>
            <article className="is-red">
              <span>Red</span>
              <strong>Hold the decision</strong>
              <p>The candidate carries conflict or weak support and should stay out of schedules.</p>
            </article>
          </div>
        </section>
      </main>
    </AppChrome>
  );
}

const enterpriseCases = [
  {
    icon: ReceiptText,
    title: 'Fiscal reports',
    body: 'Resolve BS fiscal boundaries and published month lengths before generating periods.',
  },
  {
    icon: Building2,
    title: 'Payroll and renewals',
    body: 'Check date conversion and working-day movement before a schedule becomes final.',
  },
  {
    icon: FileCheck2,
    title: 'Record migration',
    body: 'Compare stored BS and AD values and isolate rows that need review.',
  },
  {
    icon: Gauge,
    title: 'Release checks',
    body: 'Run known boundaries and source policy as part of deployment validation.',
  },
];

export function RedesignEnterprise() {
  return (
    <AppChrome>
      <main className="page-shell platform-showcase enterprise-showcase">
        <PageHero
          eyebrow="Operational calendar checks"
          title="Catch date errors before they reach reports and schedules."
          body="Use Parva as a validation layer for BS conversion, fiscal boundaries, working days, and source-aware review."
          action={(
            <div className="public-cta-row">
              <Link className="primary-button" to="/?tool=fiscal">Open fiscal tools</Link>
              <a className="ghost-button" href={DEFAULT_PUBLIC_DOCS_URL}>Review API schemas</a>
            </div>
          )}
        />

        <section className="enterprise-flow" aria-label="Enterprise validation flow">
          {[
            ['01', 'Submit', 'Existing BS and AD dates'],
            ['02', 'Compare', 'Canonical conversion and rules'],
            ['03', 'Review', 'Differences and source status'],
            ['04', 'Apply', 'Approved corrections only'],
          ].map(([step, title, body], index) => (
            <article key={step}>
              <span>{step}</span>
              <div><strong>{title}</strong><p>{body}</p></div>
              {index < 3 ? <ArrowRight aria-hidden="true" /> : null}
            </article>
          ))}
        </section>

        <section className="enterprise-case-grid">
          {enterpriseCases.map((item, index) => {
            const CaseIcon = item.icon;
            return (
              <article key={item.title} style={{ '--case-index': index }}>
                <i><CaseIcon aria-hidden="true" /></i>
                <div><h2>{item.title}</h2><p>{item.body}</p></div>
              </article>
            );
          })}
        </section>

        <section className="enterprise-boundary">
          <div>
            <p className="eyebrow">Approval boundary</p>
            <h2>Parva finds the difference. Your policy decides the change.</h2>
          </div>
          <p>Each workflow keeps the input, calculated result, source state, and review decision together so a correction has a clear audit trail.</p>
        </section>
      </main>
    </AppChrome>
  );
}
