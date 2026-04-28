import { useEffect } from 'react';
import { UtilityPageHeader } from '../consumer/UtilityPages';
import { trackEvent } from '../services/analytics';
import './MethodologyPage.css';

const TRUST_LAYERS = [
  {
    title: 'First impression trust',
    body: 'A calm shell, clear language, and fewer broken states should do more than decorative trust badges ever could.',
  },
  {
    title: 'Result trust',
    body: 'Every major answer should state the place used, the date used, and a short note about how confident the product is in that answer.',
  },
  {
    title: 'Local-first continuity',
    body: 'Saved places, reminders, readings, and integrations can stay on this device without adding a heavier account layer before the product really needs it.',
  },
  {
    title: 'Verifiability',
    body: 'Method detail, trace metadata, and variance notes stay available on demand through contextual evidence drawers.',
  },
];

export function MethodologyPage() {
  useEffect(() => {
    trackEvent('methodology_opened', { source: 'route' });
  }, []);

  return (
    <section className="method-page utility-page animate-fade-in-up">
      <UtilityPageHeader
        eyebrow="Methodology"
        title="Trust should come from visible seriousness, not extra chrome."
        body="Parva is built to lead with calm guidance first, then offer method, variance, and evidence when you want to inspect the answer more closely."
        links={[
          { label: 'Today', to: '/#today' },
          { label: 'Best Time', to: '/#best-time' },
          { label: 'My Place', to: '/#my-place' },
        ]}
        aside={(
          <>
            <span className="utility-page__eyebrow">Trust posture</span>
            <strong>Meaning first</strong>
            <p>Every result page should answer the question before it explains the method.</p>
          </>
        )}
      />

      <section className="method-grid">
        {TRUST_LAYERS.map((item) => (
          <article key={item.title} className="ink-card method-card utility-page__panel">
            <h2>{item.title}</h2>
            <p>{item.body}</p>
          </article>
        ))}
      </section>

      <section className="ink-card method-detail utility-page__panel">
        <div className="landing-section-header">
          <p className="landing-eyebrow">What you should expect</p>
          <h2>Parva should always tell you enough to act, then enough to verify.</h2>
        </div>
        <div className="method-detail__grid">
          <article>
            <h3>Place and date used</h3>
            <p>Timing should always tell you which place and date the answer was computed for.</p>
          </article>
          <article>
            <h3>Method profile</h3>
            <p>Each answer should expose a readable method name, not internal jargon, when you open evidence.</p>
          </article>
          <article>
            <h3>Where this can vary</h3>
            <p>When data is partial, Parva should defer the section or soften the claim instead of showing brittle empty states.</p>
          </article>
        </div>
      </section>

      <section className="ink-card method-detail utility-page__panel">
        <div className="landing-section-header">
          <p className="landing-eyebrow">Current product posture</p>
          <h2>Guest-first means local continuity first and heavier systems later.</h2>
        </div>
        <div className="method-detail__grid">
          <article>
            <h3>Saved state stays local</h3>
            <p>Places, reminders, readings, and integrations are stored on this device for now, with export and import available from Profile.</p>
          </article>
          <article>
            <h3>Keep the flow light</h3>
            <p>Parva should not interrupt a simple consumer task with account or platform language unless a heavier system is ready and genuinely needed.</p>
          </article>
          <article>
            <h3>Missing data should step back</h3>
            <p>If sunrise, ranking detail, or a service response is missing, the UI should omit the section or downgrade gracefully instead of foregrounding failure.</p>
          </article>
        </div>
      </section>
    </section>
  );
}

export default MethodologyPage;
