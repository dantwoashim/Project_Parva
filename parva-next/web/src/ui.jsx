import { NavLink } from "react-router-dom";

export function Shell({ children }) {
  return <div className="shell">
    <a className="skip-link" href="#main">Skip to content</a>
    <header className="header">
      <NavLink to="/" className="brand" aria-label="Parva home"><span className="brand-mark">प</span>Parva<span className="brand-caption">THE NEPALI CALENDAR</span></NavLink>
      <nav className="nav" aria-label="Main navigation">
        <NavLink to="/convert">Convert</NavLink><NavLink to="/calendar">Calendar</NavLink>
        <NavLink to="/holidays">Holidays</NavLink><NavLink to="/review">Review dates</NavLink>
      </nav>
    </header>
    <main id="main">{children}</main>
    <footer><span>Parva / पर्व<br /><span className="small">Dates, with their sources.</span></span>
      <nav aria-label="Reference navigation"><NavLink to="/festivals">Festivals</NavLink><NavLink to="/audit">Method comparison</NavLink><NavLink to="/data">Sources & coverage</NavLink><a href="/docs">API</a></nav>
      <p className="small muted">An independent calendar reference. Holiday coverage is partial; employer policies and later notices may differ.</p>
    </footer>
  </div>;
}

export function Source({ id }) {
  if (!id) return null;
  const label = /^moha-\d{4}$/.test(id) ? `MoHA ${id.slice(5)}` : id.includes(",") ? "Calendar table" : id;
  return <span className="source" title={id}>{label}</span>;
}

export function Status({ loading, error }) {
  if (loading) return <div className="loading" role="status" aria-label="Loading calendar data"><span /><span /><span /></div>;
  if (error) return <p className="err" role="alert">{error}</p>;
  return null;
}

export function Coverage({ value = "partial" }) {
  return <p className="notice"><strong>{value === "missing" ? "No holiday source for this year." : "Partial holiday coverage."}</strong> Listed dates do not establish that other days are working days. <NavLink to="/data">View evidence</NavLink></p>;
}
