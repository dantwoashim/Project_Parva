function normalize(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => normalize(item));
  }
  if (value && typeof value === 'object') {
    const input = value as Record<string, unknown>;
    return Object.keys(input)
      .sort()
      .reduce<Record<string, unknown>>((acc, key) => {
        acc[key] = normalize(input[key]);
        return acc;
      }, {});
  }
  if (typeof value === 'string') {
    return value.trim().replace(/\s+/g, ' ').toLowerCase();
  }
  return value;
}

export function canonicalize(payload: unknown): string {
  return JSON.stringify(normalize(payload));
}
