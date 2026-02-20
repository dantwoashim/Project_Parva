import { useEffect, useMemo, useState } from 'react';
import { kundaliAPI } from '../services/api';
import './KundaliPage.css';

function defaultDateTime() {
  const now = new Date(Date.now());
  const yyyy = now.getFullYear();
  const mm = String(now.getMonth() + 1).padStart(2, '0');
  const dd = String(now.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}T06:30`;
}

function formatDignity(dignity) {
  if (!dignity || typeof dignity !== 'object') {
    return '—';
  }
  return `${dignity.state || 'neutral'} (${dignity.strength || 'moderate'})`;
}

export function KundaliPage() {
  const [datetimeLocal, setDatetimeLocal] = useState(defaultDateTime());
  const [lat, setLat] = useState('27.7172');
  const [lon, setLon] = useState('85.3240');
  const [tz, setTz] = useState('Asia/Kathmandu');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [payload, setPayload] = useState(null);

  const datetimeIso = useMemo(() => `${datetimeLocal}:00`, [datetimeLocal]);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await kundaliAPI.getKundali({ datetime: datetimeIso, lat, lon, tz });
      setPayload(data);
    } catch (err) {
      setPayload(null);
      setError(err.message || 'Failed to load kundali');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="kundali-page">
      <header className="glass-card kundali-page__header motion-stagger">
        <div>
          <h2 className="text-display">Kundali Studio</h2>
          <p>D1 + D9 charts, graha drishti, yoga-dosha markers, and Vimshottari maha + antar dasha.</p>
        </div>

        <form
          className="kundali-page__controls"
          onSubmit={(e) => {
            e.preventDefault();
            load();
          }}
        >
          <label>
            <span>Birth Datetime</span>
            <input type="datetime-local" value={datetimeLocal} onChange={(e) => setDatetimeLocal(e.target.value)} required />
          </label>
          <label>
            <span>Lat</span>
            <input value={lat} onChange={(e) => setLat(e.target.value)} />
          </label>
          <label>
            <span>Lon</span>
            <input value={lon} onChange={(e) => setLon(e.target.value)} />
          </label>
          <label>
            <span>Timezone</span>
            <input value={tz} onChange={(e) => setTz(e.target.value)} />
          </label>
          <button className="btn btn-primary btn-premium interactive-surface interactive-press" type="submit">Generate</button>
        </form>
      </header>

      {loading && (
        <div className="glass-card kundali-page__state motion-stagger">
          <h3>Computing graha and lagna positions...</h3>
          <div className="skeleton" style={{ height: '220px', marginTop: '1rem' }} />
        </div>
      )}

      {!loading && error && (
        <div className="glass-card kundali-page__state motion-stagger" role="alert">
          <h3>Unable to load kundali</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && payload && (
        <>
          <section className="kundali-page__top-grid">
            <article className="glass-card kundali-card interactive-surface motion-stagger">
              <h3>Lagna</h3>
              <p className="value">{payload.lagna?.rashi_english || '—'}</p>
              <p>{payload.lagna?.rashi_sanskrit || '—'} · House 1</p>
              <p className="meta">{payload.lagna?.longitude}°</p>
            </article>

            <article className="glass-card kundali-card interactive-surface motion-stagger">
              <h3>Analysis Summary</h3>
              <p><strong>Aspects:</strong> {payload.aspects?.length || 0}</p>
              <p><strong>Yogas:</strong> {payload.yogas?.length || 0}</p>
              <p><strong>Doshas:</strong> {payload.doshas?.length || 0}</p>
              <p><strong>Major Dashas:</strong> {payload.dasha?.total_major_periods || 0}</p>
            </article>

            <article className="glass-card kundali-card interactive-surface motion-stagger">
              <h3>Trace + Confidence</h3>
              <p><strong>Trace:</strong> {payload.calculation_trace_id || 'N/A'}</p>
              <p><strong>Confidence:</strong> {payload.confidence || 'computed'}</p>
              <p><strong>Method:</strong> {payload.method_profile || payload.method || 'kundali'}</p>
              <p><strong>Quality:</strong> {payload.quality_band || 'validated'}</p>
              <p><strong>Scope:</strong> {payload.advisory_scope || 'astrology_assist'}</p>
            </article>
          </section>

          <section className="glass-card kundali-table-card motion-stagger">
            <h3>Graha Positions + Dignity</h3>
            <table className="kundali-table">
              <thead>
                <tr>
                  <th>Graha</th>
                  <th>Rashi</th>
                  <th>Longitude</th>
                  <th>Dignity</th>
                  <th>Retrograde</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(payload.grahas || {}).map(([id, row]) => (
                  <tr key={id}>
                    <td>{row.name_sanskrit} ({row.name_english})</td>
                    <td>{row.rashi_english}</td>
                    <td>{row.longitude}°</td>
                    <td>{formatDignity(row.dignity)}</td>
                    <td>{row.is_retrograde ? 'Yes' : 'No'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="kundali-page__analysis-grid">
            <article className="glass-card kundali-aspects interactive-surface motion-stagger">
              <h3>Key Aspects (Drishti)</h3>
              <ul>
                {(payload.aspects || []).slice(0, 12).map((aspect) => (
                  <li key={`${aspect.from}-${aspect.to}-${aspect.aspect_degree}`}>
                    <strong>{aspect.from}</strong> → <strong>{aspect.to}</strong>
                    <span>{aspect.aspect_degree}° · orb {aspect.orb}° · strength {aspect.strength}</span>
                  </li>
                ))}
              </ul>
            </article>

            <article className="glass-card kundali-signals interactive-surface motion-stagger">
              <h3>Yogas + Doshas</h3>
              <div className="signal-block">
                <h4>Yogas</h4>
                {payload.yogas?.length ? (
                  <ul>
                    {payload.yogas.map((row) => (
                      <li key={row.id}><strong>{row.id}</strong>: {row.description}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No yoga marker in this profile.</p>
                )}
              </div>
              <div className="signal-block">
                <h4>Doshas</h4>
                {payload.doshas?.length ? (
                  <ul>
                    {payload.doshas.map((row) => (
                      <li key={row.id}><strong>{row.id}</strong>: {row.description}</li>
                    ))}
                  </ul>
                ) : (
                  <p>No dosha marker in this profile.</p>
                )}
              </div>
            </article>
          </section>

          <section className="kundali-page__bottom-grid">
            <article className="glass-card kundali-houses interactive-surface motion-stagger">
              <h3>12 Houses (Whole Sign)</h3>
              <div className="houses-grid">
                {(payload.houses || []).map((house) => (
                  <div key={house.house_number} className="house-cell">
                    <p className="house-num">House {house.house_number}</p>
                    <p>{house.rashi_english}</p>
                    <p className="house-occupants">{house.occupants?.length ? house.occupants.join(', ') : '—'}</p>
                  </div>
                ))}
              </div>
            </article>

            <article className="glass-card kundali-dasha interactive-surface motion-stagger">
              <h3>Maha + Antar Dasha</h3>
              <ul>
                {(payload.dasha?.timeline || []).slice(0, 5).map((d) => (
                  <li key={`${d.lord}-${d.start}`}>
                    <p><strong>{d.lord}</strong> · {d.start?.slice(0, 10)} → {d.end?.slice(0, 10)} ({d.duration_years}y)</p>
                    <p className="meta">
                      Antar: {(d.antar_dasha || []).slice(0, 3).map((antar) => antar.lord).join(', ')}
                    </p>
                  </li>
                ))}
              </ul>
            </article>
          </section>

          <section className="glass-card kundali-consistency interactive-surface motion-stagger">
            <h3>Consistency Checks</h3>
            <ul>
              {(payload.consistency_checks || []).map((check) => (
                <li key={check.id}>
                  <strong>{check.id}</strong>: {check.status} · {check.message}
                </li>
              ))}
            </ul>
          </section>

          {Array.isArray(payload.warnings) && payload.warnings.length > 0 && (
            <section className="glass-card kundali-page__warnings">
              <h3>Warnings</h3>
              <ul>
                {payload.warnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            </section>
          )}
        </>
      )}
    </section>
  );
}

export default KundaliPage;
