import { translate } from '../i18n/messages';

describe('i18n messages', () => {
  it('returns english copy by default', () => {
    expect(translate('en', 'common.today')).toBe('Today');
  });

  it('returns nepali copy when requested', () => {
    expect(translate('ne', 'common.today')).toBe('आज');
  });

  it('interpolates template values', () => {
    expect(
      translate('en', 'profile.cache.revision', {
        label: 'Guest device cache',
        revision: 3,
      }),
    ).toContain('Revision 3');
  });
});
