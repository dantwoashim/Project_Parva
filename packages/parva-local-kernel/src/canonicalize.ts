export function canonicalize(query: Record<string, unknown>) {
  return JSON.stringify(query, Object.keys(query).sort());
}
