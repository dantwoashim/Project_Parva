export function parseLocalTemporalQuery(input) {
  const normalized = input
    .replace(/[०१२३४५६७८९]/g, (digit) => '०१२३४५६७८९'.indexOf(digit))
    .toLowerCase();
  const isDashain = /dashain|dasain|दशैं|दशैँ/.test(normalized);
  const year = normalized.match(/\d{4}/)?.[0] ?? null;
  if (isDashain && year) {
    return {
      intent: 'find_festival_date',
      entities: [{ type: 'festival', value: 'dashain' }],
      constraints: [{ type: 'year', value: year }],
      interpretation_confidence: 0.95,
      claim_boundary: 'local_parse_not_authority',
    };
  }
  return { intent: 'unknown', ambiguities: [{ reason: 'unsupported_or_ambiguous' }] };
}
