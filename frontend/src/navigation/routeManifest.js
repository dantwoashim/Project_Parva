const ROUTE_MANIFEST = [
  {
    id: 'today',
    to: '/today',
    labelKey: 'common.today',
    tier: 'launch-critical',
    keywords: 'today daily now temporal compass',
    metaKey: 'search.command.today.meta',
    icon: 'today',
    primaryNav: true,
    sideRail: true,
    bottomNav: true,
    footerGroup: 'consumer',
    searchDefault: true,
  },
  {
    id: 'my-place',
    to: '/my-place',
    labelKey: 'common.myPlace',
    tier: 'launch-critical',
    keywords: 'place location sunrise city personal panchanga',
    metaKey: 'search.command.myPlace.meta',
    icon: 'location_on',
    primaryNav: true,
    sideRail: true,
    bottomNav: true,
    footerGroup: 'consumer',
    searchDefault: true,
  },
  {
    id: 'festivals',
    to: '/festivals',
    labelKey: 'common.festivals',
    tier: 'launch-critical',
    keywords: 'festivals observances calendar',
    metaKey: 'search.command.festivals.meta',
    icon: 'explore',
    primaryNav: true,
    sideRail: true,
    bottomNav: true,
    footerGroup: 'consumer',
    searchDefault: true,
  },
  {
    id: 'muhurta',
    to: '/best-time',
    labelKey: 'common.bestTime',
    tier: 'launch-critical',
    keywords: 'muhurta best time timing',
    metaKey: 'search.command.bestTime.meta',
    icon: 'auto_awesome',
    primaryNav: true,
    sideRail: true,
    bottomNav: true,
    footerGroup: 'consumer',
    searchDefault: true,
  },
  {
    id: 'kundali',
    to: '/birth-reading',
    labelKey: 'common.birthReading',
    tier: 'launch-critical',
    keywords: 'birth reading kundali chart',
    metaKey: 'search.command.birthReading.meta',
    icon: 'flare',
    primaryNav: true,
    sideRail: true,
    bottomNav: true,
    footerGroup: 'consumer',
    searchDefault: true,
  },
  {
    id: 'saved',
    to: '/saved',
    labelKey: 'common.saved',
    tier: 'support',
    keywords: 'saved reminders places readings integrations',
    metaKey: 'search.command.saved.meta',
    footerGroup: 'utilities',
  },
  {
    id: 'profile',
    to: '/profile',
    labelKey: 'common.profile',
    tier: 'support',
    keywords: 'profile preferences saved local export import backup',
    metaKey: 'search.command.profile.meta',
    footerGroup: 'utilities',
  },
  {
    id: 'integrations',
    to: '/integrations',
    labelKey: 'common.integrations',
    tier: 'beta',
    keywords: 'calendar sync feeds',
    metaKey: 'search.command.integrations.meta',
    footerGroup: 'utilities',
  },
  {
    id: 'methodology',
    to: '/methodology',
    labelKey: 'common.methodology',
    tier: 'support',
    keywords: 'trust method evidence',
    metaKey: 'search.command.methodology.meta',
    footerGroup: 'utilities',
  },
  {
    id: 'about',
    to: '/about',
    labelKey: 'common.about',
    tier: 'support',
    keywords: 'about parva help',
    metaKey: 'search.command.about.meta',
    footerGroup: 'utilities',
  },
  {
    id: 'panchanga',
    to: '/panchanga',
    labelKey: 'common.panchanga',
    tier: 'deferred',
    keywords: 'panchanga almanac calendar daily details',
    metaKey: 'search.command.panchanga.meta',
  },
];

function matchesPath(pathname, routePath) {
  if (routePath === '/') {
    return pathname === '/';
  }
  return pathname === routePath || pathname.startsWith(`${routePath}/`);
}

function translatedRoute(route, copy) {
  return {
    ...route,
    label: copy(route.labelKey),
  };
}

function searchKindForTier(tier, copy) {
  if (tier === 'beta') {
    return copy('search.kind.betaPage');
  }
  if (tier === 'support' || tier === 'deferred') {
    return copy('search.kind.supportPage');
  }
  return copy('search.kind.page');
}

export function getPrimaryNavItems(copy) {
  return ROUTE_MANIFEST.filter((route) => route.primaryNav).map((route) => translatedRoute(route, copy));
}

export function getSideRailItems(copy) {
  return ROUTE_MANIFEST.filter((route) => route.sideRail).map((route) => translatedRoute(route, copy));
}

export function getBottomNavItems(copy) {
  return ROUTE_MANIFEST.filter((route) => route.bottomNav).map((route) => translatedRoute(route, copy));
}

export function getSupportNavItems(copy) {
  return ROUTE_MANIFEST
    .filter((route) => route.tier !== 'launch-critical' && route.tier !== 'deferred')
    .map((route) => translatedRoute(route, copy));
}

export function getFooterGroups(copy) {
  const groups = [
    { key: 'consumer', title: copy('footer.consumer') },
    { key: 'utilities', title: copy('footer.utilities') },
  ];

  return groups.map((group) => ({
    title: group.title,
    links: ROUTE_MANIFEST
      .filter((route) => route.footerGroup === group.key)
      .map((route) => ({
        label: copy(route.labelKey),
        to: route.to,
      })),
  }));
}

export function getSearchCommands(copy, { includeSupport = false } = {}) {
  return ROUTE_MANIFEST
    .filter((route) => route.searchDefault || includeSupport)
    .filter((route) => route.tier !== 'deferred' || includeSupport)
    .map((route) => ({
      to: route.to,
      label: copy(route.labelKey),
      keywords: route.keywords,
      kind: searchKindForTier(route.tier, copy),
      meta: copy(route.metaKey),
    }));
}

export function getActiveLaunchSection(pathname) {
  const active = ROUTE_MANIFEST.find(
    (route) => route.tier === 'launch-critical' && matchesPath(pathname, route.to),
  );
  return active?.id || null;
}

export function getSurfaceDescriptor(pathname, copy) {
  const route = ROUTE_MANIFEST.find((candidate) => matchesPath(pathname, candidate.to));
  if (!route || route.tier === 'launch-critical') {
    return null;
  }

  return {
    id: route.id,
    tier: route.tier,
    label: copy(route.labelKey),
    title: copy(`shell.surface.${route.tier}.title`),
    body: copy(`shell.surface.${route.tier}.body`),
    links: getPrimaryNavItems(copy).map((item) => ({ label: item.label, to: item.to })),
  };
}
