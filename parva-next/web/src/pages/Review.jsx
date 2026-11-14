import { useState } from "react";
import { queryURL, request } from "../api.js";
import { Source, Status } from "../ui.jsx";

export default function Review() {
  const [file, setFile] = useState(null);
  const [calendar, setCalendar] = useState("ad");
  const [column, setColumn] = useState("");
  const [result, setResult] = useState({});
  async function submit(event) {
    event.preventDefault();
    if (!file || file.size > 1048576) {
      setResult({ error: "Select a UTF-8 CSV file no larger than 1 MiB." });
      return;
    }
    setResult({ loading: true });
    try {
      const response = await request(queryURL("/v1/check", { bs: calendar === "bs", column }), { method: "POST", headers: { "Content-Type": "text/csv" }, body: file });
      setResult(response);
    } catch (error) { setResult({ error: error.message }); }
  }
  return <>
    <div className="eyebrow">CHECK BEFORE YOU IMPORT</div><h1>Review a date file</h1>
    <p className="intro">Find invalid dates, recorded holidays, and gaps in the available evidence. Each row retains its own source. This review does not approve a payroll run.</p>
    <form className="review-form" onSubmit={submit}>
      <label>CSV file<input type="file" accept=".csv,text/csv" required disabled={result.loading} onChange={(event) => { setFile(event.target.files[0]); setResult({}); }} /></label>
      <div className="row"><label>Dates are in<select value={calendar} disabled={result.loading} onChange={(event) => { setCalendar(event.target.value); setResult({}); }}><option value="ad">Gregorian (AD)</option><option value="bs">Bikram Sambat (BS)</option></select></label>
        <label>Date column<input placeholder="Auto-detect" value={column} disabled={result.loading} onChange={(event) => { setColumn(event.target.value); setResult({}); }} /></label>
        <button disabled={result.loading}>{result.loading ? "Reviewing…" : "Review dates"}</button></div>
      <p className="small muted">UTF-8 · up to 1 MiB / 10,000 rows · YYYY-MM-DD. The file is sent to this server for processing; this application does not persist it.</p>
    </form><Status {...result} />
    {result.data && <section aria-live="polite"><h2>{result.data.rows.length} rows · {result.data.to_review} need review</h2>
      <div className="scroll"><table><thead><tr><th>Input</th><th>AD / BS</th><th>Result</th><th>Evidence</th></tr></thead><tbody>{result.data.rows.map((row,index) => <tr key={index}>
        <td className="mono">{row.input || "(empty)"}</td><td>{row.ad ?? "—"}<br /><span className="muted">{row.bs}</span></td>
        <td>{row.status.replaceAll("_", " ")}<p className="small muted">{row.error ?? row.flags.join(", ").replaceAll("_", " ")}</p></td>
        <td><Source id={row.source} /><p className="small muted">{row.coverage} coverage</p></td>
      </tr>)}</tbody></table></div>
    </section>}
  </>;
}
