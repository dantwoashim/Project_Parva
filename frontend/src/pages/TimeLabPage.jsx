import { Link } from 'react-router-dom';
import { useTemporalContext } from '../context/useTemporalContext';
import {
  BS_MONTHS,
  DEFAULT_BS_ERA,
  DEFAULT_GREGORIAN_ERA,
  formatHistoricalYear,
  formatInputSignature,
  formatOutputCoordinate,
  GREGORIAN_MONTHS,
  HORIZON_ORDER,
  modeSummary,
  supportPosture,
  systemCopy,
} from './timeLab/timeLabHelpers';
import { useTimeLabState } from './timeLab/useTimeLabState';
import './TimeLabPage.css';

export function TimeLabPage() {
  const { state } = useTemporalContext();
  const {
    draft,
    result,
    loading,
    error,
    draftHorizon,
    dayLimit,
    signature,
    presets,
    isPresetPending,
    patchDraft,
    submitCurrentDraft,
    applyPreset,
    resetToToday,
    primaryResult,
    primaryEngine,
    comparisonLabel,
  } = useTimeLabState(state.timezone);

  return (
    <section className="time-lab-page animate-fade-in-up consumer-route consumer-route--analysis">
      <header className="time-lab-hero">
        <div className="time-lab-hero__copy">
          <p className="time-lab-page__eyebrow">Experimental surface</p>
          <h1 className="text-hero">Infinite Conversion Lab.</h1>
          <p className="time-lab-hero__summary">
            Convert between Gregorian and Bikram Sambat across the live engine window, then keep going into BC, far-future AD,
            and speculative BS horizons when the published table runs out.
          </p>
          <div className="time-lab-hero__chips">
            <span>{draftHorizon.label}</span>
            <span>{signature}</span>
            <span>{result ? modeSummary(result) : primaryEngine}</span>
          </div>
        </div>

        <div className="time-lab-hero__visual" aria-hidden="true">
          <div className="time-lab-hero__ring time-lab-hero__ring--outer" />
          <div className="time-lab-hero__ring time-lab-hero__ring--middle" />
          <div className="time-lab-hero__ring time-lab-hero__ring--inner" />
          <div className="time-lab-hero__core">
            <strong>{result ? formatOutputCoordinate(primaryResult) : 'Awaiting lock'}</strong>
            <span>{result?.horizon?.label || draftHorizon.label}</span>
          </div>
        </div>
      </header>

      <section className="time-lab-console">
        <form className="time-lab-console__panel ink-card" onSubmit={submitCurrentDraft}>
          <div className="time-lab-console__head">
            <div>
              <p className="time-lab-page__eyebrow">Origin system</p>
              <h2>Switch the input calendar, then throw it through the lab.</h2>
            </div>
            <div className="time-lab-console__actions">
              <button type="button" className="btn btn-secondary" onClick={resetToToday}>
                Reset to today
              </button>
              <button type="submit" className="btn btn-primary">
                {loading ? 'Locking conversion...' : 'Run conversion'}
              </button>
            </div>
          </div>

          <div className="time-lab-toggle">
            <button
              type="button"
              className={`time-lab-toggle__button ${draft.system === 'gregorian' ? 'is-active' : ''}`.trim()}
              onClick={() => patchDraft({ system: 'gregorian', era: DEFAULT_GREGORIAN_ERA })}
            >
              Gregorian origin
            </button>
            <button
              type="button"
              className={`time-lab-toggle__button ${draft.system === 'bs' ? 'is-active' : ''}`.trim()}
              onClick={() => patchDraft({ system: 'bs', era: DEFAULT_BS_ERA })}
            >
              BS origin
            </button>
          </div>

          <div className="time-lab-console__grid">
            <div className="time-lab-console__cluster">
              <label className="ink-input">
                <span>Era</span>
                <div className="time-lab-mini-toggle">
                  {(draft.system === 'gregorian'
                    ? [{ label: 'AD', value: 'AD' }, { label: 'BC', value: 'BC' }]
                    : [{ label: 'BS', value: 'BS' }, { label: 'Pre-BS', value: 'PRE_BS' }]).map((option) => (
                    <button
                      key={option.value}
                      type="button"
                      className={`time-lab-mini-toggle__button ${draft.era === option.value ? 'is-active' : ''}`.trim()}
                      onClick={() => patchDraft({ era: option.value })}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </label>

              <label className="ink-input">
                <span>Year</span>
                <input
                  type="number"
                  min="1"
                  step="1"
                  value={draft.year}
                  onChange={(event) => patchDraft({ year: event.target.value })}
                />
              </label>
            </div>

            <label className="ink-input">
              <span>Month</span>
              <select
                value={draft.month}
                onChange={(event) => patchDraft({ month: Number(event.target.value) })}
              >
                {(draft.system === 'gregorian' ? GREGORIAN_MONTHS : BS_MONTHS).map((monthName, index) => (
                  <option key={monthName} value={index + 1}>
                    {index + 1}. {monthName}
                  </option>
                ))}
              </select>
            </label>

            <label className="ink-input">
              <span>Day</span>
              <input
                type="number"
                min="1"
                max={dayLimit}
                step="1"
                value={draft.day}
                onChange={(event) => patchDraft({ day: Number(event.target.value) })}
              />
            </label>
          </div>

          <div className="time-lab-console__meta">
            <div>
              <span className="time-lab-console__meta-label">Target</span>
              <strong>{draft.system === 'gregorian' ? 'Bikram Sambat' : 'Gregorian'}</strong>
            </div>
            <div>
              <span className="time-lab-console__meta-label">Day limit</span>
              <strong>{dayLimit}</strong>
            </div>
            <div>
              <span className="time-lab-console__meta-label">Horizon</span>
              <strong>{draftHorizon.label}</strong>
            </div>
            <div>
              <span className="time-lab-console__meta-label">Query signature</span>
              <strong>{signature}</strong>
            </div>
          </div>
        </form>

        <aside className="time-lab-console__rail">
          <section className="time-lab-rail ink-card">
            <p className="time-lab-page__eyebrow">Horizon rail</p>
            <div className="time-lab-rail__track" aria-hidden="true">
              {HORIZON_ORDER.map((band) => (
                <span
                  key={band}
                  className={`time-lab-rail__segment ${draftHorizon.band === band ? 'is-active' : ''}`.trim()}
                />
              ))}
            </div>
            <div className="time-lab-rail__labels">
              {HORIZON_ORDER.map((band) => (
                <div key={band}>
                  <strong>{band.replace('_', ' ')}</strong>
                </div>
              ))}
            </div>
            <p>{draftHorizon.note}</p>
          </section>

          <section className="time-lab-presets ink-card">
            <div className="time-lab-presets__head">
              <p className="time-lab-page__eyebrow">Preset jumps</p>
              <span>{isPresetPending ? 'Retuning...' : 'One tap re-centers the lab.'}</span>
            </div>
            <div className="time-lab-presets__grid">
              {presets.map((preset) => (
                <button
                  key={preset.id}
                  type="button"
                  className={`time-lab-presets__button ${preset.id === 'today' ? 'is-live-today' : ''}`.trim()}
                  onClick={() => applyPreset(preset.query)}
                >
                  <strong>{preset.label}</strong>
                  <span>{preset.detail}</span>
                </button>
              ))}
            </div>
          </section>
        </aside>
      </section>

      {error ? (
        <section className="time-lab-status ink-card" role="alert">
          <p className="time-lab-page__eyebrow">Conversion failed to lock</p>
          <h2>{error}</h2>
          <p>Try a valid date coordinate, or jump to one of the preset horizons to re-seed the lab.</p>
        </section>
      ) : null}

      {result ? (
        <section className="time-lab-results">
          <article className="time-lab-stage">
            <div className="time-lab-stage__headline">
              <p className="time-lab-page__eyebrow">
                {result.anchored ? 'Blended answer' : 'Experimental answer'}
              </p>
              <h2>{formatOutputCoordinate(primaryResult)}</h2>
              <p>{comparisonLabel}</p>
            </div>

            <div className="time-lab-stage__facts">
              <div>
                <span>Input</span>
                <strong>{formatInputSignature(result.query)}</strong>
              </div>
              <div>
                <span>Primary engine</span>
                <strong>{primaryEngine}</strong>
              </div>
              <div>
                <span>Drift</span>
                <strong>{result.driftDays == null ? 'No comparison' : `${result.driftDays} day${result.driftDays === 1 ? '' : 's'}`}</strong>
              </div>
              <div>
                <span>Support posture</span>
                <strong>{supportPosture(result.horizon)}</strong>
              </div>
            </div>
          </article>

          <div className="time-lab-results__grid">
            {result.anchored ? (
              <article className="time-lab-result-card time-lab-result-card--anchored ink-card">
                <p className="time-lab-page__eyebrow">Live engine answer</p>
                <h3>{formatOutputCoordinate(result.anchored.output)}</h3>
                <p>
                  {result.anchored.sourceRange
                    ? `Source range: ${result.anchored.sourceRange}`
                    : 'The backend did not expose a source range for this result.'}
                </p>
                <dl>
                  <div>
                    <dt>Confidence</dt>
                    <dd>{result.anchored.confidence}</dd>
                  </div>
                  <div>
                    <dt>Error band</dt>
                    <dd>{result.anchored.estimatedErrorDays ?? 'n/a'}</dd>
                  </div>
                  <div>
                    <dt>Track</dt>
                    <dd>{result.horizon.label}</dd>
                  </div>
                </dl>
              </article>
            ) : (
              <article className="time-lab-result-card time-lab-result-card--empty ink-card">
                <p className="time-lab-page__eyebrow">Live engine unavailable</p>
                <h3>The horizon model is carrying this query alone.</h3>
                <p>
                  This request sits outside Parva&apos;s live conversion window, so the frontend stays in experimental projection mode.
                </p>
              </article>
            )}

            <article className="time-lab-result-card time-lab-result-card--projected ink-card">
              <p className="time-lab-page__eyebrow">Experimental horizon answer</p>
              <h3>{formatOutputCoordinate(result.experimental.output)}</h3>
              <p>
                Anchored to BS 2083 / April 14, 2026, then extended with the repeating synthetic BS cadence used for the long-range mirror.
              </p>
              <dl>
                <div>
                  <dt>Model</dt>
                  <dd>{result.experimental.model}</dd>
                </div>
                <div>
                  <dt>Target era</dt>
                  <dd>{formatHistoricalYear(result.experimental.output.year, result.experimental.output.era)}</dd>
                </div>
                <div>
                  <dt>Month span</dt>
                  <dd>{result.experimental.output.monthName}</dd>
                </div>
              </dl>
            </article>

            <article className="time-lab-result-card time-lab-result-card--ledger ink-card">
              <p className="time-lab-page__eyebrow">Chronology ledger</p>
              <h3>{result.query.system === 'gregorian' ? 'Gregorian to BS bridge' : 'BS to Gregorian bridge'}</h3>
              <p>
                This view keeps the lab honest about which system came in, which system came out, and whether the live engine could still be consulted.
              </p>
              <dl>
                <div>
                  <dt>Input coordinate</dt>
                  <dd>{formatInputSignature(result.query)}</dd>
                </div>
                <div>
                  <dt>Primary output</dt>
                  <dd>{formatOutputCoordinate(primaryResult)}</dd>
                </div>
                <div>
                  <dt>Target system</dt>
                  <dd>{systemCopy(result.query.system === 'gregorian' ? 'bs' : 'gregorian')}</dd>
                </div>
                <div>
                  <dt>Mirror mode</dt>
                  <dd>{result.anchored ? 'Live answer with projected mirror' : 'Projected mirror only'}</dd>
                </div>
                <div>
                  <dt>Support posture</dt>
                  <dd>{supportPosture(result.horizon)}</dd>
                </div>
                <div>
                  <dt>Projection model</dt>
                  <dd>{result.experimental.model}</dd>
                </div>
              </dl>
            </article>
          </div>
        </section>
      ) : null}

      <section className="time-lab-notes">
        <article className="time-lab-note ink-card">
          <p className="time-lab-page__eyebrow">Why it feels infinite</p>
          <h3>Signed years stay valid on the frontend.</h3>
          <p>
            The lab accepts BC, AD, BS, and Pre-BS year coordinates without collapsing back to a narrow year picker, so 10,000 BC and 10,000 BS both stay navigable.
          </p>
        </article>

        <article className="time-lab-note ink-card">
          <p className="time-lab-page__eyebrow">Where the truth line is</p>
          <h3>Live engine first, projection second.</h3>
          <p>
            Inside the live engine window, this page asks Parva for a real answer. Outside it, the horizon panel remains explicit that the result is experimental and synthetic.
          </p>
        </article>

        <article className="time-lab-note ink-card">
          <p className="time-lab-page__eyebrow">Next jump</p>
          <h3>Need the canonical monthly view instead?</h3>
          <p>
            Use this as a deep-time converter, then move back into the main calendar flows when you want festival, panchanga, or daily context.
          </p>
          <Link className="btn btn-secondary btn-sm" to="/today">Return to Today</Link>
        </article>
      </section>
    </section>
  );
}

export default TimeLabPage;
