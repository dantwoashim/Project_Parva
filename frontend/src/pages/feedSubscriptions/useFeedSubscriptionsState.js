import { useEffect, useMemo, useState } from 'react';
import { feedAPI } from '../../services/api';
import {
  buildFallbackPresets,
  buildIntegrationId,
  detectPlatformFamily,
  FALLBACK_PLATFORM_GUIDES,
} from './feedHelpers';

export function useFeedSubscriptionsState({
  festivals,
  deviceProfile,
  integrations,
  startIntegration,
  removeIntegration,
}) {
  const [years, setYears] = useState(2);
  const [lang, setLang] = useState('en');
  const [selectedIds, setSelectedIds] = useState([]);
  const [copied, setCopied] = useState('');
  const [query, setQuery] = useState('');
  const [catalog, setCatalog] = useState(null);
  const [customPlan, setCustomPlan] = useState(null);
  const [setupState, setSetupState] = useState(null);
  const [activePreset, setActivePreset] = useState('all');

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

  const fallbackPresets = useMemo(() => buildFallbackPresets(feedAPI, years, lang), [lang, years]);

  const presets = useMemo(
    () => catalog?.presets || catalog?.data?.presets || fallbackPresets,
    [catalog, fallbackPresets],
  );

  const platformGuides = useMemo(
    () => catalog?.platforms || catalog?.data?.platforms || FALLBACK_PLATFORM_GUIDES,
    [catalog],
  );

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
    () => [...(integrations || [])].sort((left, right) => {
      const parsedLeft = left?.createdAt ? Date.parse(left.createdAt) : 0;
      const parsedRight = right?.createdAt ? Date.parse(right.createdAt) : 0;
      const leftTime = Number.isFinite(parsedLeft) ? parsedLeft : 0;
      const rightTime = Number.isFinite(parsedRight) ? parsedRight : 0;
      return rightTime - leftTime;
    }),
    [integrations],
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
    setSelectedIds((current) => (
      current.includes(id) ? current.filter((value) => value !== id) : [...current, id]
    ));
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

  return {
    years,
    setYears,
    lang,
    setLang,
    selectedIds,
    copied,
    query,
    setQuery,
    filtered,
    presets,
    platformGuides,
    effectiveActivePreset,
    setActivePreset,
    selectedPreset,
    recommendedPlatform,
    orderedPlatforms,
    customLink,
    selectedFestivalNames,
    savedIntegrations,
    setupState,
    resolvedCustomPlan,
    toggleFestival,
    copyLink,
    shareLink,
    handlePresetPlatform,
    handleCustomPlatform,
    reopenSavedIntegration,
    copySavedIntegrationLink,
    removeIntegration,
  };
}
