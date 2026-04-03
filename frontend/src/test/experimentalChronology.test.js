import { buildExperimentalConversion, buildHorizonDescriptor } from '../lib/chronologyProjection';

describe('chronologyProjection', () => {
  it('anchors April 14 2026 AD to the 2083 BS new year', () => {
    const result = buildExperimentalConversion({
      system: 'gregorian',
      era: 'AD',
      year: 2026,
      month: 4,
      day: 14,
    });

    expect(result.output.calendar).toBe('bs');
    expect(result.output.year).toBe(2083);
    expect(result.output.era).toBe('BS');
    expect(result.output.month).toBe(1);
    expect(result.output.day).toBe(1);
  });

  it('supports far historical and far future coordinates in experimental mode', () => {
    const ancient = buildExperimentalConversion({
      system: 'gregorian',
      era: 'BC',
      year: 10000,
      month: 1,
      day: 1,
    });
    const farFuture = buildExperimentalConversion({
      system: 'bs',
      era: 'BS',
      year: 10000,
      month: 1,
      day: 1,
    });

    expect(ancient.output.calendar).toBe('bs');
    expect(buildHorizonDescriptor({ system: 'gregorian', era: 'BC', year: 10000 }).band).toBe('experimental');
    expect(farFuture.output.calendar).toBe('gregorian');
    expect(buildHorizonDescriptor({ system: 'bs', era: 'BS', year: 10000 }).band).toBe('experimental');
  });
});
