import {
  useEffect,
  useState,
  Link,
  feedAPI,
  policyAPI,
  reliabilityAPI,
  apiHref,
  describeSupportError,
  formatDateTime,
  humanMethodLabel,
  readableCategory,
  AppChrome,
  PageHero,
} from './ExperienceCommon.jsx';
import benchmarkSummary from '../../data/benchmarkSummary.json';
import {
  TrustLimitsStrip,
  TrustLoading,
  TrustMetricCard,
  TrustPageFrame,
} from './TrustPageParts.jsx';
import { DEFAULT_PUBLIC_DOCS_URL } from '../../config/publicEndpoints.js';
import { formatBytes, formatPercent, trustValue } from './trustPageUtils.js';
import {
  ArrowUpRight,
  CalendarCheck,
  CalendarSync,
  Check,
  Clipboard,
  Globe2,
  RefreshCw,
} from 'lucide-react';

export function RedesignIntegrations() {
  const [payload, setPayload] = useState(null);
  const [status, setStatus] = useState({ loading: true, error: '' });
  const [copiedFeed, setCopiedFeed] = useState('');

  useEffect(() => {
    let cancelled = false;
    feedAPI.getCatalog({ years: 2, lang: 'en' })
      .then((data) => {
        if (!cancelled) {
          setPayload(data);
          setStatus({ loading: false, error: '' });
        }
      })
      .catch((error) => {
        if (!cancelled) {
          setPayload(null);
          setStatus({ loading: false, error: describeSupportError(error, 'Integration catalog could not be loaded.') });
        }
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const presetCards = payload?.presets || [];
  const platformCards = Object.entries(payload?.platforms || {});

  const copyFeed = async (item) => {
    const url = item.feed_url?.startsWith('http') ? item.feed_url : `${window.location.origin}${item.feed_url}`;
    try {
      await navigator.clipboard?.writeText(url);
      setCopiedFeed(item.key || item.title);
      window.setTimeout(() => setCopiedFeed(''), 1800);
    } catch {
      if (typeof window.prompt === 'function') window.prompt('Copy calendar feed URL', url);
    }
  };

  return (
    <AppChrome>
      <main className="page-shell integrations-page">
        <PageHero
          title="Integrations"
          body="Choose a maintained festival feed, subscribe from your calendar app, or copy the direct URL for another service."
          action={<a className="ghost-button" href={apiHref('/feeds/integrations/catalog')}>Open catalog <ArrowUpRight aria-hidden="true" /></a>}
        />
        {status.loading ? <article className="panel"><h2>Loading integrations</h2><p>Fetching feed catalog from the backend.</p></article> : null}
        {status.error ? <article className="panel"><h2>Integrations unavailable</h2><p>{status.error}</p></article> : null}

        {!status.loading && !status.error ? (
          <>
            <section className="integration-intro-strip" aria-label="Calendar feed process">
              <div><CalendarCheck aria-hidden="true" /><span>Choose</span><strong>Pick a focused feed</strong></div>
              <div><CalendarSync aria-hidden="true" /><span>Connect</span><strong>Subscribe or copy URL</strong></div>
              <div><RefreshCw aria-hidden="true" /><span>Refresh</span><strong>Your calendar stays updated</strong></div>
            </section>

            <section className="integration-feed-section">
              <header>
                <div><p className="eyebrow">Calendar feeds</p><h2>Start with a preset</h2></div>
                <p>Each feed is ready to subscribe and can also be used as a direct ICS source.</p>
              </header>
              <div className="integration-feed-grid">
                {presetCards.map((item, index) => (
                  <article className={`integration-card tone-${(index % 3) + 1}`} key={item.key || item.title}>
                    <div className="integration-card__icon"><CalendarSync aria-hidden="true" /></div>
                    <p className="eyebrow">Feed preset {String(index + 1).padStart(2, '0')}</p>
                    <h3>{item.title}</h3>
                    <p>{item.description}</p>
                    <div className="integration-actions">
                      <a className="primary-button" href={item.feed_url}>Subscribe <ArrowUpRight aria-hidden="true" /></a>
                      <button type="button" className="ghost-button" onClick={() => copyFeed(item)}>
                        {copiedFeed === (item.key || item.title) ? <><Check aria-hidden="true" /> Copied</> : <><Clipboard aria-hidden="true" /> Copy URL</>}
                      </button>
                    </div>
                  </article>
                ))}
              </div>
            </section>

            <section className="integration-platform-section">
              <header>
                <div><p className="eyebrow">Calendar apps</p><h2>Use the feed where you already plan</h2></div>
                <Globe2 aria-hidden="true" />
              </header>
              <div className="integration-platform-grid">
                {platformCards.map(([key, item], index) => (
                  <article key={key}>
                    <span>{String(index + 1).padStart(2, '0')}</span>
                    <div>
                      <h3>{item.title}</h3>
                      <p>{item.recommended_action}</p>
                      <small>{item.sync_expectation}</small>
                    </div>
                  </article>
                ))}
              </div>
            </section>
          </>
        ) : null}
      </main>
    </AppChrome>
  );
}

const trustResourceConfig = {
  runtime: {
    request: () => reliabilityAPI.getStatus(),
    read: (value) => ({ runtime: value?.runtime || null, policy: value?.policy || null }),
  },
  policy: {
    request: () => policyAPI.get(),
    read: (value) => ({ policy: value?.policy || null }),
  },
  benchmark: {
    request: () => reliabilityAPI.getBenchmarkManifest(),
    read: (value) => ({ benchmark: value?.benchmark || null }),
  },
  queue: {
    request: () => reliabilityAPI.getSourceReviewQueue(),
    read: (value) => ({ queue: value?.queue || null }),
  },
  boundary: {
    request: () => reliabilityAPI.getBoundarySuite(),
    read: (value) => ({ boundary: value?.boundary_suite || null }),
  },
  differential: {
    request: () => reliabilityAPI.getDifferentialManifest(),
    read: (value) => ({ differential: value?.differential || null }),
  },
  slo: {
    request: () => reliabilityAPI.getSlos(),
    read: (value) => ({ slo: value?.slo || null }),
  },
  playbooks: {
    request: () => reliabilityAPI.getPlaybooks(),
    read: (value) => ({ playbooks: value?.playbooks || [] }),
  },
};

const inFlightTrustResources = new Map();

function loadTrustResource(name) {
  if (inFlightTrustResources.has(name)) return inFlightTrustResources.get(name);
  const config = trustResourceConfig[name];
  const request = Promise.resolve()
    .then(() => config.request())
    .finally(() => inFlightTrustResources.delete(name));
  inFlightTrustResources.set(name, request);
  return request;
}

function useTrustSurface(resources = ['runtime', 'policy']) {
  const [payload, setPayload] = useState({
    runtime: null,
    policy: null,
    benchmark: null,
    queue: null,
    boundary: null,
    differential: null,
    slo: null,
    playbooks: [],
  });
  const [status, setStatus] = useState({ loading: true, error: '' });
  const resourceKey = [...new Set(resources)].sort().join(',');

  useEffect(() => {
    let cancelled = false;
    const names = resourceKey.split(',').filter(Boolean);
    Promise.allSettled(names.map(loadTrustResource)).then((results) => {
      if (cancelled) return;
      const nextPayload = {
        runtime: null,
        policy: null,
        benchmark: null,
        queue: null,
        boundary: null,
        differential: null,
        slo: null,
        playbooks: [],
      };
      results.forEach((result, index) => {
        if (result.status !== 'fulfilled') return;
        Object.assign(nextPayload, trustResourceConfig[names[index]].read(result.value));
      });
      const rejected = results.filter((item) => item.status === 'rejected');
      setPayload(nextPayload);
      setStatus({
        loading: false,
        error: rejected.length === results.length && rejected.length
          ? describeSupportError(rejected[0].reason, 'Trust data could not be loaded from the backend.')
          : '',
      });
    });
    return () => {
      cancelled = true;
    };
  }, [resourceKey]);

  return { ...payload, loading: status.loading, error: status.error };
}

export function RedesignTrust() {
  const trust = useTrustSurface(['runtime', 'policy', 'queue']);
  const runtime = trust.runtime || {};
  const ephemeris = runtime.ephemeris || {};
  const queue = trust.queue || {};
  const policy = trust.policy || {};
  const endpoints = runtime.metrics?.endpoints || [];

  return (
    <TrustPageFrame
      current="trust"
      eyebrow="Trust Center"
      title="See what the engine knows."
      body="Runtime status, policy, source review, calculation method, and public verification stay visible in one place."
      action={<Link className="primary-button" to="/truth-lab">Inspect live evidence</Link>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <TrustLimitsStrip runtime={runtime} policy={policy} />
      <section className="trust-feature-band" aria-label="Public verification status">
        <div>
          <p className="eyebrow">Public verification status, not live uptime SLA</p>
          <h2>{formatPercent(benchmarkSummary.parva_score_percent)} benchmark score across {benchmarkSummary.task_count} public-safe tasks.</h2>
        </div>
        <p>
          Public review should start with the benchmark, public verification workflow,
          API docs, and known limitations. Parva is source-aware decision support and
          not government, calendar, legal, tax, banking, payroll, religious, or
          future-date authority.
        </p>
      </section>
      <section className="trust-hero-grid">
        <TrustMetricCard
          eyebrow="Benchmark"
          title="Reliability score"
          value={formatPercent(benchmarkSummary.parva_score_percent)}
          detail={`${formatPercent(benchmarkSummary.score_gap_percent)} gap over the static baseline; ${benchmarkSummary.review_gate_performance?.passed || 0}/${benchmarkSummary.review_gate_performance?.tasks || 0} review-gate tasks passed.`}
          actionTo="/benchmark"
          actionLabel="Open benchmark"
        />
        <TrustMetricCard
          eyebrow="Runtime"
          title="Service state"
          value={readableCategory(runtime.status || 'Unavailable')}
          detail={`${endpoints.length} API surfaces have runtime metrics in the reliability feed.`}
          actionTo="/truth-lab"
          actionLabel="Open Truth Lab"
        />
      <TrustMetricCard
          eyebrow="Ephemeris"
          title="Calculation engine"
          value={humanMethodLabel(ephemeris.mode, 'Unavailable')}
          detail={`${trustValue(ephemeris.ayanamsa)} ayanamsa, ${trustValue(ephemeris.coordinate_system)} coordinates.`}
          actionTo="/methodology"
          actionLabel="Read methodology"
        />
        <TrustMetricCard
          eyebrow="Policy"
          title="Usage posture"
          value={readableCategory(policy.usage || 'Unavailable')}
          detail={trustValue(policy.advisory)}
          actionTo="/policy"
          actionLabel="Open policy"
        />
        <TrustMetricCard
          eyebrow="Source review"
          title="Promotion queue"
          value={trustValue(queue.total_items)}
          detail={`${trustValue(queue.summary?.ready_for_promotion, '0')} sources ready for review, ${trustValue(queue.summary?.high, '0')} high priority.`}
          actionTo="/truth-lab"
          actionLabel="Review sources"
        />
      </section>
      <section className="trust-feature-band">
        <div>
          <p className="eyebrow">What this means</p>
          <h2>Confidence belongs beside its limits.</h2>
        </div>
        <p>
          Ritual dates and time windows can vary by authority, location, and boundary conditions. The app keeps those constraints visible instead of burying them behind decorative confidence language.
        </p>
      </section>
      <section className="trust-link-grid">
        {[
          ['Methodology', 'How date, place, source, and risk state become a result.', '/methodology'],
          ['Truth Lab', 'Live reliability status, benchmark manifests, source review queues, and boundary suites.', '/truth-lab'],
          ['API Policy', 'The exact advisory policy returned by the backend for consumers and integrators.', '/policy'],
          ['API Docs', 'Public OpenAPI docs for stable route inspection.', DEFAULT_PUBLIC_DOCS_URL],
          ['Verification reports', 'Reviewer packet and public verification evidence in the source repo.', 'https://github.com/dantwoashim/Project_Parva/tree/main/reports/external_reviewer_packet'],
          ['Known limitations', 'Supported ranges, authority boundaries, and unavailable external dependencies.', 'https://github.com/dantwoashim/Project_Parva/blob/main/docs/KNOWN_LIMITATIONS.md'],
          ['About', 'What Parva is, what it is not, and how to use it responsibly.', '/about'],
        ].map(([title, body, to]) => (
          String(to).startsWith('http') ? (
            <a key={title} href={to}>
              <span>{title}</span>
              <p>{body}</p>
            </a>
          ) : (
            <Link key={title} to={to}>
              <span>{title}</span>
              <p>{body}</p>
            </Link>
          )
        ))}
      </section>
    </TrustPageFrame>
  );
}

export function RedesignMethodology() {
  const trust = useTrustSurface(['runtime', 'boundary', 'benchmark']);
  const runtime = trust.runtime || {};
  const ephemeris = runtime.ephemeris || {};
  const cache = runtime.cache || {};
  const boundary = trust.boundary || {};
  const benchmark = trust.benchmark || {};
  const steps = [
    ['Set the context', 'The date, timezone, latitude, longitude, and requested tool are prepared for one clear calculation.'],
    ['Run the calculation', `${humanMethodLabel(ephemeris.library, 'The configured ephemeris')} powers the current sidereal calculation path when the backend is healthy.`],
    ['Check the result', 'Festival and timing outputs are checked against support level, source type, quality, and boundary risk.'],
    ['Show the source', 'Policy, request ID, source status, cache state, and benchmark signals stay close to the result.'],
  ];

  return (
    <TrustPageFrame
      current="methodology"
      eyebrow="Methodology"
      title="How Parva calculates a result."
      body="Each calculation starts with clear inputs, follows a named method, and returns its source confidence and limits."
      action={<Link className="ghost-button" to="/truth-lab">See live checks</Link>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="methodology-steps">
        {steps.map(([title, body], index) => (
          <article key={title}>
            <span>{String(index + 1).padStart(2, '0')}</span>
            <h2>{title}</h2>
            <p>{body}</p>
          </article>
        ))}
      </section>
      <section className="trust-evidence-grid">
        <article>
          <p className="eyebrow">Engine path</p>
          <h2>{humanMethodLabel(ephemeris.mode, 'Unavailable')}</h2>
          <dl>
            <div><dt>Ayanamsa</dt><dd>{trustValue(ephemeris.ayanamsa)}</dd></div>
            <div><dt>Accuracy</dt><dd>{trustValue(ephemeris.accuracy)}</dd></div>
            <div><dt>Library</dt><dd>{humanMethodLabel(ephemeris.library, 'Unavailable')}</dd></div>
          </dl>
        </article>
        <article>
          <p className="eyebrow">Cache and benchmark</p>
          <h2>{trustValue(cache.file_count)} artifacts</h2>
          <dl>
            <div><dt>Cache bytes</dt><dd>{formatBytes(cache.total_bytes)}</dd></div>
            <div><dt>Boundary samples</dt><dd>{trustValue(boundary.total_samples || benchmark.total_samples)}</dd></div>
            <div><dt>Manifest</dt><dd>{trustValue(benchmark.manifest_id || benchmark.version)}</dd></div>
          </dl>
        </article>
      </section>
    </TrustPageFrame>
  );
}

export function RedesignTruthLab() {
  const trust = useTrustSurface(['runtime', 'benchmark', 'boundary', 'differential', 'queue']);
  const runtime = trust.runtime || {};
  const cache = runtime.cache || {};
  const benchmark = trust.benchmark || {};
  const boundary = trust.boundary || {};
  const differential = trust.differential || {};
  const queue = trust.queue || {};
  const endpoints = runtime.metrics?.endpoints || [];
  const endpointCards = endpoints.slice(0, 6);

  return (
    <TrustPageFrame
      current="truth"
      eyebrow="Truth Lab"
      title="Live checks from the backend."
      body="See reliability status, benchmark files, source review queues, and endpoint health in one place."
      action={<a className="ghost-button" href={apiHref('/reliability/status')}>Open JSON</a>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="truth-dashboard">
        <TrustMetricCard eyebrow="Runtime" title="Status" value={readableCategory(runtime.status)} detail={`${trustValue(runtime.warnings?.length, '0')} warnings reported.`} />
        <TrustMetricCard
          eyebrow="Cache"
          title="Artifacts"
          value={trustValue(cache.file_count)}
          detail={Number(cache.file_count) > 0 ? `${formatBytes(cache.total_bytes)} available for precomputed surfaces.` : 'No precomputed cache artifacts are published.'}
        />
        <TrustMetricCard
          eyebrow="Benchmark"
          title="Manifest"
          value={trustValue(benchmark.manifest_id || benchmark.version || (boundary.total_samples ? `${boundary.total_samples} samples` : null))}
          detail={`${trustValue(boundary.total_samples || benchmark.total_samples)} boundary or benchmark samples exposed.`}
        />
        <TrustMetricCard eyebrow="Sources" title="Review queue" value={trustValue(queue.total_items)} detail={`${trustValue(queue.summary?.ready_for_promotion, '0')} ready for promotion.`} />
      </section>
      <section className="truth-table-panel">
        <div className="panel-heading tight">
          <p className="eyebrow">Endpoint health</p>
          <strong>{endpointCards.length} surfaces</strong>
        </div>
        <div className="truth-endpoint-list">
          {endpointCards.map((item) => (
            <article key={item.path}>
              <span>{item.path}</span>
              <strong>{trustValue(item.p95_latency_ms)} ms</strong>
              <em>{trustValue(item.requests, '0')} requests · {trustValue(item.errors, '0')} errors</em>
            </article>
          ))}
          {!endpointCards.length ? <p className="festival-muted-note">No endpoint metrics were returned by the reliability API.</p> : null}
        </div>
      </section>
      <section className="trust-evidence-grid">
        <article>
          <p className="eyebrow">Boundary suite</p>
          <h2>{boundary.status ? readableCategory(boundary.status) : boundary.generated_at ? formatDateTime(boundary.generated_at) : 'Unavailable'}</h2>
          <p>{trustValue(boundary.summary || 'Boundary results are exposed when the backend publishes this suite.')}</p>
        </article>
        <article>
          <p className="eyebrow">Differential manifest</p>
          <h2>{trustValue(differential.manifest_id || differential.version)}</h2>
          <p>{trustValue(differential.summary || 'Differential checks are loaded from the reliability manifest when available.')}</p>
        </article>
      </section>
    </TrustPageFrame>
  );
}

export function RedesignAbout() {
  const trust = useTrustSurface(['runtime', 'policy']);
  const policy = trust.policy || {};
  const runtime = trust.runtime || {};

  return (
    <TrustPageFrame
      current="about"
      eyebrow="About Parva"
      title="Nepali dates and daily timing in one system."
      body="Parva brings daily panchanga, festivals, muhurta windows, place context, and birth-reading tools into one public interface."
      action={<Link className="primary-button" to="/today">Open today</Link>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="about-statement">
        <div>
          <p className="eyebrow">Product stance</p>
          <h2>Daily tools with visible calculation limits.</h2>
        </div>
        <p>
          The app is intentionally advisory. It can compute, compare, and explain, but it should not replace trusted local authorities for ritual-critical decisions.
        </p>
      </section>
      <section className="trust-link-grid">
        {[
          ['Daily time', 'Today, panchanga signals, sunlight, and current timing windows.', '/today'],
          ['Festival calendar', 'A backend-backed list with computed, provisional, and inventory source states.', '/festivals'],
          ['Best time', 'Muhurta windows with score, class, and reason codes from the API.', '/best-time'],
          ['Birth reading', 'Kundali and graph surfaces tied to explicit place and time inputs.', '/birth-reading'],
        ].map(([title, body, to]) => (
          <Link key={title} to={to}>
            <span>{title}</span>
            <p>{body}</p>
          </Link>
        ))}
      </section>
      <section className="trust-evidence-grid">
        <article>
          <p className="eyebrow">Backend</p>
          <h2>{readableCategory(runtime.status || 'Unavailable')}</h2>
          <p>{trustValue(runtime.ephemeris?.notes, 'Runtime notes are loaded from the reliability endpoint.')}</p>
        </article>
        <article>
          <p className="eyebrow">Policy</p>
          <h2>Version {trustValue(policy.version)}</h2>
          <p>{trustValue(policy.advisory)}</p>
        </article>
      </section>
    </TrustPageFrame>
  );
}

export function RedesignApiPolicy() {
  const trust = useTrustSurface(['policy', 'playbooks']);
  const policy = trust.policy || {};
  const playbooks = trust.playbooks || [];

  return (
    <TrustPageFrame
      current="policy"
      eyebrow="API Policy"
      title="Know the API rules before you build."
      body="This page reads the live backend policy and shows the usage rules, advisory limits, and recovery steps."
      action={<a className="primary-button" href={apiHref('/policy')}>Open policy JSON</a>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="policy-contract">
        <article>
          <span>Usage</span>
          <strong>{readableCategory(policy.usage || 'Unavailable')}</strong>
          <p>Returned by `/v3/api/policy` for API consumers.</p>
        </article>
        <article>
          <span>Version</span>
          <strong>{trustValue(policy.version)}</strong>
          <p>Policy metadata version from the backend.</p>
        </article>
        <article>
          <span>Advisory</span>
          <strong>{policy.advisory ? 'Active' : 'Unavailable'}</strong>
          <p>{trustValue(policy.advisory)}</p>
        </article>
      </section>
      <section className="truth-table-panel">
        <div className="panel-heading tight">
          <p className="eyebrow">Reliability playbooks</p>
          <strong>{playbooks.length} backend playbooks</strong>
        </div>
        <div className="truth-endpoint-list">
          {playbooks.map((item) => (
            <article key={item.id}>
              <span>{readableCategory(item.id)}</span>
              <strong>{item.doc}</strong>
              <em>{item.summary}</em>
            </article>
          ))}
          {!playbooks.length ? <p className="festival-muted-note">No playbooks were returned by the reliability API.</p> : null}
        </div>
      </section>
    </TrustPageFrame>
  );
}

