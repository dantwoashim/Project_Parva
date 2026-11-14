import { useState } from "react";
import { todayISO, useParva } from "../api.js";
import { Status } from "../ui.jsx";

export default function Audit() {
  const [year, setYear] = useState(Number(todayISO().slice(0, 4)));
  const result = useParva(`/v1/audit/${year}`);
  return <>
    <div className="eyebrow">METHODS & EVIDENCE</div><h1>Gazette and calculation</h1>
    <p className="intro">A comparison of recorded festival dates and astronomical rules. Historical agreement is retrospective evidence; it does not guarantee future festival dates or official acceptance.</p>
    <p className="row"><button className="quiet" disabled={year <= 1944} onClick={() => setYear(year - 1)}>← Previous year</button><strong>{year}</strong><button className="quiet" disabled={year >= 2038} onClick={() => setYear(year + 1)}>Next year →</button></p>
    <Status {...result} />
    {result.data && <>
      <p className="stat">{result.data.agree} / {result.data.compared}<span className="small muted"> exact matches</span></p>
      {result.data.compared === 0 && <p>No overlapping gazette records to compare in this year.</p>}
      {result.data.disagreements.length > 0 && <div className="scroll"><table><thead><tr><th>Festival</th><th>Gazette</th><th>Calculation</th><th>Difference</th></tr></thead>
        <tbody>{result.data.disagreements.map((row) => <tr key={row.id}><td>{row.id}</td><td>{row.gazette}</td><td>{row.engine}</td><td>{row.delta_days} days</td></tr>)}</tbody></table></div>}
      <p className="notice">This comparison uses historical imported rows as well as source-reviewed rows. It is a diagnostic, not a certification.</p>
    </>}
  </>;
}
