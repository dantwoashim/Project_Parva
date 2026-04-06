import { EvidenceDrawer } from '../components/UI/EvidenceDrawer';
import { KundaliGraph } from '../components/KundaliGraph/KundaliGraph';
import { titleCase } from './kundali/kundaliFormState';
import { useKundaliState } from './kundali/useKundaliState';
import './KundaliPage.css';

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
  const {
    form,
    setForm,
    advancedOpen,
    setAdvancedOpen,
    searchResults,
    searchLoading,
    searchError,
    searchAttribution,
    submitError,
    loading,
    payload,
    graphPayload,
    graphMeta,
    selectedNode,
    setSelectedNode,
    activeTab,
    setActiveTab,
    submittedInput,
    signature,
    thesis,
    insightHighlights,
    focus,
    handlePlaceSearch,
    applyPlace,
    handleGenerate,
    handleSaveReading,
  } = useKundaliState();

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
