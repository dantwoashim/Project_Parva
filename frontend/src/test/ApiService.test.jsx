import {
  calendarAPI,
  fetchAPIEnvelope,
  festivalAPI,
  kundaliAPI,
  muhurtaAPI,
  personalAPI,
  placesAPI,
  temporalAPI,
} from '../services/api';

function responseHeaders(overrides = {}) {
  const normalized = Object.fromEntries(
    Object.entries(overrides).map(([key, value]) => [key.toLowerCase(), value]),
  );
  return {
    get(name) {
      return normalized[name.toLowerCase()] || null;
    },
  };
}

function jsonHeaders(overrides = {}) {
  return responseHeaders({
    'content-type': 'application/json',
    ...overrides,
  });
}

function jsonResponse(payload) {
  return {
    ok: true,
    status: 200,
    statusText: 'OK',
    headers: jsonHeaders(),
    json: async () => payload,
    text: async () => JSON.stringify(payload),
  };
}

function buildCompassEnvelope(overrides = {}) {
  return {
    data: {
      date: '2026-02-15',
      location: {
        latitude: 27.7172,
        longitude: 85.324,
        timezone: 'Asia/Kathmandu',
      },
      bikram_sambat: {
        year: 2082,
        month: 11,
        day: 3,
        month_name: 'Falgun',
      },
      primary_readout: {
        tithi_name: 'Chaturdashi',
        tithi_number: 14,
        paksha: 'krishna',
      },
      horizon: {
        sunrise: {
          local: '2026-02-15T06:42:00+05:45',
          utc: '2026-02-15T00:57:00Z',
          local_time: '06:42 AM',
        },
        sunset: {
          local: '2026-02-15T17:53:00+05:45',
          utc: '2026-02-15T12:08:00Z',
          local_time: '05:53 PM',
        },
        current_muhurta: {
          name: 'Abhijit Muhurta',
          start: '2026-02-15T10:30:00+05:45',
          end: '2026-02-15T12:15:00+05:45',
          score: 88,
          class: 'auspicious',
        },
        rahu_kalam: {
          start: '2026-02-15T13:15:00+05:45',
          end: '2026-02-15T14:30:00+05:45',
        },
      },
      today: {
        festivals: [],
        count: 0,
      },
      signals: {
        nakshatra: { name: 'Shravana', pada: 1 },
        yoga: { name: 'Shubha' },
        karana: { name: 'Vishti' },
        vaara: { name_english: 'Sunday' },
      },
      quality_band_filter: 'computed',
      engine: {
        method: 'ephemeris_udaya',
        method_profile: 'temporal_compass_v1',
      },
      ...overrides.data,
    },
    meta: {
      method: 'ephemeris_udaya',
      confidence: { level: 'high' },
      ...overrides.meta,
    },
  };
}

function buildPersonalContextEnvelope(overrides = {}) {
  return {
    data: {
      date: '2026-02-15',
      location: {
        latitude: 27.7172,
        longitude: 85.324,
        timezone: 'Asia/Kathmandu',
      },
      place_title: 'Your sanctuary',
      status_line: 'Sunrise 06:42 AM - Asia/Kathmandu',
      visit_note: 'Place-aware daily guidance stays synced to this location and date.',
      context_title: 'Morning Calm',
      context_summary: 'Quiet morning at your saved place.',
      temperature_note: null,
      daily_inspiration: 'Hold the quiet before the day opens.',
      upcoming_reminders: [
        { id: 'dashain', title: 'Dashain', date_label: 'Oct 20', status: 'Upcoming' },
      ],
      ...overrides.data,
    },
    meta: {
      method: 'personal_context_synthesis',
      confidence: { level: 'high' },
      ...overrides.meta,
    },
  };
}

function buildHeatmapEnvelope(overrides = {}) {
  return {
    data: {
      date: '2026-02-15',
      location: {
        latitude: 27.7172,
        longitude: 85.324,
        timezone: 'Asia/Kathmandu',
      },
      type: 'general',
      assumption_set_id: 'np-mainstream-v2',
      best_window: {
        index: 6,
        name: 'Abhijit Muhurta',
        start: '2026-02-15T10:30:00+05:45',
        end: '2026-02-15T12:15:00+05:45',
        score: 88,
      },
      blocks: [
        {
          index: 6,
          name: 'Abhijit Muhurta',
          start: '2026-02-15T10:30:00+05:45',
          end: '2026-02-15T12:15:00+05:45',
          class: 'auspicious',
          score: 88,
          reason_codes: ['quality:auspicious'],
        },
      ],
      rahu_kalam: {
        start: '2026-02-15T13:15:00+05:45',
        end: '2026-02-15T14:30:00+05:45',
      },
      sunrise: '2026-02-15T06:42:00+05:45',
      sunset: '2026-02-15T17:53:00+05:45',
      ranking_profile: { minimum_score: 25 },
      tara_bala: { status: 'neutral' },
      ...overrides.data,
    },
    meta: {
      method: 'rule_ranked_muhurta_v2',
      confidence: { level: 'high' },
      ...overrides.meta,
    },
  };
}

function buildMuhurtaCalendarPayload(overrides = {}) {
  return {
    from: '2026-03-01',
    to: '2026-04-30',
    location: {
      latitude: 27.7172,
      longitude: 85.324,
      timezone: 'Asia/Kathmandu',
    },
    type: 'general',
    assumption_set_id: 'np-mainstream-v2',
    days: [
      {
        date: '2026-03-21',
        tone: 'strong',
        window_count: 4,
        best_window: {
          name: 'Abhijit Muhurta',
          start: '2026-03-21T10:30:00+05:45',
          end: '2026-03-21T12:15:00+05:45',
          reason_codes: ['quality:auspicious'],
        },
      },
    ],
    total: 1,
    ...overrides,
  };
}

function buildPlaceSearchPayload(overrides = {}) {
  return {
    query: 'kathmandu',
    items: [
      {
        label: 'Kathmandu, Bagmati Province, Nepal',
        latitude: 27.7172,
        longitude: 85.324,
        timezone: 'Asia/Kathmandu',
        source: 'openstreetmap_nominatim',
      },
    ],
    total: 1,
    source: 'openstreetmap_nominatim',
    attribution: 'Search results use OpenStreetMap Nominatim data.',
    ...overrides,
  };
}

function buildKundaliGraphEnvelope(overrides = {}) {
  return {
    data: {
      datetime: '2026-02-15T06:30:00+05:45',
      location: {
        latitude: 27.7172,
        longitude: 85.324,
        timezone: 'Asia/Kathmandu',
      },
      lagna: {
        rashi_english: 'Pisces',
      },
      layout: {
        viewbox: '0 0 400 400',
        house_nodes: [
          { id: 'house_1', house_number: 1, x: 200, y: 60 },
        ],
        graha_nodes: [
          { id: 'moon', label: 'Moon', x: 220, y: 100 },
          { id: 'sun', label: 'Sun', x: 260, y: 120 },
        ],
        aspect_edges: [
          { id: 'moon->sun', source: 'moon', target: 'sun' },
        ],
      },
      insight_blocks: [
        { id: 'lagna_summary', title: 'Lagna Orientation', summary: 'Lagna is Pisces.' },
      ],
      ...overrides.data,
    },
    meta: {
      method: 'swiss_ephemeris_sidereal',
      confidence: { level: 'high' },
      ...overrides.meta,
    },
  };
}

describe('API service', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.useRealTimers();
  });

  it('serializes numeric coordinates as strings for private POST requests', async () => {
    const fetchMock = vi.fn(async () => jsonResponse({
      data: {
        date: '2026-02-15',
        location: {
          latitude: 27.7172,
          longitude: 85.324,
          timezone: 'Asia/Kathmandu',
        },
        tithi: { name: 'Chaturdashi' },
      },
      meta: {},
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
        headers: expect.objectContaining({
          'X-Parva-Envelope': 'data-meta',
        }),
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
    const fetchMock = vi.fn(async () => jsonResponse(buildCompassEnvelope()));
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
        headers: expect.objectContaining({
          'X-Parva-Envelope': 'data-meta',
        }),
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

  it('preserves request references from response headers on plain text failures', async () => {
    vi.stubGlobal('fetch', async () => ({
      ok: false,
      status: 503,
      statusText: 'Service Unavailable',
      headers: responseHeaders({
        'content-type': 'text/plain',
        'x-request-id': 'req_text_503',
      }),
      json: async () => {
        throw new Error('not json');
      },
      text: async () => 'Temporary upstream failure',
    }));

    await expect(fetchAPIEnvelope('/temporal/compass')).rejects.toMatchObject({
      name: 'ParvaApiError',
      message: 'Temporary upstream failure',
      status: 503,
      requestId: 'req_text_503',
    });
  });

  it('rejects flat payloads when an authoritative envelope was explicitly requested', async () => {
    vi.stubGlobal('fetch', async () => ({
      ...jsonResponse({
        date: '2026-02-15',
        location: {
          latitude: 27.7172,
          longitude: 85.324,
          timezone: 'Asia/Kathmandu',
        },
      }),
      headers: jsonHeaders({ 'x-request-id': 'req_flat_502' }),
    }));

    await expect(fetchAPIEnvelope('/temporal/compass', { preferEnvelope: true })).rejects.toMatchObject({
      name: 'ParvaApiError',
      status: 502,
      detail: '/temporal/compass did not honor the requested data-meta envelope contract.',
      requestId: 'req_flat_502',
    });
  });

  it('raises a timeout error when the request exceeds the configured timeout', async () => {
    vi.useFakeTimers();
    vi.stubGlobal(
      'fetch',
      vi.fn((_, options = {}) => new Promise((_, reject) => {
        options.signal?.addEventListener('abort', () => {
          reject(options.signal.reason || new DOMException('Aborted', 'AbortError'));
        }, { once: true });
      })),
    );

    const request = fetchAPIEnvelope('/personal/panchanga', { timeoutMs: 25 });
    const expectation = expect(request).rejects.toMatchObject({
      name: 'ParvaApiError',
      status: 408,
      message: 'Request timed out after 25ms',
    });
    await vi.advanceTimersByTimeAsync(25);
    await expectation;
  });

  it('surfaces contract drift for critical calendar responses', async () => {
    vi.stubGlobal('fetch', async () => ({
      ok: true,
      status: 200,
      statusText: 'OK',
      headers: jsonHeaders(),
      json: async () => ({
        gregorian: '2026-02-15',
        bikram_sambat: { year: 2082 },
      }),
      text: async () => '',
    }));

    await expect(calendarAPI.getToday()).rejects.toMatchObject({
      name: 'ParvaApiError',
      status: 502,
      detail: 'Missing required field: tithi',
    });
  });

  it('defaults calendar panchanga requests to today when the caller does not provide a date', async () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-04-04T06:00:00+05:45'));
    const fetchMock = vi.fn(async () => jsonResponse({
      data: {
        date: '2026-04-04',
        panchanga: {
          tithi: { number: 2, name: 'Dwitiya', paksha: 'shukla' },
          nakshatra: { number: 1, name: 'Ashwini', pada: 1 },
          yoga: { number: 1, name: 'Vishkambha' },
          karana: { number: 1, name: 'Bava' },
          vaara: { name_english: 'Saturday', name_sanskrit: 'Shanivara' },
        },
        bikram_sambat: { year: 2082, month: 1, day: 22, month_name: 'Baisakh' },
        ephemeris: { mode: 'swiss_moshier', accuracy: 'arcsecond', library: 'pyswisseph' },
      },
      meta: {},
    }));
    vi.stubGlobal('fetch', fetchMock);

    await calendarAPI.getPanchangaEnvelope('');

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/calendar/panchanga?date=2026-04-04'),
      expect.any(Object),
    );
  });

  it('surfaces contract drift for festival timeline envelopes', async () => {
    vi.stubGlobal('fetch', async () => ({
      ok: true,
      status: 200,
      statusText: 'OK',
      headers: jsonHeaders(),
      json: async () => ({
        data: {
          facets: {},
        },
        meta: {},
      }),
      text: async () => '',
    }));

    await expect(festivalAPI.getTimelineEnvelope({
      from: '2026-02-15',
      to: '2026-08-15',
    })).rejects.toMatchObject({
      name: 'ParvaApiError',
      status: 502,
      detail: 'Festival timeline payload must include a groups array.',
    });
  });

  it('surfaces contract drift for temporal compass envelopes', async () => {
    vi.stubGlobal('fetch', async () => ({
      ...jsonResponse({
        data: {
          date: '2026-02-15',
          location: {
            latitude: 27.7172,
            longitude: 85.324,
            timezone: 'Asia/Kathmandu',
          },
          primary_readout: {
            tithi_name: 'Chaturdashi',
            paksha: 'krishna',
          },
          signals: {},
          today: { festivals: [], count: 0 },
          quality_band_filter: 'computed',
          engine: {
            method: 'ephemeris_udaya',
            method_profile: 'temporal_compass_v1',
          },
        },
        meta: {},
      }),
      headers: jsonHeaders({ 'x-request-id': 'req_contract_temporal_1' }),
    }));

    await expect(temporalAPI.getCompassEnvelope({
      date: '2026-02-15',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
    })).rejects.toMatchObject({
      name: 'ParvaApiError',
      status: 502,
      detail: 'Temporal compass payload must include a bikram_sambat object.',
      requestId: 'req_contract_temporal_1',
    });
  });

  it('accepts live-shaped temporal compass envelopes', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse(buildCompassEnvelope()));

    await expect(temporalAPI.getCompassEnvelope({
      date: '2026-02-15',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
    })).resolves.toMatchObject({
      data: {
        primary_readout: { tithi_name: 'Chaturdashi' },
        horizon: {
          current_muhurta: { name: 'Abhijit Muhurta' },
        },
      },
    });
  });

  it('accepts temporal compass envelopes when sunset is temporarily unavailable', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse(buildCompassEnvelope({
      data: {
        horizon: {
          sunrise: {
            local: '2026-02-15T06:42:00+05:45',
            utc: '2026-02-15T00:57:00Z',
            local_time: '06:42 AM',
          },
          sunset: null,
          current_muhurta: {
            name: 'Abhijit Muhurta',
            start: '2026-02-15T10:30:00+05:45',
            end: '2026-02-15T12:15:00+05:45',
            score: 88,
            class: 'auspicious',
          },
          rahu_kalam: {
            start: '2026-02-15T13:15:00+05:45',
            end: '2026-02-15T14:30:00+05:45',
          },
        },
      },
    })));

    await expect(temporalAPI.getCompassEnvelope({
      date: '2026-02-15',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
    })).resolves.toMatchObject({
      data: {
        horizon: {
          sunrise: { local_time: '06:42 AM' },
          sunset: null,
        },
      },
    });
  });

  it('accepts live-shaped personal context envelopes', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse(buildPersonalContextEnvelope()));

    await expect(personalAPI.getContextEnvelope({
      date: '2026-02-15',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
    })).resolves.toMatchObject({
      data: {
        context_title: 'Morning Calm',
        upcoming_reminders: [{ title: 'Dashain' }],
      },
    });
  });

  it('rejects malformed personal context envelopes', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse(buildPersonalContextEnvelope({
      data: {
        upcoming_reminders: { title: 'Dashain' },
      },
    })));

    await expect(personalAPI.getContextEnvelope({
      date: '2026-02-15',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
    })).rejects.toMatchObject({
      name: 'ParvaApiError',
      status: 502,
      detail: 'Personal context upcoming_reminders must be an array of reminder objects.',
    });
  });

  it('accepts live-shaped muhurta heatmap envelopes', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse(buildHeatmapEnvelope()));

    await expect(muhurtaAPI.getHeatmapEnvelope({
      date: '2026-02-15',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
      type: 'general',
    })).resolves.toMatchObject({
      data: {
        blocks: [{ class: 'auspicious' }],
      },
    });
  });

  it('rejects malformed muhurta heatmap envelopes', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse(buildHeatmapEnvelope({
      data: {
        blocks: [
          {
            index: 6,
            start: null,
            end: '2026-02-15T12:15:00+05:45',
            class: 'auspicious',
          },
        ],
      },
    })));

    await expect(muhurtaAPI.getHeatmapEnvelope({
      date: '2026-02-15',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
      type: 'general',
    })).rejects.toMatchObject({
      name: 'ParvaApiError',
      status: 502,
      detail: 'blocks[].start must be a string or an object with local/utc/local_time fields.',
    });
  });

  it('accepts ranked muhurta calendar summaries and normalizes coordinate query params', async () => {
    const fetchMock = vi.fn(async () => jsonResponse(buildMuhurtaCalendarPayload()));
    vi.stubGlobal('fetch', fetchMock);

    await expect(muhurtaAPI.getCalendar({
      from: '2026-03-01',
      to: '2026-04-30',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
      type: 'general',
    })).resolves.toMatchObject({
      days: [{ best_window: { name: 'Abhijit Muhurta' } }],
    });

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/muhurta/calendar?from=2026-03-01&to=2026-04-30&type=general&assumption_set=np-mainstream-v2&lat=27.7172&lon=85.324&tz=Asia%2FKathmandu'),
      expect.any(Object),
    );
  });

  it('accepts normalized place search payloads', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse(buildPlaceSearchPayload()));

    await expect(placesAPI.search({
      query: 'kathmandu',
      limit: 4,
    })).resolves.toMatchObject({
      items: [{ label: 'Kathmandu, Bagmati Province, Nepal' }],
    });
  });

  it('accepts live-shaped kundali graph envelopes', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse(buildKundaliGraphEnvelope()));

    await expect(kundaliAPI.getGraphEnvelope({
      datetime: '2026-02-15T06:30:00+05:45',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
    })).resolves.toMatchObject({
      data: {
        layout: {
          house_nodes: [{ id: 'house_1' }],
        },
      },
    });
  });

  it('rejects malformed kundali graph envelopes', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse(buildKundaliGraphEnvelope({
      data: {
        layout: {
          viewbox: '0 0 400 400',
          house_nodes: [],
          graha_nodes: [{ id: 'moon', label: 'Moon', x: 220, y: 100 }],
          aspect_edges: [],
        },
      },
    })));

    await expect(kundaliAPI.getGraphEnvelope({
      datetime: '2026-02-15T06:30:00+05:45',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
    })).rejects.toMatchObject({
      name: 'ParvaApiError',
      status: 502,
      detail: 'Kundali graph layout.house_nodes must contain at least one house node.',
    });
  });

  it('requests authoritative backend envelopes for festival detail reads', async () => {
    const fetchMock = vi.fn(async () => jsonResponse({
      data: {
        festival: {
          id: 'dashain',
          name: 'Dashain',
        },
      },
      meta: {},
    }));
    vi.stubGlobal('fetch', fetchMock);

    await festivalAPI.getByIdEnvelope('dashain', 2026);

    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/festivals/dashain?year=2026'),
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-Parva-Envelope': 'data-meta',
        }),
      }),
    );
  });

  it('accepts raw list responses for festival on-date reads', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse([
      {
        id: 'holi',
        name: 'Holi',
        start_date: '2026-03-21',
      },
    ]));

    await expect(festivalAPI.getOnDate('2026-03-21')).resolves.toMatchObject([
      {
        id: 'holi',
        name: 'Holi',
      },
    ]);
  });

  it('accepts structured sunrise objects for personal panchanga envelopes', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse({
      data: {
        date: '2026-02-15',
        location: {
          latitude: 27.7172,
          longitude: 85.324,
          timezone: 'Asia/Kathmandu',
        },
        tithi: { name: 'Chaturdashi' },
        sunrise: {
          local: '2026-02-15T06:42:00+05:45',
          utc: '2026-02-15T00:57:00Z',
          local_time: '06:42 AM',
        },
        local_sunrise: {
          local: '2026-02-15T06:44:00+05:45',
          utc: '2026-02-15T00:59:00Z',
          local_time: '06:44 AM',
        },
      },
      meta: {},
    }));

    await expect(personalAPI.getPanchangaEnvelope({
      date: '2026-02-15',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
    })).resolves.toMatchObject({
      data: {
        sunrise: { local_time: '06:42 AM' },
        local_sunrise: { local_time: '06:44 AM' },
      },
    });
  });

  it('rejects malformed sunrise references for personal panchanga envelopes', async () => {
    vi.stubGlobal('fetch', async () => jsonResponse({
      data: {
        date: '2026-02-15',
        location: {
          latitude: 27.7172,
          longitude: 85.324,
          timezone: 'Asia/Kathmandu',
        },
        tithi: { name: 'Chaturdashi' },
        local_sunrise: {
          label: 'sunrise pending',
        },
      },
      meta: {},
    }));

    await expect(personalAPI.getPanchangaEnvelope({
      date: '2026-02-15',
      lat: 27.7172,
      lon: 85.3240,
      tz: 'Asia/Kathmandu',
    })).rejects.toMatchObject({
      name: 'ParvaApiError',
      status: 502,
      detail: 'local_sunrise must include at least one of local, utc, or local_time.',
    });
  });
});
