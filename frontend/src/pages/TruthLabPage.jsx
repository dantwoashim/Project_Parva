import { Link } from 'react-router-dom';
import { UtilityPageHeader, UtilityStatGrid } from '../consumer/UtilityPages';
import { startCaseTruth, todayYear } from './truthLab/truthLabHelpers';
import { useTruthLabState } from './truthLab/useTruthLabState';
import './TruthLabPage.css';

export function TruthLabPage() {
  const {
    year,
    setYear,
    atlas,
    selectedId,
    setSelectedId,
    capsule,
    benchmark,
    sourceReviewQueue,
    boundarySuite,
    differential,
    loading,
    capsuleLoading,
    error,
    stats,
  } = useTruthLabState();

  return (
    <section className="truth-lab utility-page animate-fade-in-up">
      <UtilityPageHeader
        eyebrow="Truth Lab"
        title="Disagreement, proof, and boundary risk should be inspectable."
        body="This surface turns authority conflict, boundary sensitivity, and proof capsules into first-class product features instead of hidden implementation detail."
        links={[
          { label: 'Festivals', to: '/festivals' },
          { label: 'Methodology', to: '/methodology' },
          { label: 'Today', to: '/today' },
        ]}
        aside={(
          <>
            <span className="utility-page__eyebrow">Current mode</span>
            <strong>Authority-aware</strong>
            <p>Public defaults stay visible, alternates stay inspectable, and strict mode can abstain when disagreement is too sharp.</p>
          </>
        )}
      />

      <UtilityStatGrid items={stats} />

      <section className="truth-lab__controls ink-card utility-page__panel">
        <label htmlFor="truth-lab-year">
          Year
          <input
            id="truth-lab-year"
            type="number"
            min="2000"
            max="2200"
            value={year}
            onChange={(event) => setYear(Number(event.target.value) || todayYear())}
          />
        </label>
      </section>

      {loading ? (
        <section className="truth-lab__loading ink-card utility-page__panel">Loading dispute atlas...</section>
      ) : null}

      {error ? (
        <section className="truth-lab__error ink-card utility-page__panel" role="alert">{error}</section>
      ) : null}

      {atlas ? (
        <>
          {benchmark ? (
            <section className="truth-lab__benchmark utility-page__panel">
              <div className="landing-section-header">
                <p className="landing-eyebrow">Benchmark reproducibility</p>
                <h2>Run metadata, hashes, and known limits stay attached to the score.</h2>
              </div>
              <div className="truth-lab__benchmark-grid">
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Run summary</h3>
                  <p><strong>Track</strong> {startCaseTruth(benchmark.evaluation_track)}</p>
                  <p><strong>Case count</strong> {benchmark.case_count}</p>
                  <p><strong>Pass rate</strong> {benchmark.pass_rate}%</p>
                  <p><strong>Conflict policy</strong> {startCaseTruth(benchmark.conflict_policy)}</p>
                  <p><strong>Abstention policy</strong> {startCaseTruth(benchmark.abstention_policy)}</p>
                </article>
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Frozen hashes</h3>
                  <p><strong>Report hash</strong> <code>{benchmark.report_hash?.slice(0, 16) || 'N/A'}</code></p>
                  <p><strong>Engine manifest</strong> <code>{benchmark.engine_manifest_hash?.slice(0, 16) || 'N/A'}</code></p>
                  {Object.entries(benchmark.source_hashes || {}).slice(0, 3).map(([key, value]) => (
                    <p key={key}><strong>{key}</strong> <code>{String(value).slice(0, 16)}</code></p>
                  ))}
                </article>
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Known limits</h3>
                  <div className="truth-lab__limit-list">
                    {(benchmark.known_limits || []).map((item) => <p key={item}>{item}</p>)}
                  </div>
                </article>
              </div>
            </section>
          ) : null}

          {differential ? (
            <section className="truth-lab__benchmark utility-page__panel">
              <div className="landing-section-header">
                <p className="landing-eyebrow">Differential drift</p>
                <h2>Regression drift is tracked separately from authority-backed evaluation.</h2>
              </div>
              <div className="truth-lab__benchmark-grid">
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Drift summary</h3>
                  <p><strong>Total compared</strong> {differential.total_compared}</p>
                  <p><strong>Drift percent</strong> {differential.drift_percent}%</p>
                  <p><strong>Gate passed</strong> {differential.gate?.passed ? 'Yes' : 'No'}</p>
                  <p><strong>Major differences</strong> {differential.gate?.major_count ?? 0}</p>
                </article>
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Taxonomy</h3>
                  {Object.entries(differential.taxonomy || {}).map(([key, value]) => (
                    <p key={key}><strong>{startCaseTruth(key)}</strong> {value}</p>
                  ))}
                </article>
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Known limits</h3>
                  <div className="truth-lab__limit-list">
                    {(differential.known_limits || []).map((item) => <p key={item}>{item}</p>)}
                  </div>
                </article>
              </div>
            </section>
          ) : null}

          {sourceReviewQueue ? (
            <section className="truth-lab__benchmark utility-page__panel">
              <div className="landing-section-header">
                <p className="landing-eyebrow">Source review queue</p>
                <h2>Official-source inventory now feeds a deterministic human-review queue.</h2>
              </div>
              <div className="truth-lab__benchmark-grid">
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Queue summary</h3>
                  <p><strong>Total items</strong> {sourceReviewQueue.total_items}</p>
                  <p><strong>Critical</strong> {sourceReviewQueue.summary?.critical || 0}</p>
                  <p><strong>High priority</strong> {sourceReviewQueue.summary?.high || 0}</p>
                  <p><strong>Ready for promotion</strong> {sourceReviewQueue.summary?.ready_for_promotion || 0}</p>
                </article>
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Top review items</h3>
                  {(sourceReviewQueue.items || []).slice(0, 3).map((item) => (
                    <p key={item.source_id}>
                      <strong>{item.source_id}</strong> {startCaseTruth(item.review_action)} ({startCaseTruth(item.review_priority)})
                    </p>
                  ))}
                </article>
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Review model</h3>
                  <p>Structured artifacts are never auto-promoted.</p>
                  <p>Archived raw PDFs are queued for extraction improvement.</p>
                  <p>Promotion stays review-driven and source-family explicit.</p>
                </article>
              </div>
            </section>
          ) : null}

          {boundarySuite ? (
            <section className="truth-lab__benchmark utility-page__panel">
              <div className="landing-section-header">
                <p className="landing-eyebrow">Boundary suite</p>
                <h2>Sunrise flips, sankranti edges, and adhik-month transitions stay regression-tested.</h2>
              </div>
              <div className="truth-lab__benchmark-grid">
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Suite summary</h3>
                  <p><strong>Suites</strong> {boundarySuite.suite_count}</p>
                  <p><strong>Total samples</strong> {boundarySuite.total_samples}</p>
                  <p><strong>Total passed</strong> {boundarySuite.total_passed}</p>
                  <p><strong>Pass rate</strong> {boundarySuite.pass_rate}</p>
                </article>
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Boundary families</h3>
                  {(boundarySuite.suites || []).map((item) => (
                    <p key={item.suite_id}>
                      <strong>{startCaseTruth(item.suite_id)}</strong> {item.samples} samples, pass rate {item.pass_rate}
                    </p>
                  ))}
                </article>
                <article className="ink-card truth-lab__benchmark-card">
                  <h3>Why it matters</h3>
                  <p>High-risk boundary classes should be visible, not hidden behind a single confidence label.</p>
                  <p>The same suite powers runtime reporting and public artifact publication.</p>
                </article>
              </div>
            </section>
          ) : null}

          <section className="truth-lab__ladder utility-page__panel">
            <div className="landing-section-header">
              <p className="landing-eyebrow">Truth ladder</p>
              <h2>Every answer should say what kind of truth it is.</h2>
            </div>
            <div className="truth-lab__ladder-grid">
              {atlas.truth_ladder.map((item) => (
                <article key={item.tier} className="ink-card truth-lab__ladder-card">
                  <p className="truth-lab__ladder-tier">{startCaseTruth(item.tier)}</p>
                  <h3>{item.title}</h3>
                  <p>{item.body}</p>
                </article>
              ))}
            </div>
          </section>

          <section className="truth-lab__atlas">
            <div className="truth-lab__atlas-list utility-page__panel">
              <div className="landing-section-header">
                <p className="landing-eyebrow">Dispute atlas</p>
                <h2>Live contested or risk-sensitive festival rows.</h2>
              </div>
              <div className="truth-lab__dispute-list">
                {atlas.disputes.map((item) => (
                  <button
                    key={`${item.festival_id}-${item.year}`}
                    type="button"
                    className={`truth-lab__dispute-card ${selectedId === item.festival_id ? 'is-active' : ''}`.trim()}
                    onClick={() => setSelectedId(item.festival_id)}
                  >
                    <div className="truth-lab__dispute-head">
                      <strong>{item.festival_name}</strong>
                      <span>{item.start_date}</span>
                    </div>
                    <p>{startCaseTruth(item.boundary_radar)} · stability {item.stability_score}</p>
                    <p>{item.recommended_action}</p>
                  </button>
                ))}
              </div>
            </div>

            <div className="truth-lab__capsule utility-page__panel">
              <div className="landing-section-header">
                <p className="landing-eyebrow">Proof capsule</p>
                <h2>{capsule?.festival_name || 'Select a dispute row'}</h2>
              </div>
              {capsuleLoading ? <p>Loading proof capsule...</p> : null}
              {capsule ? (
                <>
                  <div className="truth-lab__capsule-grid">
                    <article className="ink-card">
                      <h3>Selection</h3>
                      <p><strong>Start date</strong> {capsule.selection.start_date}</p>
                      <p><strong>Support tier</strong> {startCaseTruth(capsule.selection.support_tier)}</p>
                      <p><strong>Engine path</strong> {capsule.selection.engine_path}</p>
                      <p><strong>Fallback used</strong> {capsule.selection.fallback_used ? 'Yes' : 'No'}</p>
                    </article>
                    <article className="ink-card">
                      <h3>Risk</h3>
                      <p><strong>Boundary radar</strong> {startCaseTruth(capsule.risk.boundary_radar)}</p>
                      <p><strong>Stability score</strong> {capsule.risk.stability_score}</p>
                      <p><strong>Mode</strong> {startCaseTruth(capsule.risk.risk_mode)}</p>
                      <p>{capsule.risk.recommended_action}</p>
                    </article>
                  </div>
                  <article className="ink-card truth-lab__capsule-lineage">
                    <h3>Source lineage</h3>
                    <p><strong>Source family</strong> {capsule.source_lineage.source_family || 'Computed rule profile'}</p>
                    <p><strong>Authority conflict</strong> {capsule.source_lineage.authority_conflict ? 'Present' : 'No conflict published'}</p>
                    <p><strong>Rule summary</strong> {capsule.source_lineage.rule_summary}</p>
                    {capsule.provenance?.verify_url ? (
                      <p>
                        <a href={capsule.provenance.verify_url} target="_blank" rel="noreferrer">Open provenance reference</a>
                      </p>
                    ) : null}
                    <p>
                      <Link to={`/festivals/${capsule.festival_id}`}>Open festival detail</Link>
                    </p>
                  </article>
                </>
              ) : (
                <p>Select a dispute row to inspect its proof capsule.</p>
              )}
            </div>
          </section>
        </>
      ) : null}
    </section>
  );
}

export default TruthLabPage;
