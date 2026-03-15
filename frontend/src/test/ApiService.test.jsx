import { fetchAPIEnvelope, personalAPI, temporalAPI } from '../services/api';

function jsonHeaders() {
  return {
    get(name) {
      return name.toLowerCase() === 'content-type' ? 'application/json' : null;
    },
  };
}

describe('API service', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('serializes numeric coordinates as strings for private POST requests', async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      status: 200,
      statusText: 'OK',
      headers: jsonHeaders(),
      json: async () => ({ data: { ok: true }, meta: {} }),
      text: async () => JSON.stringify({ data: { ok: true }, meta: {} }),
    }));
    vi.stubGlobal('fetch', fetchMock);

    await personalAPI.getPanchangaEnvelope({
      date: '2026-02-15',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
    });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/personal/panchanga'),
      expect.objectContaining({
        method: 'POST',
        cache: 'no-store',
        body: JSON.stringify({
          date: '2026-02-15',
          lat: '27.7172',
          lon: '85.324',
          tz: 'Asia/Kathmandu',
        }),
      }),
    );
  });

  it('trims string coordinates before private POST requests', async () => {
    const fetchMock = vi.fn(async () => ({
      ok: true,
      status: 200,
      statusText: 'OK',
      headers: jsonHeaders(),
      json: async () => ({ data: { ok: true }, meta: {} }),
      text: async () => JSON.stringify({ data: { ok: true }, meta: {} }),
    }));
    vi.stubGlobal('fetch', fetchMock);

    await temporalAPI.getCompassEnvelope({
      date: '2026-02-15',
      lat: ' 27.7172 ',
      lon: ' 85.3240 ',
      tz: 'Asia/Kathmandu',
    });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/temporal/compass'),
      expect.objectContaining({
        body: JSON.stringify({
          date: '2026-02-15',
          lat: '27.7172',
          lon: '85.3240',
          tz: 'Asia/Kathmandu',
          quality_band: 'computed',
        }),
      }),
    );
  });

  it('preserves structured backend error details', async () => {
    vi.stubGlobal('fetch', async () => ({
      ok: false,
      status: 422,
      statusText: 'Unprocessable Entity',
      headers: jsonHeaders(),
      json: async () => ({
        detail: 'Request validation failed',
        request_id: 'req_test_123',
        errors: [{ loc: ['body', 'date'], msg: 'Field required' }],
      }),
      text: async () => '',
    }));

    await expect(fetchAPIEnvelope('/personal/panchanga')).rejects.toMatchObject({
      name: 'ParvaApiError',
      message: 'Request validation failed',
      status: 422,
      requestId: 'req_test_123',
      errors: [{ loc: ['body', 'date'], msg: 'Field required' }],
    });
  });
});
