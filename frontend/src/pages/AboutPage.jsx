import { UtilityPageHeader } from '../consumer/UtilityPages';
import './AboutPage.css';

export function AboutPage() {
  return (
    <section className="about-page utility-page animate-fade-in-up">
      <UtilityPageHeader
        eyebrow="About Parva"
        title="Parva helps people check sacred dates and timing without wading through jargon."
        body="The product starts with a direct answer, then exposes the method, evidence, and caveats when you need them."
        links={[
          { label: 'Today', to: '/#today' },
          { label: 'Festivals', to: '/#festivals' },
          { label: 'Best Time', to: '/#best-time' },
        ]}
        aside={(
          <>
            <span className="utility-page__eyebrow">Category position</span>
            <strong>Nepal-focused temporal reference</strong>
            <p>The product is meant to keep everyday calendar and observance questions readable across routes.</p>
          </>
        )}
      />

      <section className="about-grid">
        <article className="editorial-card about-card utility-page__panel">
          <h2>What it is</h2>
          <p>
            A Nepal-focused reference for festivals, panchanga, muhurta, and personal timing context.
          </p>
        </article>
        <article className="editorial-card about-card utility-page__panel">
          <h2>How it stays inspectable</h2>
          <p>
            Each result can expose the place, date, method, and evidence used so the answer can be checked.
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
            <h3>Answer first</h3>
            <p>The first screen should answer the question before it introduces background detail.</p>
          </article>
          <article>
            <h3>Show your work</h3>
            <p>Evidence, method, and variance notes stay available, but they should not crowd the first answer.</p>
          </article>
          <article>
            <h3>Stay consistent</h3>
            <p>Landing, reading, and planning surfaces should feel like one product instead of separate dashboards.</p>
          </article>
        </div>
      </section>
    </section>
  );
}

export default AboutPage;
