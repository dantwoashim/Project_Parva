import { useEffect, useMemo, useState } from 'react';
import { UtilityPageHeader } from '../consumer/UtilityPages';
import { feedAPI } from '../services/api';
import { useFestivals } from '../hooks/useFestivals';
import { useMemberContext } from '../context/useMemberContext';
import './FeedSubscriptionsPage.css';

function detectDeviceProfile() {
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

function formatFeedDate(value) {
  if (!value) return 'Not available yet';
  try {
    return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(new Date(value));
  } catch {
    return value;
  }
}

function formatDateWindow(windowValue) {
  if (!windowValue?.start || !windowValue?.end) return 'Date window unavailable';
  return `${formatFeedDate(windowValue.start)} - ${formatFeedDate(windowValue.end)}`;
}

function detectPlatformFamily(platform) {
  if (platform.startsWith('apple')) return 'apple';
  if (platform.startsWith('google')) return 'google';
  return 'manual';
}

function buildIntegrationId(platform, feedKey, festivalIds = []) {
  if (feedKey === 'custom') {
    const selection = [...festivalIds].sort().join('-') || 'selection';
    return `${platform}-${feedKey}-${selection}`;
  }
  return `${platform}-${feedKey}`;
}

function integrationPlatformLabel(integration) {
  if (integration.platformFamily === 'apple') return 'Apple Calendar';
  if (integration.platformFamily === 'google') return 'Google Calendar';
  return 'Calendar file or direct feed';
}

const FALLBACK_PLATFORM_GUIDES = {
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

function FeedPresetCard({ item, isActive, onSelect }) {
  return (
    <button
      type="button"
      className={`feeds-preset ${isActive ? 'feeds-preset--active' : ''}`}
      onClick={() => onSelect(item.key)}
    >
      <span className="feeds-preset__eyebrow">
        {item.key === 'all' ? 'Recommended' : item.category || 'Preset'}
      </span>
      <strong>{item.title}</strong>
      <p>{item.description}</p>
    </button>
  );
}

function PlatformPanel({
  platformKey,
  guide,
  onConnect,
  onCopy,
  onDownload,
  onShare,
  copied,
  recommended,
}) {
  return (
    <article className={`ink-card feeds-platform feeds-platform--${platformKey}`}>
      <div className="feeds-platform__hero">
        <div className="feeds-platform__badges">
          <span className="feeds-platform__badge">{guide.badge}</span>
          {recommended ? <span className="feeds-platform__badge feeds-platform__badge--recommended">Best for this device</span> : null}
        </div>
        <h2>{guide.title}</h2>
        <p>{guide.description}</p>
        {guide.sync_expectation ? <p className="feeds-platform__sync">{guide.sync_expectation}</p> : null}
      </div>

      <div className="feeds-platform__actions">
        <button type="button" className="btn btn-primary btn-sm" onClick={() => onConnect(platformKey)}>
          {guide.cta_label || (platformKey === 'apple' ? 'Open subscription' : platformKey === 'google' ? 'Copy link and open Google Calendar' : 'Open download')}
        </button>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => onCopy(platformKey)}>
          {copied === platformKey ? 'Copied' : guide.copy_label || 'Copy link'}
        </button>
        <button type="button" className="btn btn-secondary btn-sm" onClick={onDownload}>
          Download .ics
        </button>
        <button type="button" className="btn btn-ghost btn-sm" onClick={onShare}>
          Share
        </button>
      </div>

      <ol className="feeds-platform__steps">
        {guide.steps.map((step) => (
          <li key={step}>{step}</li>
        ))}
      </ol>
    </article>
  );
}

function AdvancedLinkField({ label, value }) {
  return (
    <details className="feed-card__advanced">
      <summary>{label}</summary>
      <label className="ink-input feed-card__advanced-field">
        <span>Calendar link</span>
        <input readOnly value={value} onFocus={(event) => event.target.select()} />
      </label>
    </details>
  );
}

function ConnectedIntegrationCard({ integration, onOpen, onCopy, onRemove }) {
  return (
    <article className="ink-card feeds-connection-card">
      <div className="feeds-connection-card__copy">
        <div className="feeds-connection-card__head">
          <span className="feeds-page__eyebrow">Connected</span>
          <strong>{integration.title}</strong>
        </div>
        <p>{integrationPlatformLabel(integration)}</p>
        <div className="feeds-connection-card__meta">
          {integration.feedKind ? <span>{integration.feedKind === 'custom' ? 'Custom feed' : 'Preset feed'}</span> : null}
          {integration.feedTitle ? <span>{integration.feedTitle}</span> : null}
          {integration.selectionCount ? <span>{integration.selectionCount} selected</span> : null}
        </div>
        {integration.nextEvent?.summary ? (
          <p>{`Next: ${integration.nextEvent.summary}${integration.nextEvent.start_date ? ` • ${formatFeedDate(integration.nextEvent.start_date)}` : ''}`}</p>
        ) : null}
        {integration.syncExpectation ? <p>{integration.syncExpectation}</p> : null}
      </div>
      <div className="feeds-connection-card__actions">
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => onOpen(integration)}>
          Reopen
        </button>
        <button type="button" className="btn btn-secondary btn-sm" onClick={() => onCopy(integration)}>
          Copy link
        </button>
        <button type="button" className="btn btn-ghost btn-sm" onClick={() => onRemove(integration)}>
          Remove
        </button>
      </div>
    </article>
  );
}

export function FeedSubscriptionsPage() {
  const { state, startIntegration, removeIntegration } = useMemberContext();
  const [years, setYears] = useState(2);
  const [lang, setLang] = useState('en');
  const [selectedIds, setSelectedIds] = useState([]);
  const [copied, setCopied] = useState('');
  const [query, setQuery] = useState('');
  const [catalog, setCatalog] = useState(null);
  const [customPlan, setCustomPlan] = useState(null);
  const [setupState, setSetupState] = useState(null);

  const { festivals, loading, error } = useFestivals({ qualityBand: 'all', algorithmicOnly: false });
  const deviceProfile = useMemo(() => detectDeviceProfile(), []);

  useEffect(() => {
    let cancelled = false;

    async function loadCatalog() {
      try {
        const payload = await feedAPI.getCatalog({ years, lang });
        if (!cancelled) setCatalog(payload);
      } catch {
        if (!cancelled) setCatalog(null);
      }
    }

    loadCatalog();
    return () => {
      cancelled = true;
    };
  }, [lang, years]);

  const filtered = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    if (!normalized) return festivals;
    return festivals.filter((festival) => `${festival.name} ${festival.name_nepali || ''}`.toLowerCase().includes(normalized));
  }, [festivals, query]);

  const fallbackPresets = useMemo(() => ([
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
  ]), [lang, years]);

  const presets = useMemo(
    () => catalog?.presets || catalog?.data?.presets || fallbackPresets,
    [catalog, fallbackPresets],
  );

  const platformGuides = useMemo(
    () => catalog?.platforms || catalog?.data?.platforms || FALLBACK_PLATFORM_GUIDES,
    [catalog],
  );

  const [activePreset, setActivePreset] = useState('all');
  const effectiveActivePreset = useMemo(
    () => (presets.some((item) => item.key === activePreset) ? activePreset : (presets[0]?.key || 'all')),
    [activePreset, presets],
  );

  const selectedPreset = useMemo(
    () => presets.find((item) => item.key === effectiveActivePreset) || presets[0],
    [effectiveActivePreset, presets],
  );
  const recommendedPlatform = deviceProfile.platform;
  const orderedPlatforms = useMemo(() => {
    const base = ['apple', 'google'];
    return base.sort((left, right) => (left === recommendedPlatform ? -1 : right === recommendedPlatform ? 1 : 0));
  }, [recommendedPlatform]);

  const customLink = useMemo(() => {
    if (!selectedIds.length) return '';
    return feedAPI.getCustomLink(selectedIds, years, lang);
  }, [selectedIds, years, lang]);

  const selectedFestivalNames = useMemo(
    () => festivals.filter((festival) => selectedIds.includes(festival.id)).map((festival) => festival.name),
    [festivals, selectedIds],
  );
  const savedIntegrations = useMemo(
    () => [...(state.integrations || [])].sort((left, right) => {
      const parsedLeft = left?.createdAt ? Date.parse(left.createdAt) : 0;
      const parsedRight = right?.createdAt ? Date.parse(right.createdAt) : 0;
      const leftTime = Number.isFinite(parsedLeft) ? parsedLeft : 0;
      const rightTime = Number.isFinite(parsedRight) ? parsedRight : 0;
      return rightTime - leftTime;
    }),
    [state.integrations],
  );

  useEffect(() => {
    if (!selectedIds.length) {
      return undefined;
    }

    let cancelled = false;

    async function loadCustomPlan() {
      try {
        const payload = await feedAPI.getCustomPlan({ festivalIds: selectedIds, years, lang });
        if (!cancelled) setCustomPlan(payload?.data || payload);
      } catch {
        if (!cancelled) setCustomPlan(null);
      }
    }

    loadCustomPlan();
    return () => {
      cancelled = true;
    };
  }, [lang, years, selectedIds]);

  const resolvedCustomPlan = useMemo(() => {
    if (!customLink) return null;
    if (customPlan?.feed_url) return customPlan;
    return {
      key: 'custom',
      title: 'Custom Calendar',
      description: 'Only the observances you selected, packaged for Apple Calendar, Google Calendar, and direct ICS use.',
      feed_url: customLink,
      download_url: feedAPI.getDownloadLink(customLink),
      apple_subscribe_url: feedAPI.getAppleSubscribeLink(customLink),
      google_copy_url: customLink,
      selection_count: selectedIds.length,
      festival_ids: selectedIds,
      platform_links: {
        apple: {
          open_url: feedAPI.getAppleSubscribeLink(customLink),
          copy_url: customLink,
          download_url: feedAPI.getDownloadLink(customLink),
        },
        google: {
          open_url: feedAPI.getGoogleSetupUrl(),
          copy_url: customLink,
          download_url: feedAPI.getDownloadLink(customLink),
        },
        manual: {
          open_url: feedAPI.getDownloadLink(customLink),
          copy_url: customLink,
          download_url: feedAPI.getDownloadLink(customLink),
        },
      },
    };
  }, [customLink, customPlan, selectedIds]);

  async function copyLink(label, link, successMessage, meta = {}) {
    if (!link) return;
    try {
      await navigator.clipboard.writeText(link);
      setCopied(label);
      setSetupState({
        platform: meta.platform || 'manual',
        title: meta.title || 'Link copied',
        body: successMessage || 'Calendar link copied.',
      });
      setTimeout(() => setCopied(''), 1500);
    } catch {
      setCopied('');
      setSetupState({
        platform: meta.platform || 'manual',
        title: 'Copy failed',
        body: 'Clipboard access was blocked on this device, so use the advanced field below and copy the link manually.',
      });
    }
  }

  function toggleFestival(id) {
    setSelectedIds((current) => {
      if (current.includes(id)) {
        return current.filter((value) => value !== id);
      }
      return [...current, id];
    });
  }

  async function shareLink(title, link) {
    if (!link) return;
    if (typeof navigator.share === 'function') {
      try {
        await navigator.share({ title, url: link });
        setSetupState({
          platform: 'manual',
          title: 'Share sheet opened',
          body: 'You can send the calendar link to another device or person from here.',
        });
        return;
      } catch {
        // Fall back to copy if the user dismisses or the platform blocks sharing.
      }
    }
    await copyLink(`${title}-share`, link, 'Calendar link copied so you can share it anywhere.', {
      platform: 'manual',
      title: 'Link ready to share',
    });
  }

  async function openIntegration({ integrationId, platform, title, link, openUrl, note, integrationMeta = {} }) {
    const platformFamily = detectPlatformFamily(platform);
    const allowed = await startIntegration({
      id: integrationId || `${platform}-${activePreset}`,
      platform,
      platformFamily,
      title,
      link,
      createdAt: new Date().toISOString(),
      ...integrationMeta,
    });

    if (!allowed) return;

    if (openUrl && typeof window.open === 'function') {
      window.open(openUrl, '_blank', 'noreferrer');
    }
    if (note) {
      setSetupState({
        platform,
        title,
        body: note,
      });
    }
  }

  async function reopenSavedIntegration(integration) {
    if (integration.link && typeof window.open === 'function') {
      window.open(integration.link, '_blank', 'noreferrer');
    }
    setSetupState({
      platform: integration.platformFamily || detectPlatformFamily(integration.platform),
      title: integration.title,
      body: integration.platformFamily === 'google'
        ? 'If Google Calendar is open, paste the copied link into From URL to finish or refresh the subscription.'
        : 'Your saved calendar connection reopened in a new tab.',
    });
  }

  async function copySavedIntegrationLink(integration) {
    const value = integration.feedUrl || integration.link;
    if (!value) return;
    await copyLink(integration.id || integration.title, value, 'Saved calendar link copied.', {
      platform: integration.platformFamily || detectPlatformFamily(integration.platform),
      title: 'Saved link copied',
    });
  }

  async function handlePresetPlatform(platform) {
    if (!selectedPreset) return;

    const platformGuide = platformGuides[platform] || FALLBACK_PLATFORM_GUIDES[platform];
    const appleLink = selectedPreset.platform_links?.apple?.open_url
      || selectedPreset.apple_subscribe_url
      || feedAPI.getAppleSubscribeLink(selectedPreset.feed_url);
    const googleLink = selectedPreset.platform_links?.google?.copy_url
      || selectedPreset.google_copy_url
      || selectedPreset.feed_url;
    const googleOpenUrl = selectedPreset.platform_links?.google?.open_url || feedAPI.getGoogleSetupUrl();
    const downloadLink = selectedPreset.platform_links?.manual?.download_url
      || selectedPreset.download_url
      || feedAPI.getDownloadLink(selectedPreset.feed_url);

    if (platform === 'apple') {
      await openIntegration({
        integrationId: buildIntegrationId('apple', selectedPreset.key, selectedPreset.festival_ids || []),
        platform: 'apple',
        title: `${selectedPreset.title} for Apple Calendar`,
        link: appleLink,
        openUrl: appleLink,
        note: 'Apple Calendar subscription opened. Confirm the subscription in Calendar to finish setup.',
        integrationMeta: {
          feedKind: 'preset',
          feedKey: selectedPreset.key,
          feedTitle: selectedPreset.title,
          feedUrl: selectedPreset.feed_url,
          downloadUrl: downloadLink,
          years,
          lang,
          recommendedPlatform,
          selectionCount: selectedPreset.selection_count || 0,
          syncExpectation: platformGuide?.sync_expectation || null,
          nextEvent: selectedPreset.stats?.next_event || null,
          dateWindow: selectedPreset.stats?.date_window || null,
        },
      });
      return;
    }

    if (platform === 'google') {
      await copyLink('google', googleLink, 'Feed link copied. Paste it into Google Calendar > Other calendars > From URL on desktop.', {
        platform: 'google',
        title: 'Google feed copied',
      });
      await openIntegration({
        integrationId: buildIntegrationId('google', selectedPreset.key, selectedPreset.festival_ids || []),
        platform: 'google',
        title: `${selectedPreset.title} for Google Calendar`,
        link: googleLink,
        openUrl: googleOpenUrl,
        note: 'Google Calendar opened. Paste the copied link into the From URL field to subscribe.',
        integrationMeta: {
          feedKind: 'preset',
          feedKey: selectedPreset.key,
          feedTitle: selectedPreset.title,
          feedUrl: selectedPreset.feed_url,
          downloadUrl: downloadLink,
          years,
          lang,
          recommendedPlatform,
          selectionCount: selectedPreset.selection_count || 0,
          syncExpectation: platformGuide?.sync_expectation || null,
          nextEvent: selectedPreset.stats?.next_event || null,
          dateWindow: selectedPreset.stats?.date_window || null,
        },
      });
      return;
    }

    await openIntegration({
      integrationId: buildIntegrationId('manual', selectedPreset.key, selectedPreset.festival_ids || []),
      platform: 'manual',
      title: `${selectedPreset.title} download`,
      link: downloadLink,
      openUrl: downloadLink,
      note: 'The ICS download opened in a new tab.',
      integrationMeta: {
        feedKind: 'preset',
        feedKey: selectedPreset.key,
        feedTitle: selectedPreset.title,
        feedUrl: selectedPreset.feed_url,
        downloadUrl: downloadLink,
        years,
        lang,
        recommendedPlatform,
        selectionCount: selectedPreset.selection_count || 0,
        syncExpectation: platformGuide?.sync_expectation || null,
        nextEvent: selectedPreset.stats?.next_event || null,
        dateWindow: selectedPreset.stats?.date_window || null,
      },
    });
  }

  async function handleCustomPlatform(platform) {
    if (!resolvedCustomPlan) return;

    const platformGuide = platformGuides[platform] || FALLBACK_PLATFORM_GUIDES[platform];
    const appleLink = resolvedCustomPlan.platform_links?.apple?.open_url || feedAPI.getAppleSubscribeLink(customLink);
    const googleLink = resolvedCustomPlan.platform_links?.google?.copy_url || customLink;
    const googleOpenUrl = resolvedCustomPlan.platform_links?.google?.open_url || feedAPI.getGoogleSetupUrl();
    const downloadLink = resolvedCustomPlan.platform_links?.manual?.download_url || feedAPI.getDownloadLink(customLink);
    const integrationMeta = {
      feedKind: 'custom',
      feedKey: 'custom',
      feedTitle: resolvedCustomPlan.title,
      feedUrl: resolvedCustomPlan.feed_url,
      downloadUrl: downloadLink,
      years,
      lang,
      recommendedPlatform,
      selectionCount: resolvedCustomPlan.selection_count || selectedIds.length,
      selectedFestivalNames: selectedFestivalNames.slice(0, 8),
      syncExpectation: platformGuide?.sync_expectation || null,
      nextEvent: resolvedCustomPlan.stats?.next_event || null,
      dateWindow: resolvedCustomPlan.stats?.date_window || null,
    };

    if (platform === 'apple') {
      await openIntegration({
        integrationId: buildIntegrationId('apple', 'custom', selectedIds),
        platform: 'apple-custom',
        title: 'Custom calendar for Apple Calendar',
        link: appleLink,
        openUrl: appleLink,
        note: 'Custom Apple subscription opened. Confirm it in Calendar to start syncing.',
        integrationMeta,
      });
      return;
    }

    if (platform === 'google') {
      await copyLink('google-custom', googleLink, 'Custom feed copied. Paste it into Google Calendar > From URL on desktop.', {
        platform: 'google',
        title: 'Custom Google feed copied',
      });
      await openIntegration({
        integrationId: buildIntegrationId('google', 'custom', selectedIds),
        platform: 'google-custom',
        title: 'Custom calendar for Google Calendar',
        link: googleLink,
        openUrl: googleOpenUrl,
        note: 'Google Calendar opened. Paste the copied custom link into the From URL field.',
        integrationMeta,
      });
      return;
    }

    await openIntegration({
      integrationId: buildIntegrationId('manual', 'custom', selectedIds),
      platform: 'manual-custom',
      title: 'Custom calendar download',
      link: downloadLink,
      openUrl: downloadLink,
      note: 'The custom ICS download opened in a new tab.',
      integrationMeta,
    });
  }

  return (
    <section className="feeds-page utility-page animate-fade-in-up">
      <UtilityPageHeader
        eyebrow="Calendar integrations"
        title="Connect Parva without dealing with raw calendar plumbing first."
        body="Choose the calendar you already use, pick a preset, and follow the shortest path. Apple opens directly. Google gets the link copied first because Google still asks for the URL in a desktop browser."
        links={[
          { label: 'Saved', to: '/#saved' },
          { label: 'Profile', to: '/profile' },
          { label: 'Methodology', to: '/methodology' },
        ]}
        aside={(
          <div className="feeds-hero__controls">
            <label className="ink-input">
              <span>Years</span>
              <select value={years} onChange={(event) => setYears(Number(event.target.value))}>
                {[1, 2, 3, 4, 5].map((value) => (
                  <option key={value} value={value}>{value}</option>
                ))}
              </select>
            </label>
            <label className="ink-input">
              <span>Language</span>
              <select value={lang} onChange={(event) => setLang(event.target.value)}>
                <option value="en">English</option>
                <option value="ne">Nepali</option>
              </select>
            </label>
          </div>
        )}
      />

      <section className="ink-card feeds-premium-panel">
        <div className="feeds-premium-panel__top">
          <div>
            <p className="feeds-page__eyebrow">Pick your calendar pack</p>
            <h2>Start with a polished preset, then switch to a custom feed only if you need it.</h2>
          </div>
          <div className="feeds-premium-panel__meta">
            <span>{years} year sync window</span>
            <span>{lang === 'ne' ? 'Nepali labels' : 'English labels'}</span>
          </div>
        </div>

        <div className="feeds-presets" role="tablist" aria-label="Calendar feed presets">
          {presets.map((item) => (
            <FeedPresetCard key={item.key} item={item} isActive={item.key === effectiveActivePreset} onSelect={setActivePreset} />
          ))}
        </div>

        {selectedPreset ? (
          <section className="feeds-selected">
            <div className="feeds-selected__summary">
              <span className="feeds-page__eyebrow">Selected preset</span>
              <h3>{selectedPreset.title}</h3>
              <p>{selectedPreset.description}</p>
            </div>

            <section className="ink-card feeds-device-spotlight">
              <div className="feeds-device-spotlight__copy">
                <span className="feeds-page__eyebrow">Recommended next step</span>
                <h3>{deviceProfile.title}</h3>
                <p>{deviceProfile.description}</p>
              </div>
              <div className="feeds-device-spotlight__actions">
                <span className="feeds-platform__badge">{deviceProfile.badge}</span>
                <button type="button" className="btn btn-primary btn-sm" onClick={() => handlePresetPlatform(recommendedPlatform)}>
                  {(platformGuides[recommendedPlatform] || FALLBACK_PLATFORM_GUIDES[recommendedPlatform])?.cta_label || 'Continue'}
                </button>
              </div>
            </section>

            {selectedPreset.stats ? (
              <div className="feeds-selected__stats">
                <article className="ink-card feeds-stat">
                  <span>Events in this feed</span>
                  <strong>{selectedPreset.stats.event_count}</strong>
                </article>
                <article className="ink-card feeds-stat">
                  <span>Calendar window</span>
                  <strong>{formatDateWindow(selectedPreset.stats.date_window)}</strong>
                </article>
                <article className="ink-card feeds-stat">
                  <span>Next observance</span>
                  <strong>
                    {selectedPreset.stats.next_event
                      ? `${selectedPreset.stats.next_event.summary} • ${formatFeedDate(selectedPreset.stats.next_event.start_date)}`
                      : 'No upcoming event in this window'}
                  </strong>
                </article>
              </div>
            ) : null}

            {selectedPreset.stats?.highlights?.length ? (
              <div className="feeds-highlights" aria-label="Feed highlights">
                {selectedPreset.stats.highlights.map((highlight) => (
                  <span key={`${highlight.summary}-${highlight.start_date}`} className="feeds-highlight-chip">
                    {highlight.summary} • {formatFeedDate(highlight.start_date)}
                  </span>
                ))}
              </div>
            ) : null}

            <div className="feeds-platform-grid">
              {orderedPlatforms.map((platformKey) => {
                const guide = platformGuides[platformKey] || FALLBACK_PLATFORM_GUIDES[platformKey];
                const copyValue = selectedPreset.platform_links?.[platformKey]?.copy_url
                  || (platformKey === 'google' ? selectedPreset.google_copy_url : selectedPreset.feed_url)
                  || selectedPreset.feed_url;
                return (
                  <PlatformPanel
                    key={platformKey}
                    platformKey={platformKey}
                    guide={guide}
                    copied={copied}
                    recommended={platformKey === recommendedPlatform}
                    onConnect={handlePresetPlatform}
                    onCopy={() => copyLink(platformKey, copyValue, `${guide.title} link copied.`, {
                      platform: platformKey,
                      title: `${guide.title} link copied`,
                    })}
                    onDownload={() => handlePresetPlatform('manual')}
                    onShare={() => shareLink(`${selectedPreset.title} calendar`, selectedPreset.feed_url)}
                  />
                );
              })}
            </div>

            <div className="feeds-manual-grid">
              <article className="ink-card feeds-manual-card">
                <span className="feeds-page__eyebrow">Direct links</span>
                <h3>Manual and advanced setup</h3>
                <p>Use these when you want the raw feed or a downloaded ICS file for another app.</p>
                <div className="feeds-manual-card__actions">
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => copyLink('manual', selectedPreset.feed_url, 'Direct calendar link copied.', {
                    platform: 'manual',
                    title: 'Direct feed copied',
                  })}>
                    {copied === 'manual' ? 'Copied' : 'Copy direct link'}
                  </button>
                  <button type="button" className="btn btn-secondary btn-sm" onClick={() => window.open(selectedPreset.download_url || feedAPI.getDownloadLink(selectedPreset.feed_url), '_blank', 'noreferrer')}>
                    Download .ics
                  </button>
                </div>
                <AdvancedLinkField label="Show advanced manual setup" value={selectedPreset.feed_url} />
              </article>

              {setupState ? (
                <aside className="feeds-setup-note" role="status" aria-live="polite">
                  <span className="feeds-page__eyebrow">Setup note</span>
                  <strong>{setupState.title}</strong>
                  <p>{setupState.body}</p>
                </aside>
              ) : null}
            </div>
          </section>
        ) : null}
      </section>

      <section className="ink-card feeds-connections">
        <div className="feeds-connections__header">
          <div>
            <p className="feeds-page__eyebrow">Connected calendars</p>
            <h2>Reopen, copy, or clean up the calendars you already connected.</h2>
          </div>
          <span className="feeds-platform__badge">{savedIntegrations.length} saved</span>
        </div>

        {savedIntegrations.length ? (
          <div className="feeds-connections__grid">
            {savedIntegrations.map((integration) => (
              <ConnectedIntegrationCard
                key={integration.id || integration.platform}
                integration={integration}
                onOpen={reopenSavedIntegration}
                onCopy={copySavedIntegrationLink}
                onRemove={(entry) => removeIntegration(entry.id || entry.platform)}
              />
            ))}
          </div>
        ) : (
          <article className="feeds-connections__empty">
            <strong>No calendar connections yet</strong>
            <p>Use one of the Apple, Google, or manual actions above and it will show up here with the next step, feed details, and quick reopen actions.</p>
          </article>
        )}
      </section>

      <section className="ink-card feeds-custom utility-page__panel">
        <div className="feeds-custom__header">
          <div>
            <p className="feeds-page__eyebrow">Build your own</p>
            <h2>Make a smaller calendar for the observances you follow closely.</h2>
          </div>
          <p>Choose specific observances, then use the same Apple, Google, or manual setup flow with a custom feed.</p>
        </div>

        <label className="ink-input feeds-custom__search">
          <span>Search festivals</span>
          <input
            type="search"
            placeholder="Dashain, Teej, Shivaratri..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </label>

        {loading ? <p className="feeds-custom__status">Loading festivals...</p> : null}
        {!loading && error ? <p className="feeds-custom__status" role="alert">{error}</p> : null}
        {!loading && !error ? (
          <div className="feeds-picker" role="group" aria-label="Festival selector">
            {filtered.slice(0, 60).map((festival) => (
              <label key={festival.id} className="feeds-picker__item">
                <input
                  type="checkbox"
                  checked={selectedIds.includes(festival.id)}
                  onChange={() => toggleFestival(festival.id)}
                />
                <span>{festival.name}</span>
              </label>
            ))}
          </div>
        ) : null}

        <div className="feeds-custom__output">
          <div className="feeds-custom__summary">
            <span>Selected festivals</span>
            <strong>{selectedIds.length}</strong>
          </div>

          {customLink ? (
            <div className="feeds-custom__actions">
              <div className="ink-card feeds-custom-plan">
                <div className="feeds-custom-plan__copy">
                  <span className="feeds-page__eyebrow">Custom feed ready</span>
                  <h3>{resolvedCustomPlan?.title || 'Custom Calendar'}</h3>
                  <p>{resolvedCustomPlan?.description || 'Use the same polished Apple, Google, and manual flow for the observances you selected.'}</p>
                </div>
                <div className="feeds-custom-plan__stats">
                  <span>{resolvedCustomPlan?.selection_count || selectedIds.length} selected</span>
                  <span>{formatDateWindow(resolvedCustomPlan?.stats?.date_window)}</span>
                  <span>
                    {resolvedCustomPlan?.stats?.next_event
                      ? `${resolvedCustomPlan.stats.next_event.summary} • ${formatFeedDate(resolvedCustomPlan.stats.next_event.start_date)}`
                      : 'Building your next observance preview'}
                  </span>
                </div>
                {selectedFestivalNames.length ? (
                  <div className="feeds-highlights">
                    {selectedFestivalNames.slice(0, 6).map((name) => (
                      <span key={name} className="feeds-highlight-chip">{name}</span>
                    ))}
                  </div>
                ) : null}
              </div>
              <div className="feeds-custom__cta-row">
                <button type="button" className="btn btn-primary btn-sm" onClick={() => handleCustomPlatform('apple')}>
                  Open in Apple Calendar
                </button>
                <button type="button" className="btn btn-primary btn-sm" onClick={() => handleCustomPlatform('google')}>
                  Copy for Google Calendar
                </button>
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => handleCustomPlatform('manual')}>
                  Download .ics
                </button>
              </div>
              <div className="feeds-custom__secondary-row">
                <button type="button" className="btn btn-secondary btn-sm" onClick={() => copyLink('Custom feed', customLink, 'Custom feed copied.', {
                  platform: 'manual',
                  title: 'Custom feed copied',
                })}>
                  {copied === 'Custom feed' ? 'Copied' : 'Copy direct link'}
                </button>
                <button type="button" className="btn btn-ghost btn-sm" onClick={() => shareLink('Custom calendar', customLink)}>
                  Share custom link
                </button>
              </div>
              <AdvancedLinkField label="Advanced manual setup" value={customLink} />
            </div>
          ) : (
            <p className="feeds-custom__hint">Select at least one festival above to generate a custom feed.</p>
          )}
        </div>
      </section>
    </section>
  );
}

export const IntegrationsPage = FeedSubscriptionsPage;

export default FeedSubscriptionsPage;
