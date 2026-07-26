import { Link } from 'react-router-dom';
import benchmarkSummary from '../data/benchmarkSummary.json';

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

export function RedesignBenchmark() {
  const rows = categoryRows(benchmarkSummary);
  const reviewGate = benchmarkSummary.review_gate_performance || {};

  return (
    <main className="trust-page-shell benchmark-page" data-testid="benchmark-page">
      <section className="page-hero">
        <div>
          <span className="eyebrow">Public benchmark v0</span>
          <h1>Nepali Time Reliability Benchmark</h1>
          <p>
            A technical benchmark for Nepali calendar behavior, source handling,
            uncertainty, review gates, and machine-readable output.
          </p>
        </div>
        <div className="hero-actions">
          <a href="https://github.com/dantwoashim/Project_Parva/tree/main/public-benchmark">Benchmark files</a>
          <Link to="/developers">Developer quickstart</Link>
        </div>
      </section>

      <section className="trust-hero-grid" aria-label="Benchmark headline scores">
        <article className="trust-metric-card">
          <h2>Parva score</h2>
          <strong>{formatPercent(benchmarkSummary.parva_score_percent)}</strong>
          <p>{benchmarkSummary.task_count} public-safe tasks executed against Parva.</p>
        </article>
        <article className="trust-metric-card">
          <h2>Static baseline</h2>
          <strong>{formatPercent(benchmarkSummary.static_score_percent)}</strong>
          <p>Naive/static behavior without source-aware review boundaries.</p>
        </article>
        <article className="trust-metric-card">
          <h2>Score gap</h2>
          <strong>{formatPercent(benchmarkSummary.score_gap_percent)}</strong>
          <p>Difference between Parva and the static baseline in benchmark v0.</p>
        </article>
        <article className="trust-metric-card">
          <h2>Review gates</h2>
          <strong>
            {reviewGate.passed || 0}/{reviewGate.tasks || 0}
          </strong>
          <p>{formatPercent(reviewGate.score_percent)} review-required behavior preservation.</p>
        </article>
      </section>

      <section className="simple-grid" aria-label="Benchmark category breakdown">
        <article className="trust-metric-card">
          <h2>Category Breakdown</h2>
          <div className="route-table-wrap">
            <table className="route-table">
              <thead>
                <tr>
                  <th>Category</th>
                  <th>Tasks</th>
                  <th>Parva score</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.category}>
                    <td>{row.category}</td>
                    <td>{row.tasks}</td>
                    <td>{formatPercent(row.score)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>
        <article className="trust-metric-card">
          <h2>Claim Boundary</h2>
          <p>
            Benchmark v0 is a technical reliability benchmark, not official government/calendar
            authority.
          </p>
          <p>
            Future-BS cases are scored on review-required behavior and
            computed_prediction_not_official boundaries, not public exact unsupported future
            predictions.
          </p>
        </article>
      </section>
    </main>
  );
}
