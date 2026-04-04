import { UtilityPageHeader } from '../consumer/UtilityPages';
import './AboutPage.css';

export function AboutPage() {
  return (
    <section className="about-page utility-page animate-fade-in-up">
      <UtilityPageHeader
        eyebrow="About Parva"
        title="Parva is built to make sacred time feel clear before it feels technical."
        body="The product is designed for everyday people first: calm language, one useful answer, and deeper detail only when someone wants it."
        links={[
          { label: 'Today', to: '/#today' },
          { label: 'Festivals', to: '/#festivals' },
          { label: 'Best Time', to: '/#best-time' },
        ]}
        aside={(
          <>
            <span className="utility-page__eyebrow">Category position</span>
            <strong>Nepal-first sacred time guide</strong>
            <p>The consumer product should feel singular, calm, and serious across every route.</p>
          </>
        )}
      />

      <section className="about-grid">
        <article className="editorial-card about-card utility-page__panel">
          <h2>What it is</h2>
          <p>
            A Nepal-focused guide for festivals, panchanga, muhurta, and kundali that tries to feel trustworthy without feeling overloaded.
          </p>
        </article>
        <article className="editorial-card about-card utility-page__panel">
          <h2>How trust works</h2>
          <p>
            The first answer stays calm and useful. Method notes, where results can vary, and deeper evidence stay available when you want to inspect them.
          </p>
        </article>
      </section>

      <section className="editorial-card about-details utility-page__panel">
        <div className="landing-section-header">
          <p className="landing-eyebrow">Principles</p>
          <h2>What the interface promises</h2>
        </div>
        <div className="about-details__grid">
          <article>
            <h3>Meaning before mechanics</h3>
            <p>The first screen should answer the question, not explain the machinery.</p>
          </article>
          <article>
            <h3>Calm trust</h3>
            <p>Evidence, method, and variance notes stay available, but they never crowd the first answer.</p>
          </article>
          <article>
            <h3>One product language</h3>
            <p>Landing, reading, and planning surfaces should feel like one premium product, not separate dashboards.</p>
          </article>
        </div>
      </section>
    </section>
  );
}

export default AboutPage;
