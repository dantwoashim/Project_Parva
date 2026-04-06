export function startCaseTruth(value) {
  return String(value || '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

export function todayYear() {
  return new Date().getFullYear();
}

export function buildTruthLabStats(atlas, year) {
  const disputes = atlas?.disputes || [];
  const highRisk = disputes.filter((item) => item.boundary_radar === 'high_disagreement_risk').length;
  return [
    { label: 'Year', value: year },
    { label: 'Tracked disputes', value: disputes.length },
    { label: 'High-risk rows', value: highRisk },
    { label: 'Top stability', value: disputes[0] ? disputes[0].stability_score : 'N/A' },
  ];
}
