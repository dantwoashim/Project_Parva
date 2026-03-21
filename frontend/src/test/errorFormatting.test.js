import { describeSupportError, pickRejectedReason } from '../services/errorFormatting';

describe('error formatting', () => {
  it('appends the support reference when requestId is present', () => {
    expect(describeSupportError(
      { message: 'Festival timeline is unavailable right now.', requestId: 'req_live_123' },
      'Fallback message',
    )).toBe('Festival timeline is unavailable right now. Support reference: req_live_123.');
  });

  it('falls back cleanly when no structured error metadata exists', () => {
    expect(describeSupportError({}, 'Fallback message')).toBe('Fallback message');
  });

  it('returns the first rejected reason from settled results', () => {
    const reason = { message: 'Request failed', requestId: 'req_live_456' };
    expect(pickRejectedReason(
      { status: 'fulfilled', value: {} },
      { status: 'rejected', reason },
      { status: 'rejected', reason: { message: 'Later failure' } },
    )).toBe(reason);
  });
});
