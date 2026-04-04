import { useDeferredValue, useEffect, useMemo, useState, useTransition } from 'react';
import { Link } from 'react-router-dom';
import { useTemporalContext } from '../context/useTemporalContext';
import { todayIso } from '../context/temporalContextState';
import {
  BS_MONTHS,
  GREGORIAN_MONTHS,
  buildExperimentalConversion,
  buildHorizonDescriptor,
  daysInGregorianMonth,
  daysInProjectedBsMonth,
  formatBsCoordinate,
  formatGregorianCoordinate,
  formatHistoricalYear,
  formatInputSignature,
  gregorianToJdn,
  historicalYearToAstronomical,
  parseGregorianIso,
  projectedBsToJdn,
} from '../lib/chronologyProjection';
import { calendarAPI } from '../services/api';
import './TimeLabPage.css';

const DEFAULT_GREGORIAN_ERA = 'AD';
const DEFAULT_BS_ERA = 'BS';
const HORIZON_ORDER = ['authoritative', 'estimated', 'experimental', 'deep_time'];

function buildDefaultQuery(dateIso) {
  const match = String(dateIso || '').match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) {
    return {
      system: 'gregorian',
      era: DEFAULT_GREGORIAN_ERA,
      year: '2026',
      month: 4,
      day: 14,
    };
  }

  return {
    system: 'gregorian',
    era: DEFAULT_GREGORIAN_ERA,
    year: String(Number(match[1])),
    month: Number(match[2]),
    day: Number(match[3]),
  };
}

function apiGregorianIso(query) {
  return `${String(query.year).padStart(4, '0')}-${String(query.month).padStart(2, '0')}-${String(query.day).padStart(2, '0')}`;
}

function parseQuery(query) {
  const normalizedYear = String(query.year || '').replace(/,/g, '').trim();
  if (!normalizedYear) {
    throw new Error('Enter a year before running the conversion.');
  }

  const year = Number(normalizedYear);
  if (!Number.isInteger(year) || year < 1) {
    throw new Error('Year must be a whole number greater than 0.');
  }

  const month = Number(query.month);
  const day = Number(query.day);
  if (!Number.isInteger(month) || month < 1 || month > 12) {
    throw new Error('Month must be between 1 and 12.');
  }
  if (!Number.isInteger(day) || day < 1) {
    throw new Error('Day must be a whole number greater than 0.');
  }

  if (query.system === 'gregorian') {
    return {
      system: 'gregorian',
      era: query.era === 'BC' ? 'BC' : 'AD',
      year,
      month,
      day,
    };
  }

  return {
    system: 'bs',
    era: query.era === 'PRE_BS' ? 'PRE_BS' : 'BS',
    year,
    month,
    day,
  };
}

function dayLimitForQuery(query) {
  try {
    const parsed = parseQuery({ ...query, day: 1 });
    const astronomicalYear = historicalYearToAstronomical(parsed.year, parsed.era);
    if (parsed.system === 'gregorian') {
      return daysInGregorianMonth(astronomicalYear, parsed.month);
    }
    return daysInProjectedBsMonth(astronomicalYear, parsed.month);
  } catch {
    return query.system === 'gregorian' ? 31 : 32;
  }
}

function formatOutputCoordinate(result) {
  if (!result) return '';
  return result.calendar === 'gregorian'
    ? formatGregorianCoordinate(result)
    : formatBsCoordinate(result);
}

function buildPresetCatalog(todayQuery) {
  return [
    {
      id: 'today',
      label: 'Parva today',
      detail: 'Current live date from the app context.',
      query: todayQuery,
    },
    {
      id: 'bc10000',
      label: '10,000 BC',
      detail: 'Deep prehistory, projected only.',
      query: { system: 'gregorian', era: 'BC', year: '10000', month: 1, day: 1 },
    },
    {
      id: 'ad10000',
      label: '10,000 AD',
      detail: 'Far future, projected horizon.',
      query: { system: 'gregorian', era: 'AD', year: '10000', month: 1, day: 1 },
    },
    {
      id: 'bs2083',
      label: '2083 BS',
      detail: 'The live BS new year anchor.',
      query: { system: 'bs', era: 'BS', year: '2083', month: 1, day: 1 },
    },
    {
      id: 'bs10000',
      label: '10,000 BS',
      detail: 'Long-range BS projection.',
      query: { system: 'bs', era: 'BS', year: '10000', month: 1, day: 1 },
    },
  ];
}

async function resolveAnchoredConversion(query) {
  const horizon = buildHorizonDescriptor(query);
  const liveCapable = horizon.band === 'authoritative' || horizon.band === 'estimated';
  if (!liveCapable) {
    return null;
  }

  if (query.system === 'gregorian' && query.era === 'AD') {
    const iso = apiGregorianIso(query);
    const [convert, compare] = await Promise.all([
      calendarAPI.convertGregorian(iso),
      calendarAPI.compareGregorian(iso).catch(() => null),
    ]);
    return {
      system: 'gregorian_to_bs',
      confidence: convert?.bikram_sambat?.confidence || 'computed',
      sourceRange: convert?.bikram_sambat?.source_range || null,
      estimatedErrorDays: convert?.bikram_sambat?.estimated_error_days || null,
      comparison: compare,
      output: {
        calendar: 'bs',
        year: convert.bikram_sambat.year,
        era: 'BS',
        month: convert.bikram_sambat.month,
        day: convert.bikram_sambat.day,
        monthName: convert.bikram_sambat.month_name,
      },
    };
  }

  if (query.system === 'bs' && query.era === 'BS') {
    const convert = await calendarAPI.convertBsToGregorian({
      year: query.year,
      month: query.month,
      day: query.day,
    });
    return {
      system: 'bs_to_gregorian',
      confidence: convert?.bs?.confidence || 'computed',
      sourceRange: convert?.bs?.source_range || null,
      estimatedErrorDays: convert?.bs?.estimated_error_days || null,
      comparison: null,
      output: {
        calendar: 'gregorian',
        ...parseGregorianIso(convert.gregorian),
      },
    };
  }

  return null;
}

function computeDriftDays(experimental, anchored) {
  if (!experimental?.output || !anchored?.output) return null;

  if (anchored.output.calendar === 'gregorian') {
    const experimentalYear = historicalYearToAstronomical(experimental.output.year, experimental.output.era);
    const anchoredYear = historicalYearToAstronomical(anchored.output.year, anchored.output.era);
    return Math.abs(
      gregorianToJdn(experimentalYear, experimental.output.month, experimental.output.day)
      - gregorianToJdn(anchoredYear, anchored.output.month, anchored.output.day),
    );
  }

  const experimentalYear = historicalYearToAstronomical(experimental.output.year, experimental.output.era);
  const anchoredYear = historicalYearToAstronomical(anchored.output.year, anchored.output.era);
  return Math.abs(
    projectedBsToJdn(experimentalYear, experimental.output.month, experimental.output.day)
    - projectedBsToJdn(anchoredYear, anchored.output.month, anchored.output.day),
  );
}

function engineLabel(confidence) {
  if (confidence === 'official' || confidence === 'exact') return 'Live authoritative engine';
  if (confidence === 'estimated') return 'Live estimated engine';
  return 'Experimental horizon engine';
}

function systemCopy(system) {
  return system === 'gregorian' ? 'Gregorian' : 'Bikram Sambat';
}

function modeSummary(result) {
  if (!result) return 'Awaiting lock';
  return result.anchored ? 'Blended live + projected mode' : 'Projected deep-time mode';
}

function supportPosture(horizon) {
  if (!horizon) return 'Unknown';
  if (horizon.band === 'authoritative') return 'Source-backed live window';
  if (horizon.band === 'estimated') return 'Estimated live window';
  if (horizon.band === 'experimental') return 'Frontend projection window';
  return 'Deep-time speculative window';
}

export function TimeLabPage() {
  const { state } = useTemporalContext();
  const todayQuery = useMemo(() => buildDefaultQuery(todayIso(state.timezone)), [state.timezone]);
  const initialQuery = todayQuery;
  const [draft, setDraft] = useState(initialQuery);
  const [activeQuery, setActiveQuery] = useState(initialQuery);
  const [isPresetPending, startPresetTransition] = useTransition();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const deferredDraft = useDeferredValue(draft);

  const presets = useMemo(() => buildPresetCatalog(initialQuery), [initialQuery]);
  const draftHorizon = useMemo(() => buildHorizonDescriptor(deferredDraft), [deferredDraft]);
  const dayLimit = useMemo(() => dayLimitForQuery(draft), [draft]);
  const signature = useMemo(() => formatInputSignature(deferredDraft), [deferredDraft]);

  useEffect(() => {
    let cancelled = false;

    async function run() {
      setLoading(true);
      setError(null);
      try {
        const normalized = parseQuery(activeQuery);
        const experimental = buildExperimentalConversion(normalized);
        const anchored = await resolveAnchoredConversion(normalized);
        if (cancelled) return;
        setResult({
          query: normalized,
          horizon: buildHorizonDescriptor(normalized),
          experimental,
          anchored,
          driftDays: computeDriftDays(experimental, anchored),
        });
      } catch (nextError) {
        if (!cancelled) {
          setResult(null);
          setError(nextError?.message || 'The conversion engine could not stabilize this request.');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void run();
    return () => {
      cancelled = true;
    };
  }, [activeQuery]);

  function patchDraft(patch) {
    setDraft((current) => {
      const next = { ...current, ...patch };
      const nextLimit = dayLimitForQuery(next);
      if (next.day > nextLimit) {
        next.day = nextLimit;
      }
      return next;
    });
  }

  function submitCurrentDraft(event) {
    event?.preventDefault?.();
    try {
      const normalized = parseQuery(draft);
      setActiveQuery(normalized);
    } catch (nextError) {
      setError(nextError?.message || 'The conversion engine could not stabilize this request.');
    }
  }

  function applyPreset(query) {
    startPresetTransition(() => {
      setDraft(query);
      setActiveQuery(query);
    });
  }

  function resetToToday() {
    setError(null);
    applyPreset(todayQuery);
  }

  const primaryResult = result?.anchored?.output || result?.experimental?.output || null;
  const primaryEngine = result?.anchored ? engineLabel(result.anchored.confidence) : 'Experimental horizon engine';
  const comparisonLabel = result?.anchored
    ? result.anchored.comparison?.match === true
      ? 'Official and estimated live paths agree on this date.'
      : result.anchored.comparison?.official && result.anchored.comparison?.estimated
        ? 'The live engine sees both an official and estimated track here.'
        : 'The live engine returned one stable answer for this query.'
    : 'No live engine path exists for this query, so the horizon model carries the entire result.';

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
