import { useState } from "react";
import { fmt, todayISO, useParva } from "../api.js";
import { Source, Status } from "../ui.jsx";

export default function Convert() {
  const [ad, setAd] = useState(todayISO());
  const [bs, setBs] = useState("");
  const [query, setQuery] = useState({ ad });
  const result = useParva("/v1/convert", query);

  return (
    <>
      <h1>Convert</h1>
      <div className="grid">
        <form className="card" onSubmit={(e) => { e.preventDefault(); setQuery({ ad }); }}>
          <h2>AD → BS</h2>
          <div className="row"><input aria-label="Gregorian date" type="date" value={ad} onChange={(e) => setAd(e.target.value)} required /><button>Convert</button></div>
        </form>
        <form className="card" onSubmit={(e) => { e.preventDefault(); setQuery({ bs }); }}>
          <h2>BS → AD</h2>
          <div className="row">
            <input aria-label="Bikram Sambat date" value={bs} onChange={(e) => setBs(e.target.value)} placeholder="2083-03-32" pattern="[0-9०-९]{4}-[0-9०-९]{1,2}-[0-9०-९]{1,2}" required />
            <button>Convert</button>
          </div>
          <p className="small muted">Invalid dates (Baishakh 32, a 13th month) are refused, not rounded.</p>
        </form>
      </div>
      <section className="card" style={{ marginTop: "1rem" }}>
        <Status {...result} />
        {result.data && (
          <>
            <div className="stat">{result.data.bs.text}<span className="ne">{result.data.bs.nepali}</span></div>
            <p>{fmt(result.data.ad)} = {result.data.bs.month_name} {result.data.bs.day}, {result.data.bs.year} BS</p>
            <p><Source id={result.source} /> <span className="small muted">month lengths for BS {result.data.bs.year} come from these sources</span></p>
          </>
        )}
      </section>
    </>
  );
}
