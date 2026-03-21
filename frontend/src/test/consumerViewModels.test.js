import {
  CONSUMER_BEST_TIME_OPTIONS,
  buildConsumerBestTimeViewModel,
  buildConsumerFestivalDetailViewModel,
  buildConsumerFestivalsViewModel,
  buildConsumerMyPlaceViewModel,
  buildConsumerTodayViewModel,
} from '../consumer/consumerViewModels';

describe('consumer view models', () => {
  const temporalState = {
    date: '2026-02-15',
    timezone: 'Asia/Kathmandu',
    language: 'en',
    theme: 'warm-paper',
    location: { latitude: 27.7172, longitude: 85.324 },
  };

  it('builds the today answer with observances and evidence metadata', () => {
    const model = buildConsumerTodayViewModel({
      state: temporalState,
      placeLabel: 'Kathmandu',
      compass: {
        bikram_sambat: { year: 2082, month_name: 'Falgun', day: 3 },
        primary_readout: { tithi_name: 'Chaturdashi', paksha: 'krishna' },
        horizon: {
          sunrise: '2026-02-15T06:42:00+05:45',
          sunset: '2026-02-15T17:53:00+05:45',
        },
        signals: {
          nakshatra: { name: 'Shravana', pada: 1 },
          yoga: { name: 'Shubha' },
          karana: { name: 'Vishti' },
        },
      },
      compassMeta: { method: 'daily profile', confidence: { level: 'high' } },
      muhurta: {
        best_window: {
          index: 6,
          name: 'Abhijit Muhurta',
          score: 88,
          start: '2026-02-15T10:30:00+05:45',
          end: '2026-02-15T12:15:00+05:45',
        },
        rahu_kalam: {
          start: '2026-02-15T13:15:00+05:45',
          end: '2026-02-15T14:30:00+05:45',
        },
        blocks: [
          {
            index: 6,
            name: 'Abhijit Muhurta',
            class: 'auspicious',
            score: 88,
            start: '2026-02-15T10:30:00+05:45',
            end: '2026-02-15T12:15:00+05:45',
          },
        ],
      },
      muhurtaMeta: { method: 'best-time profile', confidence: { level: 'high' } },
      onDateFestivals: [{ id: 'dashain', name: 'Dashain', start_date: '2026-10-20' }],
      upcomingFestivals: [{ id: 'tihar', name: 'Tihar', start_date: '2026-11-07' }],
    });

    expect(model.headline).toBe('Today in Kathmandu');
    expect(model.observances[0].title).toBe('Dashain');
    expect(model.bestWindow.value).toMatch(/10:30 AM/i);
    expect(model.evidence.methodRef).toBe('best-time profile');
    expect(model.timeline).toHaveLength(1);
  });

  it('builds best-time guidance with a primary window, alternates, and a timeline', () => {
    const model = buildConsumerBestTimeViewModel({
      payload: {
        blocks: [
          {
            index: 1,
            name: 'Abhijit Muhurta',
            class: 'auspicious',
            score: 88,
            start: '2026-02-15T10:30:00+05:45',
            end: '2026-02-15T12:15:00+05:45',
            reason_codes: ['tara_good'],
          },
          {
            index: 2,
            name: 'Labh',
            class: 'mixed',
            score: 41,
            start: '2026-02-15T15:45:00+05:45',
            end: '2026-02-15T17:00:00+05:45',
          },
          {
            index: 3,
            name: 'Rahu Kalam',
            class: 'avoid',
            score: -30,
            start: '2026-02-15T13:15:00+05:45',
            end: '2026-02-15T14:30:00+05:45',
          },
        ],
        best_window: {
          index: 1,
          name: 'Abhijit Muhurta',
          score: 88,
          start: '2026-02-15T10:30:00+05:45',
          end: '2026-02-15T12:15:00+05:45',
        },
        rahu_kalam: {
          start: '2026-02-15T13:15:00+05:45',
          end: '2026-02-15T14:30:00+05:45',
        },
      },
      meta: { method: 'best-time profile' },
      state: temporalState,
      type: 'creative_focus',
      selectedBlock: null,
      placeLabel: 'Kathmandu',
    });

    expect(model.activityLabel).toBe('Focus work');
    expect(model.best.title).toMatch(/10:30 AM/i);
    expect(model.alternates).toHaveLength(1);
    expect(model.avoid.title).toMatch(/1:15 PM/i);
    expect(model.timeline).toHaveLength(3);
    expect(CONSUMER_BEST_TIME_OPTIONS.some((item) => item.value === 'creative_focus')).toBe(true);
  });

  it('builds the festivals browse model with a featured observance and chapters', () => {
    const model = buildConsumerFestivalsViewModel({
      payload: {
        groups: [
          {
            month_key: '2026-10',
            month_label: 'Kartik 2083',
            items: [
              {
                id: 'dashain',
                display_name: 'Dashain',
                category: 'national',
                start_date: '2026-10-20',
                end_date: '2026-10-30',
                summary: 'Blessing, reunion, and seasonal turning.',
                regional_focus: ['Nepal'],
              },
              {
                id: 'tihar',
                display_name: 'Tihar',
                category: 'national',
                start_date: '2026-11-07',
                summary: 'Festival of lights.',
                regional_focus: ['Kathmandu Valley'],
              },
            ],
          },
        ],
        facets: {
          categories: [{ value: 'national', label: 'National', count: 2 }],
          months: [{ value: '2026-10', label: 'October', count: 2 }],
          regions: [{ value: 'nepal', label: 'Nepal', count: 1 }],
        },
      },
      search: '',
      category: '',
      savedFestivals: [{ id: 'dashain' }],
    });

    expect(model.featured.title).toBe('Dashain');
    expect(model.timelineCards[0].saved).toBe(true);
    expect(model.facets.categories[0].label).toBe('National');
    expect(model.chapters[0].lead.title).toBe('Dashain');
  });

  it('builds the festival detail model with rituals, occurrences, and related observances', () => {
    const model = buildConsumerFestivalDetailViewModel({
      festival: {
        id: 'dashain',
        name: 'Dashain',
        category: 'national',
        calendar_system: 'Lunisolar profile',
        duration_days: 10,
        tagline: 'Blessing, reunion, and seasonal turning.',
        mythology: {
          summary: 'The observance is tied to renewal, protection, and family blessing.',
          significance: 'Families mark the season through blessing and homecoming.',
        },
        ritual_sequence: {
          days: [
            {
              name: 'Ghatasthapana',
              events: [{ title: 'Kalash Sthapana', description: 'Barley planting begins.' }],
            },
          ],
        },
      },
      dates: {
        start_date: '2026-10-20',
        end_date: '2026-10-30',
        calculation_method: 'lunisolar festival profile',
      },
      nextDates: [
        {
          gregorian_year: 2027,
          start_date: '2027-10-10',
          end_date: '2027-10-20',
          bs_start: { formatted: '2084 Ashwin 23' },
        },
      ],
      nearbyFestivals: [{ id: 'tihar', name: 'Tihar', start_date: '2026-11-07' }],
      completeness: {
        overall: 'complete',
        narrative: {
          status: 'available',
          note: 'Editorial origin, meaning, and contextual notes are published for this observance.',
        },
        ritual_sequence: {
          status: 'available',
          note: 'Structured ritual steps are published for this observance.',
        },
        dates: {
          status: 'available',
          note: 'Resolved calendar dates are available for the requested year.',
        },
        related_observances: {
          status: 'available',
          note: 'Nearby observances are available for the current ritual window.',
        },
      },
    });

    expect(model.title).toBe('Dashain');
    expect(model.profileStatusLabel).toBe('Editorial profile complete');
    expect(model.rituals[0].title).toBe('Kalash Sthapana');
    expect(model.occurrences[0].year).toBe(2027);
    expect(model.related[0].title).toBe('Tihar');
    expect(model.originStatusNote).toMatch(/Editorial origin, meaning, and contextual notes are published/i);
    expect(model.evidence.methodRef).toBe('lunisolar festival profile');
  });

  it('builds my-place from local-first state plus personal context', () => {
    const model = buildConsumerMyPlaceViewModel({
      temporalState,
      memberState: {
        savedPlaces: [{ id: 'ktm', label: 'Kathmandu Home' }],
        reminders: [{ id: 'festival:dashain', title: 'Dashain', date: 'Oct 20' }],
        preferences: { notificationStyle: 'ritual' },
      },
      activePreset: { label: 'Kathmandu' },
      panchanga: {
        tithi: { name: 'Chaturdashi', paksha: 'krishna' },
        nakshatra: { name: 'Shravana', number: 22 },
        yoga: { name: 'Shubha' },
        vaara: { name_english: 'Sunday' },
        local_sunrise: {
          local: '2026-02-15T06:44:00+05:45',
          utc: '2026-02-15T00:59:00Z',
          local_time: '06:44 AM',
        },
        sunrise: {
          local: '2026-02-15T06:42:00+05:45',
          utc: '2026-02-15T00:57:00Z',
          local_time: '06:42 AM',
        },
      },
      contextPayload: {
        context_title: 'Morning Calm',
        context_summary: 'Quiet morning at your saved place.',
        visit_note: 'Saved locally on this device.',
        daily_inspiration: 'Hold the quiet before the day opens.',
        upcoming_reminders: [{ id: 'gion', title: 'Gion Matsuri', date_label: 'Jul 1-31', status: 'Active' }],
      },
      festivals: [{ id: 'dashain', name: 'Dashain' }],
      meta: { method: 'personal place profile' },
    });

    expect(model.placeLabel).toBe('Kathmandu Home');
    expect(model.contextTitle).toBe('Morning Calm');
    expect(model.reminders).toHaveLength(2);
    expect(model.cards[0].label).toBe('What changes here');
    expect(model.sunriseShift).toBe('+2 minutes vs Kathmandu');
    expect(model.localSunrise).toMatch(/6:44 AM/i);
    expect(model.evidence.methodRef).toBe('personal place profile');
  });
});
