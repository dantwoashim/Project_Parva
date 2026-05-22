import {
  AppChrome,
  Link,
  NavLink,
  PageHero,
  readableCategory,
} from './ExperienceCommon.jsx';
import { trustValue } from './trustPageUtils.js';

function TrustNav({ current }) {
  const items = [
    { id: 'trust', label: 'Trust', to: '/trust' },
    { id: 'methodology', label: 'Methodology', to: '/methodology' },
    { id: 'truth', label: 'Truth Lab', to: '/truth-lab' },
    { id: 'about', label: 'About', to: '/about' },
    { id: 'policy', label: 'API Policy', to: '/policy' },
  ];
  return (
    <nav className="trust-nav" aria-label="Trust pages">
      {items.map((item) => (
        <NavLink key={item.id} to={item.to} className={item.id === current ? 'is-current' : undefined}>
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}

export function TrustLoading({ loading, error }) {
  if (loading) {
    return (
      <article className="trust-alert">
        <span aria-hidden="true" />
        <div>
          <strong>Loading backend trust surfaces</strong>
          <p>Policy, reliability, benchmark, source review, and boundary data are being fetched live.</p>
        </div>
      </article>
    );
  }
  if (error) {
    return (
      <article className="trust-alert is-error">
        <span aria-hidden="true" />
        <div>
          <strong>Trust data unavailable</strong>
          <p>{error}</p>
        </div>
      </article>
    );
  }
  return null;
}

export function TrustMetricCard({ eyebrow, title, value, detail, actionTo, actionLabel }) {
  if (value === 'Unavailable' && !detail) return null;
  return (
    <article className="trust-metric-card">
      <p className="eyebrow">{eyebrow}</p>
      <h2>{title}</h2>
      <strong>{value}</strong>
      <p>{detail}</p>
      {actionTo ? <Link className="text-link" to={actionTo}>{actionLabel || 'Open'}</Link> : null}
    </article>
  );
}

export function TrustLimitsStrip({ runtime = {}, policy = {} }) {
  const warnings = runtime.warnings || [];
  return (
    <section className="trust-limits-strip" aria-label="Known trust limits">
      <div>
        <span>Known limits</span>
        <strong>{warnings.length ? `${warnings.length} warnings` : 'No runtime warnings'}</strong>
        <small>{warnings[0] || 'Live feed did not report runtime warnings.'}</small>
      </div>
      <div>
        <span>Advisory boundary</span>
        <strong>{readableCategory(policy.usage || 'Informational')}</strong>
        <small>{trustValue(policy.advisory, 'Verify ritual-critical decisions locally.')}</small>
      </div>
      <div>
        <span>Failure posture</span>
        <strong>Show uncertainty</strong>
        <small>Missing feeds should hide claims instead of presenting fake certainty.</small>
      </div>
    </section>
  );
}

export function TrustPageFrame({ current, eyebrow, title, body, action, children }) {
  return (
    <AppChrome>
      <main className="page-shell trust-page-shell">
        <PageHero eyebrow={eyebrow} title={title} body={body} action={action} />
        <TrustNav current={current} />
        {children}
      </main>
    </AppChrome>
  );
}
