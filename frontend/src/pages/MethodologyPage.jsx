import { useEffect } from 'react';
import { UtilityPageHeader } from '../consumer/UtilityPages';
import { trackEvent } from '../services/analytics';
import './MethodologyPage.css';

const METHODOLOGY_LAYERS = [
  {
    title: 'Visible inputs',
    body: 'Major results should state the place, date, and method used.',
  },
  {
    title: 'Clear support level',
    body: 'Responses should signal whether they come from validated computation, provisional data, or a fallback path.',
  },
  {
    title: 'Local continuity',
    body: 'Saved places, reminders, readings, and integrations can stay on this device until account-backed sync is ready.',
  },
  {
    title: 'Inspectable evidence',
    body: 'Method notes, trace metadata, and variance notes stay one step away instead of being buried.',
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
        title="Method should be inspectable, not mystical."
        body="Parva tries to answer quickly, then expose the method, caveats, and evidence behind the result."
        links={[
          { label: 'Today', to: '/#today' },
          { label: 'Best Time', to: '/#best-time' },
          { label: 'My Place', to: '/#my-place' },
        ]}
        aside={(
          <>
            <span className="utility-page__eyebrow">Review posture</span>
            <strong>Inspectable by default</strong>
            <p>Each result should name its inputs before it makes a strong claim.</p>
          </>
        )}
      />

      <section className="method-grid">
        {METHODOLOGY_LAYERS.map((item) => (
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
          <h2>Guest-first means local continuity now and heavier systems later.</h2>
        </div>
        <div className="method-detail__grid">
          <article>
            <h3>Saved state stays local</h3>
            <p>Places, reminders, readings, and integrations are stored on this device for now, with export and import available from Profile.</p>
          </article>
          <article>
            <h3>Do not overbuild early</h3>
            <p>Parva should not interrupt a simple task with account or platform language unless a heavier system is actually ready and needed.</p>
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
