import {
  useEffect,
  useState,
  Link,
  kundaliAPI,
  placesAPI,
  useTemporalContext,
  describeSupportError,
  grahaShort,
  housePositions,
  readingTraits,
  sampleBirthProfile,
  signShort,
  formatCoordinates,
  formatDateTime,
  humanMethodLabel,
  readableCategory,
  supportReference,
  titleCase,
  Confidence,
  currentDasha,
  strongestGraha,
  d9Houses,
  AppChrome,
  PageHero,
} from './ExperienceCommon.jsx';

function KundaliChart({ payload, selected, onSelect, mode }) {
  const houses = mode === 'd9' ? d9Houses(payload) : payload?.houses || [];
  const grahas = payload?.grahas || {};
  const lagna = payload?.lagna?.rashi_english || 'Unknown';

  return (
    <figure className="sacred-chart" aria-label={`${mode === 'd9' ? 'Navamsha' : 'North Indian'} Kundali chart`}>
      <div className="chart-toolbar">
        <div>
          <span>{mode === 'd9' ? 'D9 Navamsha' : 'D1 Rashi'}</span>
          <strong>{mode === 'd9' ? 'Navamsha Chakra' : `${lagna} Janma Kundali`}</strong>
        </div>
        <small>Interactive chart - select a house or graha</small>
      </div>
      <div className="chart-canvas">
        <svg viewBox="0 0 100 100" className="chart-frame" aria-hidden="true">
          <defs>
            <filter id="kundaliShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feDropShadow dx="0" dy="4" stdDeviation="3" floodColor="#3b2a1b" floodOpacity="0.12" />
            </filter>
          </defs>
          <rect x="4.5" y="4.5" width="91" height="91" rx="8" fill="#fffaf0" filter="url(#kundaliShadow)" />
          <rect x="7.5" y="7.5" width="85" height="85" rx="5.5" fill="#f8f5ff" />
          <path className="chart-grid-major" d="M50 7.5 L92.5 50 L50 92.5 L7.5 50 Z" />
          <path className="chart-grid-major" d="M7.5 7.5 L50 50 L92.5 92.5" />
          <path className="chart-grid-major" d="M92.5 7.5 L50 50 L7.5 92.5" />
          <path className="chart-grid-minor" d="M50 7.5 L50 92.5" />
          <path className="chart-grid-minor" d="M7.5 50 L92.5 50" />
          <circle cx="50" cy="50" r="7.5" />
          <path className="chart-grid-faint" d="M50 16 L84 50 L50 84 L16 50 Z" />
        </svg>
        {houses.map((house) => {
          const position = housePositions[house.house_number] || { x: 50, y: 50 };
          const isActive = selected?.type === 'house' && selected.id === house.house_number;
          return (
            <article
              key={house.house_number}
              className={`chart-house ${isActive ? 'is-active' : ''} ${house.house_number === 1 ? 'is-lagna' : ''}`}
              style={{ '--x': `${position.x}%`, '--y': `${position.y}%` }}
            >
              <button type="button" onClick={() => onSelect({ type: 'house', id: house.house_number, house })}>
                <span>{house.house_number}</span>
                <strong>{signShort[house.rashi_english] || house.rashi_english || 'Sign'}</strong>
                {house.house_number === 1 && mode === 'd1' ? <em>Ascendant</em> : null}
              </button>
              {house.occupants?.length ? (
                <div className="chart-grahas">
                  {house.occupants.map((id) => {
                    const graha = grahas[id] || {};
                    const grahaActive = selected?.type === 'graha' && selected.id === id;
                    return (
                      <button
                        key={id}
                        type="button"
                        className={grahaActive ? 'is-active' : ''}
                        title={`${graha.name_english || titleCase(id)} in ${graha.rashi_english || house.rashi_english || 'sign'}`}
                        onClick={(event) => {
                          event.stopPropagation();
                          onSelect({ type: 'graha', id, graha });
                        }}
                      >
                        {grahaShort[id] || titleCase(id).slice(0, 2)}
                      </button>
                    );
                  })}
                </div>
              ) : null}
            </article>
          );
        })}
        <button type="button" className="chart-center" onClick={() => onSelect(null)}>
          <span>{mode === 'd9' ? 'Navamsha' : 'Lagna'}</span>
          <strong>{mode === 'd9' ? 'D9' : lagna}</strong>
          <small>{selected ? 'Clear focus' : 'Select to inspect'}</small>
        </button>
      </div>
    </figure>
  );
}

function ReadingBrief({ payload, selected }) {
  const moon = payload?.grahas?.moon;
  const lagna = payload?.lagna;
  const dominant = strongestGraha(payload);
  const dasha = currentDasha(payload?.dasha?.timeline || []);
  const focusTitle = selected?.type === 'graha'
    ? selected.graha?.name_english || titleCase(selected.id)
    : selected?.type === 'house'
      ? `House ${selected.id}`
      : 'Opening read';
  const focusBody = selected?.type === 'graha'
    ? `${selected.graha?.name_english || titleCase(selected.id)} is in ${selected.graha?.rashi_english || 'its sign'} at ${Number(selected.graha?.degree_in_rashi || 0).toFixed(2)} degrees, with ${selected.graha?.dignity?.state || 'neutral'} dignity.`
    : selected?.type === 'house'
      ? `House ${selected.id} opens through ${selected.house?.rashi_english || 'this sign'}${selected.house?.occupants?.length ? ` and contains ${selected.house.occupants.map(titleCase).join(', ')}.` : ' and has no listed graha occupants.'}`
      : `This chart begins with ${lagna?.rashi_english || 'unknown'} rising and Moon in ${moon?.rashi_english || 'unknown'}, giving the reading a ${readingTraits[lagna?.rashi_english] || 'layered'} outer rhythm.`;

  return (
    <aside className="panel birth-brief">
      <div className="panel-heading tight">
        <p className="eyebrow">{focusTitle}</p>
        <strong>{selected ? 'Focused detail' : 'Primary anchors'}</strong>
      </div>
      <p>{focusBody}</p>
      <div className="anchor-stack">
        <div><span>Lagna</span><strong>{lagna?.rashi_english || 'Pending'}</strong></div>
        <div><span>Moon</span><strong>{moon?.rashi_english || 'Pending'}</strong></div>
        <div><span>Strongest pull</span><strong>{dominant ? `${dominant.name_english} in ${dominant.rashi_english}` : 'Pending'}</strong></div>
        <div><span>Current dasha</span><strong>{dasha ? titleCase(dasha.lord) : 'Unavailable'}</strong></div>
      </div>
      <Confidence value={86} label="Calculation confidence" />
      <small className="reading-disclaimer">Informational astrology assistance. Birth time precision, timezone, ayanamsha, and tradition affect interpretation.</small>
    </aside>
  );
}

function PlanetTable({ payload, selected, onSelect }) {
  return (
    <section className="panel graha-table-card">
      <div className="panel-heading">
        <p className="eyebrow">Planetary placements</p>
        <strong>Grahas, signs, degrees, and dignity</strong>
      </div>
      <div className="graha-table-wrap">
        <table className="graha-table">
          <thead>
            <tr><th>Graha</th><th>Rashi</th><th>Degree</th><th>D9</th><th>Dignity</th></tr>
          </thead>
          <tbody>
            {Object.entries(payload?.grahas || {}).map(([id, graha]) => (
              <tr key={id} className={selected?.type === 'graha' && selected.id === id ? 'is-active' : undefined}>
                <td><button type="button" onClick={() => onSelect({ type: 'graha', id, graha })}>{graha.name_english || titleCase(id)}</button></td>
                <td>{graha.rashi_english}</td>
                <td>{Number(graha.degree_in_rashi || 0).toFixed(2)} deg</td>
                <td>{payload?.d9?.[id]?.navamsa_rashi_english || 'Not listed'}</td>
                <td>{titleCase(graha.dignity?.state || 'neutral')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

function DashaTimeline({ payload }) {
  const periods = payload?.dasha?.timeline || [];
  const active = currentDasha(periods);
  return (
    <section className="panel dasha-card">
      <div className="panel-heading">
        <p className="eyebrow">Vimshottari dasha</p>
        <strong>{active ? `${titleCase(active.lord)} period is active now` : 'Timeline unavailable'}</strong>
      </div>
      <div className="dasha-rail">
        {periods.slice(0, 7).map((period) => (
          <article key={`${period.lord}-${period.start}`} className={period === active ? 'is-active' : ''}>
            <span>{titleCase(period.lord)}</span>
            <strong>{formatDateTime(period.start)} to {formatDateTime(period.end)}</strong>
            <small>{period.duration_years} years</small>
          </article>
        ))}
      </div>
    </section>
  );
}

function CalculationTrace({ payload, graphPayload }) {
  return (
    <section className="panel trace-card">
      <div className="panel-heading">
        <p className="eyebrow">Verify calculation</p>
        <strong>{humanMethodLabel(payload?.method, 'Swiss Ephemeris sidereal')}</strong>
      </div>
      <div className="trace-grid">
        <div><span>Rule set</span><strong>{humanMethodLabel(payload?.assumption_set_id, 'Kundali rules')}</strong></div>
        <div><span>Evidence</span><strong>{supportReference(payload?.calculation_trace_id || graphPayload?.calculation_trace_id)}</strong></div>
        <div><span>Quality</span><strong>{readableCategory(payload?.quality_band || 'validated')}</strong></div>
        <div><span>Scope</span><strong>{readableCategory(payload?.advisory_scope || 'astrology assist')}</strong></div>
      </div>
      <p>Swiss Ephemeris-based sidereal placements are used for calculation. Interpretive labels remain tradition-dependent and should stay transparent.</p>
    </section>
  );
}

export function RedesignBirthReading() {
  const { state } = useTemporalContext();
  const [form, setForm] = useState({
    name: '',
    date: '',
    time: '',
    place: '',
    lat: state.location?.latitude || '',
    lon: state.location?.longitude || '',
    tz: state.timezone || 'Asia/Kathmandu',
  });
  const [placeOptions, setPlaceOptions] = useState([]);
  const [placeStatus, setPlaceStatus] = useState({ loading: false, error: '' });
  const [payload, setPayload] = useState(null);
  const [graphPayload, setGraphPayload] = useState(null);
  const [selected, setSelected] = useState(null);
  const [chartMode, setChartMode] = useState('d1');
  const [status, setStatus] = useState({ loading: false, error: '' });
  const update = (key, value) => setForm((current) => ({ ...current, [key]: value }));
  const missingFields = [
    ['date', 'Date of birth'],
    ['time', 'Exact birth time'],
    ['lat', 'Latitude'],
    ['lon', 'Longitude'],
    ['tz', 'Timezone'],
  ].filter(([key]) => !String(form[key] || '').trim());
  const canGenerate = missingFields.length === 0;
  const loadSample = () => {
    setForm(sampleBirthProfile);
    setPlaceOptions([]);
    setPlaceStatus({ loading: false, error: '' });
    setStatus({ loading: false, error: '' });
  };

  const applyPlace = (place) => {
    setForm((current) => ({
      ...current,
      place: place.label,
      lat: place.latitude,
      lon: place.longitude,
      tz: place.timezone,
    }));
  };

  useEffect(() => {
    const value = form.place.trim();
    if (value.length < 2) {
      return undefined;
    }
    let cancelled = false;
    const timeoutId = window.setTimeout(async () => {
      setPlaceStatus({ loading: true, error: '' });
      try {
        const payload = await placesAPI.search({ query: value, limit: 5 });
        if (!cancelled) {
          setPlaceOptions(payload.items || []);
          setPlaceStatus({ loading: false, error: '' });
        }
      } catch (error) {
        if (!cancelled) {
          setPlaceOptions([]);
          setPlaceStatus({ loading: false, error: describeSupportError(error, 'Birth place search failed.') });
        }
      }
    }, 250);
    return () => {
      cancelled = true;
      window.clearTimeout(timeoutId);
    };
  }, [form.place]);

  const generate = async (event) => {
    event.preventDefault();
    setStatus({ loading: true, error: '' });
    setSelected(null);
    try {
      const request = {
        datetime: `${form.date}T${form.time}:00`,
        lat: form.lat,
        lon: form.lon,
        tz: form.tz,
      };
      const [kundali, graphEnvelope] = await Promise.all([
        kundaliAPI.getKundali(request),
        kundaliAPI.getGraphEnvelope(request),
      ]);
      setPayload(kundali);
      setGraphPayload(graphEnvelope.data || null);
    } catch (error) {
      setPayload(null);
      setGraphPayload(null);
      setStatus({ loading: false, error: describeSupportError(error, 'Birth chart generation failed.') });
      return;
    }
    setStatus({ loading: false, error: '' });
  };

  return (
    <AppChrome>
      <main className="page-shell birth-page">
        <PageHero
          title="Birth Reading"
          body="Enter birth date, time, and place to generate a private Kundali with assumptions and limits visible."
          action={<div className="hero-actions"><button type="button" onClick={loadSample}>Load sample</button><Link to="/methodology">Read limits</Link></div>}
        />
        <section className="birth-trust-strip" aria-label="Birth Reading privacy and readiness">
          <div>
            <span>Privacy</span>
            <strong>Local session</strong>
            <small>No account is required to calculate.</small>
          </div>
          <div>
            <span>Required</span>
            <strong>{missingFields.length ? `${missingFields.length} missing` : 'Ready'}</strong>
            <small>{missingFields.map(([, label]) => label).join(', ') || 'All required fields are present.'}</small>
          </div>
          <div>
            <span>Interpretation</span>
            <strong>Advisory</strong>
            <small>Tradition, time precision, and timezone can change readings.</small>
          </div>
        </section>
        <section className="birth-workspace">
          <form className="panel birth-form" onSubmit={generate}>
            <div className="panel-heading tight">
              <p className="eyebrow">Create chart</p>
              <strong>Birth details</strong>
            </div>
            <div className="birth-stepper" aria-label="Birth Reading steps">
              <span className={form.date && form.time ? 'is-complete' : 'is-current'}>1 Details</span>
              <span className={form.place ? 'is-complete' : ''}>2 Place</span>
              <span className={canGenerate ? 'is-current' : ''}>3 Generate</span>
            </div>
            <label>Profile name<input value={form.name} onChange={(event) => update('name', event.target.value)} /></label>
            <label>Date of birth<input type="date" value={form.date} onChange={(event) => update('date', event.target.value)} /></label>
            <label>Exact birth time<input type="time" value={form.time} onChange={(event) => update('time', event.target.value)} /></label>
            <label>Birth place<input
              value={form.place}
              onChange={(event) => {
                update('place', event.target.value);
                if (event.target.value.trim().length < 2) {
                  setPlaceOptions([]);
                  setPlaceStatus({ loading: false, error: '' });
                }
              }}
              placeholder="Search places"
            /></label>
            <div className="place-result-strip">
              {placeStatus.loading ? <span>Searching...</span> : null}
              {placeStatus.error ? <span>{placeStatus.error}</span> : null}
              {placeOptions.map((place) => (
                <button key={`${place.label}-${place.latitude}`} type="button" onClick={() => applyPlace(place)}>
                  {place.label}
                  <small>{formatCoordinates(place)}</small>
                </button>
              ))}
            </div>
            <details className="advanced-birth-settings">
              <summary>Advanced calculation settings</summary>
              <div className="coordinate-grid">
                <label>Latitude<input value={form.lat} onChange={(event) => update('lat', event.target.value)} /></label>
                <label>Longitude<input value={form.lon} onChange={(event) => update('lon', event.target.value)} /></label>
              </div>
              <label>Timezone<input value={form.tz} onChange={(event) => update('tz', event.target.value)} /></label>
              <div className="method-strip">
                <span>Method</span>
                <strong>Lahiri-style sidereal / Swiss Ephemeris</strong>
                <small>Birth details stay in this browser session unless you choose to share or export them.</small>
              </div>
            </details>
            {missingFields.length ? (
              <div className="missing-field-list" role="status">
                <strong>Still needed</strong>
                {missingFields.map(([, label]) => <span key={label}>{label}</span>)}
              </div>
            ) : null}
            {status.error ? <p className="birth-error" role="alert">{status.error}</p> : null}
            <div className="birth-form-actions">
              <button type="submit" className="primary-button" disabled={status.loading || !canGenerate}>
              {status.loading ? 'Calculating Kundali...' : 'Generate Kundali'}
              </button>
              <button type="button" className="ghost-button" onClick={loadSample}>Preview sample</button>
            </div>
          </form>

          <section className="panel kundali-card" aria-label="Interactive Kundali chart">
            <div className="birth-chart-switch" role="tablist" aria-label="Chart type">
              <button type="button" className={chartMode === 'd1' ? 'is-active' : ''} onClick={() => setChartMode('d1')}>D1 Rashi</button>
              <button type="button" className={chartMode === 'd9' ? 'is-active' : ''} onClick={() => setChartMode('d9')}>D9 Navamsha</button>
            </div>
            {payload ? (
              <KundaliChart payload={payload} graphPayload={graphPayload} selected={selected} onSelect={setSelected} mode={chartMode} />
            ) : (
              <div className="chart-loading">
                <div className="sample-chart-preview" aria-hidden="true">
                  {Array.from({ length: 12 }, (_, index) => (
                    <span key={index}>{index + 1}</span>
                  ))}
                </div>
                <strong>{status.loading ? 'Calculating chart...' : 'Sample-ready chart preview'}</strong>
                <p>{canGenerate ? 'Generate the Kundali when ready.' : 'Complete the required fields or load the sample profile to see the finished state.'}</p>
                <button type="button" className="ghost-button" onClick={loadSample}>Load sample profile</button>
              </div>
            )}
          </section>

          {payload ? <ReadingBrief payload={payload} selected={selected} /> : (
            <aside className="panel birth-brief">
              <p className="eyebrow">Reading brief</p>
              <h2>{canGenerate ? 'Ready to calculate' : 'Complete the required fields'}</h2>
              <p>{canGenerate ? 'The interpretation will appear after the backend returns real chart data.' : `Needed: ${missingFields.map(([, label]) => label).join(', ')}.`}</p>
              <button type="button" className="ghost-button" onClick={loadSample}>Use sample details</button>
            </aside>
          )}
        </section>

        {payload ? (
          <section className="birth-analysis-grid">
            <PlanetTable payload={payload} selected={selected} onSelect={setSelected} />
            <DashaTimeline payload={payload} />
            <CalculationTrace payload={payload} graphPayload={graphPayload} />
          </section>
        ) : null}
      </main>
    </AppChrome>
  );
}

