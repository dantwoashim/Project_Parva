import { useMemo, useState } from 'react';
import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { KundaliGraph } from '../components/KundaliGraph/KundaliGraph';
import { useMemberContext } from '../context/useMemberContext';
import { placesAPI, kundaliAPI } from '../services/api';
import { describeSupportError } from '../services/errorFormatting';
import {
  buildChartFocus,
  buildInsightHighlights,
  buildSignature,
  buildThesis,
} from './kundali/kundaliPresentation';
import './KundaliPage.css';

function titleCase(value) {
  return String(value || '')
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (char) => char.toUpperCase());
}

function buildBirthDateIso(form) {
  const year = Number(form.birthYear);
  const month = Number(form.birthMonth);
  const day = Number(form.birthDay);
  if (!Number.isInteger(year) || !Number.isInteger(month) || !Number.isInteger(day)) return null;
  const date = new Date(Date.UTC(year, month - 1, day));
  if (
    Number.isNaN(date.valueOf())
    || date.getUTCFullYear() !== year
    || date.getUTCMonth() !== month - 1
    || date.getUTCDate() !== day
  ) {
    return null;
  }
  return `${String(year).padStart(4, '0')}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

function resolveBirthInput(form) {
  const birthDate = buildBirthDateIso(form);
  const errors = [];

  if (!birthDate) {
    errors.push('Enter a valid birth date.');
  }
  if (!/^\d{2}:\d{2}$/.test(form.birthTime || '')) {
    errors.push('Enter an exact birth time.');
  }

  const latitude = Number(form.latitude);
  const longitude = Number(form.longitude);
  if (!Number.isFinite(latitude) || !Number.isFinite(longitude)) {
    errors.push('Select a birth place or enter valid coordinates.');
  }
  if (!String(form.timezone || '').trim()) {
    errors.push('Choose a timezone for the birth place.');
  }
  if (!String(form.placeQuery || '').trim()) {
    errors.push('Search and select a birth place.');
  }

  if (errors.length) {
    return {
      errors,
      value: null,
    };
  }

  return {
    errors: [],
    value: {
      date: birthDate,
      time: form.birthTime,
      datetime: `${birthDate}T${form.birthTime}:00`,
      latitude,
      longitude,
      timezone: form.timezone.trim(),
      placeLabel: form.placeQuery.trim(),
    },
  };
}

function buildSavedReading(resolvedInput, payload) {
  return {
    id: `kundali:${resolvedInput.datetime}:${resolvedInput.latitude}:${resolvedInput.longitude}:${resolvedInput.timezone}`,
    title: `Birth reading | ${resolvedInput.placeLabel}`,
    datetime: resolvedInput.datetime,
    placeLabel: resolvedInput.placeLabel,
    location: {
      latitude: resolvedInput.latitude,
      longitude: resolvedInput.longitude,
      timezone: resolvedInput.timezone,
    },
    lagna: payload?.lagna?.rashi_english || null,
    moon: payload?.grahas?.moon?.rashi_english || null,
    createdAt: new Date().toISOString(),
  };
}

function PlacementsTab({ payload, selectedNode, onSelectNode }) {
  const grahaRows = Object.entries(payload?.grahas || {});
  const houses = payload?.houses || [];

  return (
    <div className="kundali-reset__tab-grid">
      <article className="kundali-reset__panel">
        <div className="kundali-reset__panel-head">
          <p className="kundali-reset__eyebrow">Planetary placements</p>
          <h3>Grahas by sign</h3>
        </div>
        <div className="kundali-reset__table-wrap">
          <table className="kundali-reset__table">
            <thead>
              <tr>
                <th>Graha</th>
                <th>Sign</th>
                <th>Degree</th>
                <th>Dignity</th>
              </tr>
            </thead>
            <tbody>
              {grahaRows.map(([id, graha]) => (
                <tr key={id}>
                  <td>
                    <button type="button" className="kundali-reset__inline-link" onClick={() => onSelectNode(id)}>
                      {graha.name_english}
                    </button>
                  </td>
                  <td>{graha.rashi_english}</td>
                  <td>{Number(graha.longitude).toFixed(1)} deg</td>
                  <td>{titleCase(graha?.dignity?.state || 'neutral')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </article>

      <article className="kundali-reset__panel">
        <div className="kundali-reset__panel-head">
          <p className="kundali-reset__eyebrow">House placements</p>
          <h3>Twelve fixed houses</h3>
        </div>
        <div className="kundali-reset__houses-grid">
          {houses.map((house) => {
            const isSelected = selectedNode === `house_${house.house_number}`;
            return (
              <button
                key={house.house_number}
                type="button"
                className={`kundali-reset__house-card ${isSelected ? 'is-selected' : ''}`.trim()}
                onClick={() => onSelectNode(isSelected ? null : `house_${house.house_number}`)}
              >
                <span>House {house.house_number}</span>
                <strong>{house.rashi_english}</strong>
                <small>{house.occupants?.length ? house.occupants.map((item) => titleCase(item)).join(', ') : 'No grahas in this house'}</small>
              </button>
            );
          })}
        </div>
      </article>
    </div>
  );
}

function AspectsTab({ payload }) {
  const aspects = payload?.aspects || [];
  if (!aspects.length) {
    return (
      <article className="kundali-reset__panel">
        <div className="kundali-reset__panel-head">
          <p className="kundali-reset__eyebrow">Aspect structure</p>
          <h3>No aspect detail returned</h3>
        </div>
      </article>
    );
  }

  return (
    <div className="kundali-reset__aspect-grid">
      {aspects.map((aspect, index) => (
        <article key={`${aspect.from}-${aspect.to}-${index}`} className="kundali-reset__aspect-card">
          <span>{titleCase(aspect.nature || 'aspect')}</span>
          <strong>{titleCase(aspect.from)} to {titleCase(aspect.to)}</strong>
          <p>House {aspect.aspect_house} | Angle {aspect.aspect_angle} deg | Strength {Number(aspect.strength || 0).toFixed(2)}</p>
        </article>
      ))}
    </div>
  );
}

export function KundaliPage() {
  const { saveReading } = useMemberContext();
  const [form, setForm] = useState({
    birthDay: '',
    birthMonth: '',
    birthYear: '',
    birthTime: '',
    placeQuery: '',
    latitude: '',
    longitude: '',
    timezone: '',
  });
  const [advancedOpen, setAdvancedOpen] = useState(false);
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState('');
  const [searchAttribution, setSearchAttribution] = useState('');
  const [submitError, setSubmitError] = useState('');
  const [loading, setLoading] = useState(false);
  const [payload, setPayload] = useState(null);
  const [graphPayload, setGraphPayload] = useState(null);
  const [graphMeta, setGraphMeta] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [activeTab, setActiveTab] = useState('chart');
  const [submittedInput, setSubmittedInput] = useState(null);

  const resolvedInput = useMemo(() => resolveBirthInput(form), [form]);
  const signature = useMemo(() => buildSignature(payload), [payload]);
  const thesis = useMemo(() => buildThesis(payload, graphPayload), [graphPayload, payload]);
  const insightHighlights = useMemo(() => buildInsightHighlights(payload, graphPayload), [graphPayload, payload]);
  const focusPayload = useMemo(
    () => ({
      ...payload,
      houses: graphPayload?.layout?.house_nodes || payload?.houses || [],
      grahas: payload?.grahas || {},
    }),
    [graphPayload, payload],
  );
  const focus = useMemo(() => buildChartFocus(selectedNode, focusPayload), [focusPayload, selectedNode]);

  const handlePlaceSearch = async (event) => {
    event.preventDefault();
    setSearchLoading(true);
    setSearchError('');

    try {
      const response = await placesAPI.search({ query: form.placeQuery, limit: 5 });
      setSearchResults(response.items || []);
      setSearchAttribution(response.attribution || '');
      if (!(response.items || []).length) {
        setSearchError('No matching places were found. Try a city, district, or country.');
      }
    } catch (error) {
      setSearchResults([]);
      setSearchAttribution('');
      setSearchError(describeSupportError(error, 'Place search is unavailable right now.'));
    } finally {
      setSearchLoading(false);
    }
  };

  const applyPlace = (item) => {
    setForm((current) => ({
      ...current,
      placeQuery: item.label,
      latitude: String(item.latitude),
      longitude: String(item.longitude),
      timezone: item.timezone,
    }));
    setSearchResults([]);
    setSearchError('');
  };

  const handleGenerate = async (event) => {
    event.preventDefault();

    if (resolvedInput.errors.length || !resolvedInput.value) {
      setSubmitError(resolvedInput.errors[0] || 'Enter complete birth details before generating the chart.');
      return;
    }

    setLoading(true);
    setSubmitError('');

    try {
      const nextInput = resolvedInput.value;
      const [kundali, graphEnvelope] = await Promise.all([
        kundaliAPI.getKundali({
          datetime: nextInput.datetime,
          lat: nextInput.latitude,
          lon: nextInput.longitude,
          tz: nextInput.timezone,
        }),
        kundaliAPI.getGraphEnvelope({
          datetime: nextInput.datetime,
          lat: nextInput.latitude,
          lon: nextInput.longitude,
          tz: nextInput.timezone,
        }),
      ]);

      setPayload(kundali);
      setGraphPayload(graphEnvelope.data || null);
      setGraphMeta(graphEnvelope.meta || null);
      setSelectedNode(null);
      setActiveTab('chart');
      setSubmittedInput(nextInput);
    } catch (error) {
      setPayload(null);
      setGraphPayload(null);
      setGraphMeta(null);
      setSubmittedInput(null);
      setSubmitError(describeSupportError(error, 'Birth chart generation failed.'));
    } finally {
      setLoading(false);
    }
  };

  const handleSaveReading = async () => {
    if (!submittedInput || !payload) return;
    await saveReading(buildSavedReading(submittedInput, payload));
  };

  return (
    <section className="kundali-reset animate-fade-in-up consumer-route consumer-route--analysis">
      <header className="kundali-reset__hero">
        <div>
          <p className="kundali-reset__eyebrow">Birth Reading</p>
          <h1>Enter the birth details first.</h1>
          <p className="kundali-reset__intro">
            Generate the natal chart from the actual birth date, exact time, and birth place. The reading starts with ascendant, moon placement, and the strongest graha.
          </p>
        </div>
      </header>

      <div className="kundali-reset__layout">
        <form className="kundali-reset__form-card" onSubmit={handleGenerate}>
          <div className="kundali-reset__section-head">
            <div>
              <p className="kundali-reset__eyebrow">Birth details</p>
              <h2>Required inputs</h2>
            </div>
          </div>

          <div className="kundali-reset__date-grid">
            <label className="ink-input">
              <span>Day</span>
              <input
                inputMode="numeric"
                value={form.birthDay}
                onChange={(event) => setForm((current) => ({ ...current, birthDay: event.target.value }))}
              />
            </label>
            <label className="ink-input">
              <span>Month</span>
              <input
                inputMode="numeric"
                value={form.birthMonth}
                onChange={(event) => setForm((current) => ({ ...current, birthMonth: event.target.value }))}
              />
            </label>
            <label className="ink-input">
              <span>Year</span>
              <input
                inputMode="numeric"
                value={form.birthYear}
                onChange={(event) => setForm((current) => ({ ...current, birthYear: event.target.value }))}
              />
            </label>
            <label className="ink-input">
              <span>Birth time</span>
              <input
                type="time"
                value={form.birthTime}
                onChange={(event) => setForm((current) => ({ ...current, birthTime: event.target.value }))}
              />
            </label>
          </div>

          <div className="kundali-reset__place-block">
            <div className="kundali-reset__section-head">
              <div>
                <p className="kundali-reset__eyebrow">Birth place</p>
                <h2>Search and select</h2>
              </div>
            </div>

            <div className="kundali-reset__place-search">
              <label className="ink-input kundali-reset__place-input">
                <span>Place</span>
                <input
                  type="search"
                  value={form.placeQuery}
                  onChange={(event) => setForm((current) => ({ ...current, placeQuery: event.target.value }))}
                  placeholder="Kathmandu, Nepal"
                />
              </label>
              <button type="button" className="btn btn-secondary" onClick={handlePlaceSearch} disabled={searchLoading}>
                {searchLoading ? 'Searching...' : 'Search place'}
              </button>
            </div>

            {searchError ? <p className="kundali-reset__status" role="status">{searchError}</p> : null}
            {searchResults.length ? (
              <div className="kundali-reset__search-results">
                {searchResults.map((item) => (
                  <button key={`${item.label}-${item.latitude}-${item.longitude}`} type="button" className="kundali-reset__search-result" onClick={() => applyPlace(item)}>
                    <strong>{item.label}</strong>
                    <span>{item.timezone}</span>
                  </button>
                ))}
              </div>
            ) : null}
            {searchAttribution ? <p className="kundali-reset__attribution">{searchAttribution}</p> : null}

            <button type="button" className="kundali-reset__advanced-toggle" onClick={() => setAdvancedOpen((value) => !value)}>
              {advancedOpen ? 'Hide manual coordinates' : 'Show manual coordinates'}
            </button>

            {advancedOpen ? (
              <div className="kundali-reset__advanced-grid">
                <label className="ink-input">
                  <span>Latitude</span>
                  <input
                    inputMode="decimal"
                    value={form.latitude}
                    onChange={(event) => setForm((current) => ({ ...current, latitude: event.target.value }))}
                  />
                </label>
                <label className="ink-input">
                  <span>Longitude</span>
                  <input
                    inputMode="decimal"
                    value={form.longitude}
                    onChange={(event) => setForm((current) => ({ ...current, longitude: event.target.value }))}
                  />
                </label>
                <label className="ink-input">
                  <span>Timezone</span>
                  <input
                    value={form.timezone}
                    onChange={(event) => setForm((current) => ({ ...current, timezone: event.target.value }))}
                    placeholder="Asia/Kathmandu"
                  />
                </label>
              </div>
            ) : null}
          </div>

          {submitError ? <p className="kundali-reset__error" role="alert">{submitError}</p> : null}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? 'Generating chart...' : 'Generate chart'}
          </button>
        </form>

        <aside className="kundali-reset__anchors">
          <article className="kundali-reset__anchor-card">
            <p className="kundali-reset__eyebrow">Reading flow</p>
            <h2>Three anchors, then detail.</h2>
            <p>Start with the ascendant, then moon placement, then the strongest graha. After that, open houses or aspects only when you need more structure.</p>
          </article>
          {signature.map((item) => (
            <article key={item.label} className="kundali-reset__anchor-card">
              <span>{item.label}</span>
              <strong>{item.value}</strong>
            </article>
          ))}
        </aside>
      </div>

      {payload && graphPayload && submittedInput ? (
        <section className="kundali-reset__results">
          <div className="kundali-reset__results-head">
            <div>
              <p className="kundali-reset__eyebrow">Generated chart</p>
              <h2>{submittedInput.placeLabel}</h2>
              <p>{submittedInput.date} at {submittedInput.time} | {submittedInput.timezone}</p>
            </div>
            <div className="kundali-reset__results-actions">
              <button type="button" className="btn btn-secondary" onClick={handleSaveReading}>Save reading</button>
              <EvidenceDrawer
                title="Birth Reading"
                intro="This birth chart is computed from the submitted birth datetime and place."
                methodRef={graphMeta?.method || payload?.method || 'Kundali profile'}
                confidenceNote={graphMeta?.confidence?.level || payload?.confidence || 'Computed guidance'}
                placeUsed={submittedInput.placeLabel}
                computedForDate={submittedInput.datetime}
                availability={[
                  { label: 'North Indian chart', available: Boolean(graphPayload?.layout), note: 'The house grid stays fixed so the reading starts from the actual natal structure.' },
                  { label: 'Placements', available: Boolean(Object.keys(payload?.grahas || {}).length), note: 'Every graha placement is available in the placements tab.' },
                  { label: 'Aspects', available: Boolean(payload?.aspects?.length), note: 'Aspect links stay separate from the opening chart so the first read remains clear.' },
                ]}
                meta={graphMeta || payload}
                traceFallbackId={graphPayload?.calculation_trace_id || payload?.calculation_trace_id}
              />
            </div>
          </div>

          <div className="kundali-reset__thesis-card">
            <p className="kundali-reset__eyebrow">Opening read</p>
            <h3>{focus.title}</h3>
            <p>{selectedNode ? focus.body : thesis}</p>
            <small>{selectedNode ? focus.note : 'Select a house or graha to tighten the reading.'}</small>
          </div>

          <div className="kundali-reset__tabs" role="tablist" aria-label="Birth reading sections">
            {[
              { id: 'chart', label: 'Chart' },
              { id: 'placements', label: 'Placements' },
              { id: 'aspects', label: 'Aspects' },
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                id={`kundali-tab-${tab.id}`}
                role="tab"
                className={`kundali-reset__tab ${activeTab === tab.id ? 'is-active' : ''}`.trim()}
                aria-controls={`kundali-panel-${tab.id}`}
                aria-selected={activeTab === tab.id}
                tabIndex={activeTab === tab.id ? 0 : -1}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === 'chart' ? (
            <div
              id="kundali-panel-chart"
              role="tabpanel"
              aria-labelledby="kundali-tab-chart"
              className="kundali-reset__chart-grid"
            >
              <article className="kundali-reset__panel">
                <KundaliGraph payload={{ ...(graphPayload || {}), grahas: payload?.grahas || {}, houses: payload?.houses || [] }} selectedNode={selectedNode} onSelectNode={setSelectedNode} />
              </article>

              <aside className="kundali-reset__side-reading">
                <article className="kundali-reset__panel">
                  <div className="kundali-reset__panel-head">
                    <p className="kundali-reset__eyebrow">{focus.eyebrow}</p>
                    <h3>{focus.title}</h3>
                  </div>
                  <p>{focus.body}</p>
                  <small>{focus.note}</small>
                </article>

                <article className="kundali-reset__panel">
                  <div className="kundali-reset__panel-head">
                    <p className="kundali-reset__eyebrow">Primary anchors</p>
                    <h3>Where to start reading</h3>
                  </div>
                  <div className="kundali-reset__anchor-list">
                    {signature.map((item) => (
                      <div key={item.label}>
                        <span>{item.label}</span>
                        <strong>{item.value}</strong>
                      </div>
                    ))}
                  </div>
                </article>

                {insightHighlights.length ? (
                  <article className="kundali-reset__panel">
                    <div className="kundali-reset__panel-head">
                      <p className="kundali-reset__eyebrow">Interpretive signals</p>
                      <h3>Three useful highlights</h3>
                    </div>
                    <div className="kundali-reset__highlight-list">
                      {insightHighlights.map((item) => (
                        <div key={item.id}>
                          <strong>{item.title}</strong>
                          <p>{item.summary}</p>
                        </div>
                      ))}
                    </div>
                  </article>
                ) : null}
              </aside>
            </div>
          ) : null}

          {activeTab === 'placements' ? (
            <div
              id="kundali-panel-placements"
              role="tabpanel"
              aria-labelledby="kundali-tab-placements"
            >
              <PlacementsTab payload={payload} selectedNode={selectedNode} onSelectNode={setSelectedNode} />
            </div>
          ) : null}

          {activeTab === 'aspects' ? (
            <div
              id="kundali-panel-aspects"
              role="tabpanel"
              aria-labelledby="kundali-tab-aspects"
            >
              <AspectsTab payload={payload} />
            </div>
          ) : null}
        </section>
      ) : null}
    </section>
  );
}

export default KundaliPage;
