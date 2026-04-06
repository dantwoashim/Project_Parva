export function detectDeviceProfile() {
  if (typeof navigator === 'undefined') {
    return {
      platform: 'google',
      title: 'Google Calendar works well from a desktop browser.',
      description: 'Copy the feed link first, then finish the subscription in Google Calendar from URL.',
      badge: 'Desktop-friendly flow',
    };
  }

  const userAgent = navigator.userAgent.toLowerCase();
  const isAppleDevice = /(iphone|ipad|ipod|macintosh|mac os x)/.test(userAgent);
  const isAndroid = /android/.test(userAgent);
  const isMobile = /(iphone|ipad|ipod|android|mobile)/.test(userAgent);

  if (isAppleDevice) {
    return {
      platform: 'apple',
      title: 'This device can open Apple Calendar directly.',
      description: 'Apple devices can subscribe in one jump with the webcal link, so this is the shortest path.',
      badge: 'Best on iPhone, iPad, and Mac',
    };
  }

  if (isAndroid || isMobile) {
    return {
      platform: 'google',
      title: 'Google Calendar still needs one desktop step.',
      description: 'Copy the feed on this device now, then paste it into Google Calendar from a computer browser when you are ready.',
      badge: 'Copy now, finish on desktop',
    };
  }

  return {
    platform: 'google',
    title: 'Google Calendar works well from this browser.',
    description: 'Parva will copy the link first, then open Google Calendar where you can paste it into From URL.',
    badge: 'Best on desktop browsers',
  };
}

export function formatFeedDate(value) {
  if (!value) return 'Not available yet';
  try {
    return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value));
  } catch {
    return value;
  }
}

export function formatDateWindow(windowValue) {
  if (!windowValue?.start || !windowValue?.end) return 'Date window unavailable';
  return `${formatFeedDate(windowValue.start)} - ${formatFeedDate(windowValue.end)}`;
}

export function detectPlatformFamily(platform) {
  if (platform.startsWith('apple')) return 'apple';
  if (platform.startsWith('google')) return 'google';
  return 'manual';
}

export function buildIntegrationId(platform, feedKey, festivalIds = []) {
  if (feedKey === 'custom') {
    const selection = [...festivalIds].sort().join('-') || 'selection';
    return `${platform}-${feedKey}-${selection}`;
  }
  return `${platform}-${feedKey}`;
}

export function integrationPlatformLabel(integration) {
  if (integration.platformFamily === 'apple') return 'Apple Calendar';
  if (integration.platformFamily === 'google') return 'Google Calendar';
  return 'Calendar file or direct feed';
}

export const FALLBACK_PLATFORM_GUIDES = {
  apple: {
    title: 'Apple Calendar',
    badge: 'Best on iPhone, iPad, and Mac',
    description: 'Open the subscription link directly and Apple Calendar handles the rest.',
    cta_label: 'Open in Apple Calendar',
    copy_label: 'Copy Apple subscription link',
    sync_expectation: 'Subscribed calendars usually refresh automatically after you confirm the subscription.',
    steps: [
      'Tap the Apple button.',
      'Confirm the subscription inside Calendar.',
      'Keep the calendar enabled so future updates continue to sync.',
    ],
  },
  google: {
    title: 'Google Calendar',
    badge: 'Desktop browser required',
    description: 'Google subscribes to public calendar feeds from a URL on desktop web.',
    cta_label: 'Copy link and open Google Calendar',
    copy_label: 'Copy Google feed link',
    sync_expectation: 'Google Calendar subscriptions can take several hours to refresh after you add the URL.',
    steps: [
      'Copy the feed link first.',
      'Open Google Calendar on your computer.',
      'Use Other calendars > From URL and paste the link.',
    ],
  },
  manual: {
    title: 'Any calendar app',
    badge: 'Manual or advanced setup',
    description: 'Use the direct feed URL or download an ICS file for other apps and workflows.',
    cta_label: 'Download .ics',
    copy_label: 'Copy direct link',
    sync_expectation: 'Use this route for Outlook, Fantastical, or when you want a one-off ICS file.',
    steps: [
      'Copy the direct calendar link or download the ICS file.',
      'Paste it into Outlook, Fantastical, or another calendar app.',
      'Use the advanced field only when you need the raw link.',
    ],
  },
};

export function buildFallbackPresets(feedAPI, years, lang) {
  return [
    {
      key: 'all',
      title: 'All Festivals',
      description: 'The broadest Parva calendar, best for most personal use.',
      feed_url: feedAPI.getAllLink(years, lang),
      apple_subscribe_url: feedAPI.getAppleSubscribeLink(feedAPI.getAllLink(years, lang)),
      google_copy_url: feedAPI.getAllLink(years, lang),
      download_url: feedAPI.getDownloadLink(feedAPI.getAllLink(years, lang)),
      platform_links: {
        apple: {
          open_url: feedAPI.getAppleSubscribeLink(feedAPI.getAllLink(years, lang)),
          copy_url: feedAPI.getAllLink(years, lang),
          download_url: feedAPI.getDownloadLink(feedAPI.getAllLink(years, lang)),
        },
        google: {
          open_url: feedAPI.getGoogleSetupUrl(),
          copy_url: feedAPI.getAllLink(years, lang),
          download_url: feedAPI.getDownloadLink(feedAPI.getAllLink(years, lang)),
        },
        manual: {
          open_url: feedAPI.getDownloadLink(feedAPI.getAllLink(years, lang)),
          copy_url: feedAPI.getAllLink(years, lang),
          download_url: feedAPI.getDownloadLink(feedAPI.getAllLink(years, lang)),
        },
      },
    },
    {
      key: 'national',
      title: 'National Holidays',
      description: 'A lighter calendar focused on major public observances.',
      feed_url: feedAPI.getNationalLink(years, lang),
      apple_subscribe_url: feedAPI.getAppleSubscribeLink(feedAPI.getNationalLink(years, lang)),
      google_copy_url: feedAPI.getNationalLink(years, lang),
      download_url: feedAPI.getDownloadLink(feedAPI.getNationalLink(years, lang)),
      platform_links: {
        apple: {
          open_url: feedAPI.getAppleSubscribeLink(feedAPI.getNationalLink(years, lang)),
          copy_url: feedAPI.getNationalLink(years, lang),
          download_url: feedAPI.getDownloadLink(feedAPI.getNationalLink(years, lang)),
        },
        google: {
          open_url: feedAPI.getGoogleSetupUrl(),
          copy_url: feedAPI.getNationalLink(years, lang),
          download_url: feedAPI.getDownloadLink(feedAPI.getNationalLink(years, lang)),
        },
        manual: {
          open_url: feedAPI.getDownloadLink(feedAPI.getNationalLink(years, lang)),
          copy_url: feedAPI.getNationalLink(years, lang),
          download_url: feedAPI.getDownloadLink(feedAPI.getNationalLink(years, lang)),
        },
      },
    },
    {
      key: 'newari',
      title: 'Newari Festivals',
      description: 'A focused calendar for Kathmandu Valley and Newar observances.',
      feed_url: feedAPI.getNewariLink(years, lang),
      apple_subscribe_url: feedAPI.getAppleSubscribeLink(feedAPI.getNewariLink(years, lang)),
      google_copy_url: feedAPI.getNewariLink(years, lang),
      download_url: feedAPI.getDownloadLink(feedAPI.getNewariLink(years, lang)),
      platform_links: {
        apple: {
          open_url: feedAPI.getAppleSubscribeLink(feedAPI.getNewariLink(years, lang)),
          copy_url: feedAPI.getNewariLink(years, lang),
          download_url: feedAPI.getDownloadLink(feedAPI.getNewariLink(years, lang)),
        },
        google: {
          open_url: feedAPI.getGoogleSetupUrl(),
          copy_url: feedAPI.getNewariLink(years, lang),
          download_url: feedAPI.getDownloadLink(feedAPI.getNewariLink(years, lang)),
        },
        manual: {
          open_url: feedAPI.getDownloadLink(feedAPI.getNewariLink(years, lang)),
          copy_url: feedAPI.getNewariLink(years, lang),
          download_url: feedAPI.getDownloadLink(feedAPI.getNewariLink(years, lang)),
        },
      },
    },
  ];
}
