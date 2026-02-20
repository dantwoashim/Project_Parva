import { useEffect, useState } from 'react';
import { muhurtaAPI } from '../services/api';
import './MuhurtaPage.css';

function todayIso() {
  return new Date(Date.now()).toISOString().slice(0, 10);
}

export function MuhurtaPage() {
  const [date, setDate] = useState(todayIso());
  const [type, setType] = useState('general');
  const [lat, setLat] = useState('27.7172');
  const [lon, setLon] = useState('85.3240');
  const [tz, setTz] = useState('Asia/Kathmandu');
  const [birthNakshatra, setBirthNakshatra] = useState('');
  const [assumptionSet, setAssumptionSet] = useState('np-mainstream-v2');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dayData, setDayData] = useState(null);
  const [auspiciousData, setAuspiciousData] = useState(null);
  const [rahuData, setRahuData] = useState(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const [day, auspicious, rahu] = await Promise.all([
        muhurtaAPI.getDay({ date, lat, lon, tz, birthNakshatra }),
        muhurtaAPI.getAuspicious({ date, type, lat, lon, tz, birthNakshatra, assumptionSet }),
        muhurtaAPI.getRahuKalam({ date, lat, lon, tz }),
      ]);
      setDayData(day);
      setAuspiciousData(auspicious);
      setRahuData(rahu);
    } catch (err) {
      setDayData(null);
      setAuspiciousData(null);
      setRahuData(null);
      setError(err.message || 'Failed to load muhurta data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <section className="muhurta-page">
      <header className="glass-card muhurta-page__header">
        <div>
          <h2 className="text-display">Muhurta Finder</h2>
          <p>Day-night muhurtas with hora, chaughadia, and optional tara-bala scoring.</p>
        </div>
        <form
          className="muhurta-page__controls"
          onSubmit={(e) => {
            e.preventDefault();
            load();
          }}
        >
          <label>
            <span>Date</span>
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} required />
          </label>
          <label>
            <span>Ceremony</span>
            <select value={type} onChange={(e) => setType(e.target.value)}>
              <option value="general">General</option>
              <option value="vivah">Vivah</option>
              <option value="griha_pravesh">Griha Pravesh</option>
              <option value="travel">Travel</option>
              <option value="upanayana">Upanayana</option>
            </select>
          </label>
          <label>
            <span>Assumption Set</span>
            <select value={assumptionSet} onChange={(e) => setAssumptionSet(e.target.value)}>
              <option value="np-mainstream-v2">NP Mainstream</option>
              <option value="diaspora-practical-v2">Diaspora Practical</option>
            </select>
          </label>
          <label>
            <span>Birth Nakshatra (optional)</span>
            <input
              value={birthNakshatra}
              onChange={(e) => setBirthNakshatra(e.target.value)}
              placeholder="1-27 or name"
            />
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
          <button type="submit" className="btn btn-primary">Find Windows</button>
        </form>
      </header>

      {loading && (
        <div className="glass-card muhurta-page__state">
          <h3>Computing muhurta windows...</h3>
          <div className="skeleton" style={{ height: '180px', marginTop: '1rem' }} />
        </div>
      )}

      {!loading && error && (
        <div className="glass-card muhurta-page__state" role="alert">
          <h3>Unable to load muhurta windows</h3>
          <p>{error}</p>
        </div>
      )}

      {!loading && !error && dayData && auspiciousData && rahuData && (
        <>
          <section className="muhurta-page__hero-grid">
            <article className="glass-card muhurta-highlight">
              <h3>Best Window</h3>
              <p className="value">{auspiciousData.best_window?.name || '—'}</p>
              <p>{auspiciousData.best_window?.start || '—'} to {auspiciousData.best_window?.end || '—'}</p>
              <p className="meta">Score: {auspiciousData.best_window?.score ?? 'N/A'}</p>
              <p className="meta">Profile: {auspiciousData.method_profile || auspiciousData.method || 'muhurta'}</p>
            </article>

            <article className="glass-card muhurta-highlight">
              <h3>Rahu Kalam</h3>
              <p className="value">{rahuData.rahu_kalam?.start || '—'}</p>
              <p>{rahuData.rahu_kalam?.end || '—'}</p>
              <p className="meta">Segment {rahuData.rahu_kalam?.segment} ({rahuData.weekday})</p>
            </article>

            <article className="glass-card muhurta-highlight">
              <h3>Tara-Bala</h3>
              <p className="value">{auspiciousData.tara_bala?.quality || 'unknown'}</p>
              {auspiciousData.tara_bala?.tara?.name && (
                <p>
                  {auspiciousData.tara_bala.tara.name} (distance {auspiciousData.tara_bala.tara.distance})
                </p>
              )}
              <p className="meta">Assumption: {auspiciousData.assumption_set_id || 'np-mainstream-v2'}</p>
            </article>
          </section>

          <section className="glass-card muhurta-table-card">
            <h3>Auspicious Muhurtas</h3>
            {auspiciousData.muhurtas?.length > 0 ? (
              <table className="muhurta-table">
                <thead>
                  <tr>
                    <th>#</th>
                    <th>Name</th>
                    <th>Start</th>
                    <th>End</th>
                    <th>Score</th>
                    <th>Hora</th>
                    <th>Chaughadia</th>
                  </tr>
                </thead>
                <tbody>
                  {auspiciousData.muhurtas.slice(0, 12).map((row) => (
                    <tr key={`${row.index}-${row.start}`}>
                      <td>{row.number}</td>
                      <td>{row.name}</td>
                      <td>{row.start}</td>
                      <td>{row.end}</td>
                      <td>{row.score}</td>
                      <td>{row.hora?.lord_display || '—'}</td>
                      <td>{row.chaughadia?.name_display || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>No ceremony-specific windows found; use Abhijit Muhurta as fallback.</p>
            )}
          </section>

          <section className="glass-card muhurta-table-card">
            <h3>Day/Night Snapshot</h3>
            <p>
              Daylight: {dayData.daylight_minutes} min · Night: {dayData.night_minutes} min ·
              Day Muhurtas: {dayData.day_muhurtas?.length || 0} · Night Muhurtas: {dayData.night_muhurtas?.length || 0}
            </p>
            <p>
              Day Hora: {dayData.hora?.day?.[0]?.lord_display || '—'} starts ·
              First Chaughadia: {dayData.chaughadia?.day?.[0]?.name_display || '—'}
            </p>
          </section>

          {Array.isArray(auspiciousData.warnings) && auspiciousData.warnings.length > 0 && (
            <section className="glass-card muhurta-page__warnings">
              <h3>Warnings</h3>
              <ul>
                {auspiciousData.warnings.map((warning) => (
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

export default MuhurtaPage;
