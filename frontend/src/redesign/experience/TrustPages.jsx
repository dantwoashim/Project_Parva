import {
  useEffect,
  useState,
  Link,
  feedAPI,
  policyAPI,
  reliabilityAPI,
  apiHref,
  describeSupportError,
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
      <main className="page-shell simple-grid">
        <PageHero title="Integrations" body="Subscribe to verified festival calendars, copy feed URLs, or connect Parva data to the calendar app you already use." />
        {status.loading ? <article className="panel"><h2>Loading integrations</h2><p>Fetching feed catalog from the backend.</p></article> : null}
        {status.error ? <article className="panel"><h2>Integrations unavailable</h2><p>{status.error}</p></article> : null}
        {presetCards.map((item) => (
          <article className="panel integration-card" key={item.key || item.title}>
            <p className="eyebrow">Feed preset</p>
            <h2>{item.title}</h2>
            <p>{item.description}</p>
            <div className="integration-actions">
              <a className="primary-button" href={item.feed_url}>Subscribe</a>
              <button type="button" className="ghost-button" onClick={() => copyFeed(item)}>
                {copiedFeed === (item.key || item.title) ? 'Copied' : 'Copy URL'}
              </button>
            </div>
          </article>
        ))}
        {platformCards.map(([key, item]) => (
          <article className="panel" key={key}>
            <p className="eyebrow">Calendar platform</p>
            <h2>{item.title}</h2>
            <p>{item.recommended_action}</p>
            <small>{item.sync_expectation}</small>
          </article>
        ))}
      </main>
    </AppChrome>
  );
}

function useTrustSurface() {
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

  useEffect(() => {
    let cancelled = false;
    Promise.allSettled([
      reliabilityAPI.getStatus(),
      policyAPI.get(),
      reliabilityAPI.getBenchmarkManifest(),
      reliabilityAPI.getSourceReviewQueue(),
      reliabilityAPI.getBoundarySuite(),
      reliabilityAPI.getDifferentialManifest(),
      reliabilityAPI.getSlos(),
      reliabilityAPI.getPlaybooks(),
    ]).then(([runtime, policy, benchmark, queue, boundary, differential, slo, playbooks]) => {
      if (cancelled) return;
      const rejected = [runtime, policy, benchmark, queue, boundary, differential, slo, playbooks]
        .filter((item) => item.status === 'rejected');
      const runtimeData = runtime.status === 'fulfilled' ? runtime.value : null;
      const policyData = policy.status === 'fulfilled' ? policy.value : null;
      setPayload({
        runtime: runtimeData?.runtime || null,
        policy: policyData?.policy || runtimeData?.policy || null,
        benchmark: benchmark.status === 'fulfilled' ? benchmark.value?.benchmark : null,
        queue: queue.status === 'fulfilled' ? queue.value?.queue : null,
        boundary: boundary.status === 'fulfilled' ? boundary.value?.boundary_suite : null,
        differential: differential.status === 'fulfilled' ? differential.value?.differential : null,
        slo: slo.status === 'fulfilled' ? slo.value?.slo : null,
        playbooks: playbooks.status === 'fulfilled' ? playbooks.value?.playbooks || [] : [],
      });
      setStatus({
        loading: false,
        error: rejected.length === 8
          ? describeSupportError(rejected[0].reason, 'Trust data could not be loaded from the backend.')
          : '',
      });
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return { ...payload, loading: status.loading, error: status.error };
}

const infrastructureFeatures = [
  ['Calendar conversion', 'BS to AD, AD to BS, validation, today context, and calendar metadata for software systems.'],
  ['Fiscal-year logic', 'Nepali fiscal boundaries, reporting periods, and date-range helpers for operational workflows.'],
  ['Panchanga computation', 'Tithi, nakshatra, yoga, karana, sunrise basis, and timing signals with visible method context.'],
  ['Festival intelligence', 'Festival catalogs, observance logic, calendar feeds, and source-aware public surfaces.'],
  ['Source policy', 'Evidence tiers separate official, printed, publisher, software-table, third-party, and needs-review rows.'],
  ['Future BS risk research', 'Controlled research on boundary-sensitive month-length assumptions, always computed_prediction_not_official.'],
];

function InfrastructureFeatureGrid() {
  return (
    <section className="infrastructure-grid" aria-label="Project Parva capabilities">
      {infrastructureFeatures.map(([title, body]) => (
        <article key={title}>
          <span>{title}</span>
          <p>{body}</p>
        </article>
      ))}
    </section>
  );
}

function PublicCtaRow() {
  return (
    <div className="public-cta-row">
      <a className="primary-button" href={DEFAULT_PUBLIC_DOCS_URL}>Open API docs</a>
      <a className="ghost-button" href="https://github.com/dantwoashim/Project_Parva">GitHub</a>
      <Link className="ghost-button" to="/policy">Read API policy</Link>
      <Link className="ghost-button" to="/trust">Review source posture</Link>
    </div>
  );
}

export function RedesignHome() {
  return (
    <AppChrome>
      <main className="page-shell home-page">
        <section className="infrastructure-hero">
          <div>
            <p className="eyebrow">Project Parva</p>
            <h1>Nepali calendar infrastructure for software systems.</h1>
            <p>
              BS/AD conversion, fiscal-year logic, panchanga computation, festivals, source-aware validation, and controlled calendar-risk research for teams that need reliable Nepali temporal behavior.
            </p>
            <PublicCtaRow />
          </div>
          <aside className="infrastructure-proof panel">
            <p className="eyebrow">Public boundary</p>
            <h2>Computed results stay source-aware.</h2>
            <dl>
              <div><dt>Future outputs</dt><dd>computed_prediction_not_official</dd></div>
              <div><dt>Public API</dt><dd>Stable calendar and documentation surfaces</dd></div>
              <div><dt>Private deployment</dt><dd>Controlled audit and reconciliation workflows</dd></div>
            </dl>
          </aside>
        </section>
        <section className="infrastructure-grid" aria-label="Public review links">
          {[
            ['Developer quickstart', 'Copy-paste API calls and SDK entry points for stable routes.', 'https://github.com/dantwoashim/Project_Parva/blob/main/docs/QUICKSTART.md'],
            ['Benchmark v0', '38 public-safe tasks for Nepali time reliability and review gates.', 'https://github.com/dantwoashim/Project_Parva/tree/main/public-benchmark'],
            ['Verification gates', 'Public CI, clean-clone assumptions, trust checks, leakage scans, and route inventory.', 'https://github.com/dantwoashim/Project_Parva/actions/workflows/public-verification.yml'],
            ['Known limitations', 'Authority boundaries, unsupported ranges, and non-replacement policy.', 'https://github.com/dantwoashim/Project_Parva/blob/main/docs/KNOWN_LIMITATIONS.md'],
          ].map(([title, body, href]) => (
            <a key={title} href={href}>
              <span>{title}</span>
              <p>{body}</p>
            </a>
          ))}
        </section>
        <InfrastructureFeatureGrid />
        <section className="trust-feature-band">
          <div>
            <p className="eyebrow">For financial and enterprise systems</p>
            <h2>Calendar assumptions should be audited before they affect records.</h2>
          </div>
          <p>
            Parva can work as a validation layer around existing calendar tables, fiscal logic, schedules, reporting exports, and customer-facing BS dates. It does not replace official publication or institutional approval.
          </p>
        </section>
      </main>
    </AppChrome>
  );
}

function PublicBriefPage({ eyebrow, title, body, cards, action }) {
  return (
    <AppChrome>
      <main className="page-shell public-brief-page">
        <PageHero eyebrow={eyebrow} title={title} body={body} action={action || <PublicCtaRow />} />
        <section className="infrastructure-grid">
          {cards.map(([cardTitle, cardBody]) => (
            <article key={cardTitle}>
              <span>{cardTitle}</span>
              <p>{cardBody}</p>
            </article>
          ))}
        </section>
      </main>
    </AppChrome>
  );
}

export function RedesignDevelopers() {
  return (
    <PublicBriefPage
      eyebrow="Developers"
      title="APIs for Nepali temporal logic."
      body="Use Parva for calendar conversion, fiscal periods, panchanga signals, festivals, calendar feeds, and source-aware validation without scattering fragile date tables through your product."
      cards={[
        ['API mode', 'Call the public API for stable evaluation surfaces and private deployments for controlled internal validation.'],
        ['Local integration', 'Use generated clients or simple HTTP calls for BS/AD conversion, date validation, and calendar feeds.'],
        ['Source-aware responses', 'Responses are designed to carry method context, confidence, and claim boundaries where the backend exposes them.'],
        ['Safe public research', 'Future-BS research is exposed publicly as methodology and risk posture, not as raw future month tables.'],
      ]}
    />
  );
}

export function RedesignEnterprise() {
  return (
    <PublicBriefPage
      eyebrow="Enterprise"
      title="Calendar-risk validation for operational systems."
      body="Project Parva helps teams review BS date behavior before it affects fiscal reports, payroll periods, renewal schedules, transaction records, or customer-facing dates."
      cards={[
        ['Validation layer', 'Compare existing calendar behavior against source-aware conversion and fiscal logic.'],
        ['Controlled deployment', 'Run private deployments when sensitive audits, reconciliation workflows, or internal approval rules are required.'],
        ['Review workflow', 'Use source policy, claim boundaries, and diff reports to decide which changes require human approval.'],
        ['No silent authority', 'Official publication, institutional policy, and legal requirements remain the final authority.'],
      ]}
    />
  );
}

export function RedesignFutureBsResearch() {
  return (
    <PublicBriefPage
      eyebrow="Future BS risk research"
      title="Risk labels for future calendar assumptions."
      body="Parva studies whether future BS month-length assumptions are stable, boundary-sensitive, source-conflicted, or review-worthy before they enter financial, contractual, reporting, or operational systems."
      cards={[
        ['Claim boundary', 'Every future research output is treated as computed_prediction_not_official.'],
        ['Risk posture', 'GREEN, YELLOW, and RED labels describe internal consistency and review need, not official publication.'],
        ['Source separation', 'Weak third-party and software-table rows can support shadow comparison, but not official-grade claims.'],
        ['Controlled audit', 'Full comparisons, exports, and schedule-impact workflows belong in private or controlled deployments.'],
      ]}
    />
  );
}

export function RedesignTrust() {
  const trust = useTrustSurface();
  const runtime = trust.runtime || {};
  const ephemeris = runtime.ephemeris || {};
  const queue = trust.queue || {};
  const policy = trust.policy || {};
  const endpoints = runtime.metrics?.endpoints || [];

  return (
    <TrustPageFrame
      current="trust"
      eyebrow="Trust Center"
      title="A calmer way to see what the engine knows."
      body="Every major surface is backed by API status, policy metadata, source inventory, and provenance-oriented reliability checks."
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
          <h2>Parva should show confidence without pretending certainty.</h2>
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
  const trust = useTrustSurface();
  const runtime = trust.runtime || {};
  const ephemeris = runtime.ephemeris || {};
  const cache = runtime.cache || {};
  const boundary = trust.boundary || {};
  const benchmark = trust.benchmark || {};
  const steps = [
    ['Context first', 'Date, timezone, latitude, longitude, and requested surface are normalized before interpretation.'],
    ['Compute openly', `${humanMethodLabel(ephemeris.library, 'The configured ephemeris')} powers the current sidereal calculation path when the backend is healthy.`],
    ['Compare and classify', 'Festival and timing outputs carry support tiers, authority mode, quality band, and boundary sensitivity.'],
    ['Expose provenance', 'Policy, request IDs, source status, cache state, and benchmark signals stay close to the result.'],
  ];

  return (
    <TrustPageFrame
      current="methodology"
      eyebrow="Methodology"
      title="Evidence-led calculations, not decorative certainty."
      body="The method is designed around explicit inputs, source confidence, authority comparison, and visible limits."
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
  const trust = useTrustSurface();
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
      title="Live evidence from the backend."
      body="Reliability status, benchmark manifests, source review queues, and endpoint health in one inspectable surface."
      action={<a className="ghost-button" href={apiHref('/reliability/status')}>Open JSON</a>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="truth-dashboard">
        <TrustMetricCard eyebrow="Runtime" title="Status" value={readableCategory(runtime.status)} detail={`${trustValue(runtime.warnings?.length, '0')} warnings reported.`} />
        <TrustMetricCard eyebrow="Cache" title="Artifacts" value={trustValue(cache.file_count)} detail={`${formatBytes(cache.total_bytes)} available for precomputed surfaces.`} />
        <TrustMetricCard eyebrow="Benchmark" title="Manifest" value={trustValue(benchmark.manifest_id || benchmark.version)} detail={`${trustValue(boundary.total_samples || benchmark.total_samples)} boundary or benchmark samples exposed.`} />
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
          <h2>{trustValue(boundary.status || boundary.generated_at)}</h2>
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
  const trust = useTrustSurface();
  const policy = trust.policy || {};
  const runtime = trust.runtime || {};

  return (
    <TrustPageFrame
      current="about"
      eyebrow="About Parva"
      title="A source-aware time layer for Nepal."
      body="Parva brings daily panchanga, festivals, muhurta windows, place context, and birth-reading tools into a single public reference interface."
      action={<Link className="primary-button" to="/today">Open today</Link>}
    >
      <TrustLoading loading={trust.loading} error={trust.error} />
      <section className="about-statement">
        <div>
          <p className="eyebrow">Product stance</p>
          <h2>Beautiful enough to use daily, careful enough to question.</h2>
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
  const trust = useTrustSurface();
  const policy = trust.policy || {};
  const playbooks = trust.playbooks || [];

  return (
    <TrustPageFrame
      current="policy"
      eyebrow="API Policy"
      title="The contract should be visible before anyone builds on it."
      body="This page mirrors the backend policy endpoint and shows how Parva frames usage, advisory limits, and operational recovery."
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

