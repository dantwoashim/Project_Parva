import { Check, CircleMinus, ExternalLink, GitCompareArrows, Play } from 'lucide-react';
import { Link } from '@parva/router';
import benchmarkSummary from '../data/benchmarkSummary.json';
import competitorBenchmark from '../data/competitorBenchmark.json';
import './styles/polish/15-positioning-licensing.css';

function formatPercent(value) {
  return `${Number(value || 0).toFixed(2)}%`;
}

function categoryRows(summary) {
  const parva = summary.category_breakdown?.parva || {};
  return Object.entries(parva).map(([category, data]) => ({
    category: category.replaceAll('_', ' '),
    tasks: data.tasks,
    score: data.score_percent,
  }));
}

function marketStatus(value) {
  return value === 'documented';
}

const capabilityColumns = [
  ['bs_conversion', 'BS conversion'],
  ['location_aware_astronomical_panchanga', 'Astronomical Panchanga'],
  ['nepal_business_rules', 'Nepal business rules'],
  ['future_bs_research', 'Future BS research'],
  ['public_replay_artifacts', 'Replay artifacts'],
  ['public_conformance_suite', 'Conformance suite'],
];

export function RedesignBenchmark() {
  const rows = categoryRows(benchmarkSummary);
  const reviewGate = benchmarkSummary.review_gate_performance || {};
  const historical = competitorBenchmark.historical_conformance || [];
  const replay = competitorBenchmark.forecast_replay || {};
  const market = competitorBenchmark.market_review || {};

  return (
    <main className="trust-page-shell benchmark-page comparison-page" data-testid="benchmark-page">
      <section className="page-hero">
        <div>
          <span className="eyebrow">Public evidence, rerunnable</span>
          <h1>Benchmark the claims.</h1>
          <p>
            One public reliability suite, one named-tool BS comparison, and one
            chronological replay of the future-BS engine.
          </p>
        </div>
        <div className="hero-actions">
          <a href="https://github.com/dantwoashim/Project_Parva/tree/main/public-benchmark">
            <GitCompareArrows aria-hidden="true" /> Benchmark files
          </a>
          <a href="https://github.com/dantwoashim/Project_Parva/blob/main/public-benchmark/results/competitor-comparison.md">
            <Play aria-hidden="true" /> Reproduce comparison
          </a>
        </div>
      </section>

      <section className="comparison-headlines" aria-label="Benchmark headline results">
        <article>
          <span>Public reliability suite</span>
          <strong>{formatPercent(benchmarkSummary.parva_score_percent)}</strong>
          <p>{benchmarkSummary.task_count} tasks across calendar behavior, metadata, and review gates.</p>
        </article>
        <article>
          <span>Historical conformance</span>
          <strong>72/72</strong>
          <p>Parva matches every month in the common BS 2078-2083 fixture.</p>
        </article>
        <article id="forecast-replay">
          <span>Chronological forecast replay</span>
          <strong>{replay.exact_matches || 0}/{replay.month_cases || 0}</strong>
          <p>Each target year used training data ending in the previous year.</p>
        </article>
        <article>
          <span>Review gates</span>
          <strong>{reviewGate.passed || 0}/{reviewGate.tasks || 0}</strong>
          <p>Review-required behavior retained across the public suite.</p>
        </article>
      </section>

      <section className="comparison-section" aria-labelledby="real-tools-title">
        <header>
          <div>
            <span className="eyebrow">Executed against published packages</span>
            <h2 id="real-tools-title">Historical BS month conformance</h2>
          </div>
          <p>Month lengths were derived from consecutive BS-to-AD month-start conversions, then compared with one fixed 72-case fixture.</p>
        </header>
        <div className="route-table-wrap comparison-desktop-table">
          <table className="route-table comparison-table">
            <thead>
              <tr>
                <th>Implementation</th>
                <th>Version</th>
                <th>Exact months</th>
                <th>Accuracy</th>
                <th>Mismatches</th>
              </tr>
            </thead>
            <tbody>
              {historical.map((item) => (
                <tr key={item.implementation}>
                  <td><a href={item.source}>{item.implementation}<ExternalLink aria-hidden="true" /></a></td>
                  <td>{item.version}</td>
                  <td>{item.exact_matches}/{item.month_cases}</td>
                  <td>{formatPercent(item.accuracy_percent)}</td>
                  <td>{item.mismatches?.length || 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="comparison-mobile-cards" aria-label="Historical BS month conformance results">
          {historical.map((item) => (
            <article key={item.implementation}>
              <header><a href={item.source}>{item.implementation}<ExternalLink aria-hidden="true" /></a><small>{item.version}</small></header>
              <strong>{item.exact_matches}/{item.month_cases}</strong>
              <span>{formatPercent(item.accuracy_percent)} · {item.mismatches?.length || 0} mismatches</span>
            </article>
          ))}
        </div>
        <div className="comparison-scope-note">
          <strong>Two different questions.</strong>
          <p>Historical conformance measures current lookup output. Forecast replay measures whether a method could predict each target year from earlier years. Lookup-only packages receive no forecast score.</p>
        </div>
      </section>

      <section id="market-review" className="comparison-section market-review" aria-labelledby="market-review-title">
        <header>
          <div>
            <span className="eyebrow">Market review · {market.as_of}</span>
            <h2 id="market-review-title">The complete capability set</h2>
          </div>
          <p>{market.match_definition}</p>
        </header>
        <div className="route-table-wrap comparison-desktop-table">
          <table className="route-table capability-table">
            <thead>
              <tr>
                <th>Product</th>
                {capabilityColumns.map(([, label]) => <th key={label}>{label}</th>)}
              </tr>
            </thead>
            <tbody>
              {(market.products || []).map((product) => (
                <tr key={product.name}>
                  <td><a href={product.source}>{product.name}<ExternalLink aria-hidden="true" /></a></td>
                  {capabilityColumns.map(([key]) => (
                    <td key={key} aria-label={marketStatus(product[key]) ? 'Documented' : 'Not found in review'}>
                      {marketStatus(product[key])
                        ? <Check className="capability-yes" aria-hidden="true" />
                        : <CircleMinus className="capability-unseen" aria-hidden="true" />}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="comparison-mobile-cards market-mobile-cards" aria-label="Reviewed product capabilities">
          {(market.products || []).map((product) => {
            const documented = capabilityColumns.filter(([key]) => marketStatus(product[key]));
            return (
              <article key={product.name}>
                <header><a href={product.source}>{product.name}<ExternalLink aria-hidden="true" /></a><small>{documented.length}/{capabilityColumns.length} documented</small></header>
                <ul>
                  {documented.map(([, label]) => <li key={label}><Check aria-hidden="true" />{label}</li>)}
                </ul>
              </article>
            );
          })}
        </div>
        <div className="comparison-conclusion">
          <span>Review conclusion</span>
          <strong>{market.conclusion}</strong>
          <p>Blank capabilities mean the feature was absent from the reviewed public documentation. They do not prove that private or unpublished functionality is absent.</p>
        </div>
      </section>

      <section className="comparison-section" aria-labelledby="suite-title">
        <header>
          <div>
            <span className="eyebrow">Nepali Time Reliability Benchmark v0</span>
            <h2 id="suite-title">Category results</h2>
          </div>
          <p>The broader suite tests deterministic behavior, source handling, uncertainty, review gates, and machine-readable structure.</p>
        </header>
        <div className="benchmark-category-grid">
          {rows.map((row) => (
            <article key={row.category}>
              <span>{row.category}</span>
              <strong>{formatPercent(row.score)}</strong>
              <small>{row.tasks} tasks</small>
            </article>
          ))}
        </div>
      </section>

      <section className="benchmark-trust-link">
        <div>
          <span className="eyebrow">Trust center</span>
          <h2>Review operating boundaries in one place.</h2>
        </div>
        <Link to="/trust">Open Trust Center</Link>
      </section>
    </main>
  );
}
