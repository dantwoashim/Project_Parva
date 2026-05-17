export function firstTrueIndexes(bits: boolean[], count: number) {
  return bits.map((bit, index) => bit ? index + 1 : null).filter((item): item is number => item !== null).slice(0, count);
}
