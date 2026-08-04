export const DEFAULT_ROUTE_PROFILE = 'developer_preview';

export const ROUTE_PROFILES = Object.freeze({
  minimal_public: { public: true, allowResearchPrivate: false },
  public_demo: { public: true, allowResearchPrivate: false },
  public_reference: { public: true, allowResearchPrivate: false },
  developer_preview: { public: true, allowResearchPrivate: false },
  enterprise_preview: { public: false, allowResearchPrivate: false },
  research_private: { public: false, allowResearchPrivate: true },
  internal_lab: { public: false, allowResearchPrivate: true },
  full_dev: { public: false, allowResearchPrivate: true },
});

export const ROUTE_CAPABILITIES = Object.freeze({
  coreCalendar: {
    lane: 'stable_core',
    maturity: 'stable',
    profiles: ['minimal_public', 'public_demo', 'public_reference', 'developer_preview', 'enterprise_preview', 'full_dev'],
  },
  policyMetadata: {
    lane: 'stable_core',
    maturity: 'stable',
    profiles: ['minimal_public', 'public_demo', 'public_reference', 'developer_preview', 'enterprise_preview', 'full_dev'],
  },
  trustPreview: {
    lane: 'public_preview',
    maturity: 'public_preview',
    profiles: ['public_demo', 'public_reference', 'developer_preview', 'enterprise_preview', 'full_dev'],
  },
  futureBsMethodology: {
    lane: 'public_preview',
    maturity: 'research_preview',
    profiles: ['public_demo', 'public_reference', 'developer_preview', 'enterprise_preview', 'full_dev'],
    exactFutureOutput: 'curated_snapshot',
    researchData: 'public_snapshot',
  },
  festivalTimeline: {
    lane: 'public_preview',
    maturity: 'public_preview',
    profiles: ['public_reference', 'developer_preview', 'enterprise_preview', 'full_dev'],
  },
  placeSearch: {
    lane: 'public_preview',
    maturity: 'public_preview',
    profiles: ['public_reference', 'developer_preview', 'enterprise_preview', 'full_dev'],
  },
  panchangaPublic: {
    lane: 'public_preview',
    maturity: 'public_preview',
    profiles: ['public_reference', 'developer_preview', 'enterprise_preview', 'full_dev'],
  },
  muhurtaPublic: {
    lane: 'public_preview',
    maturity: 'public_preview',
    profiles: ['public_reference', 'developer_preview', 'enterprise_preview', 'full_dev'],
    exactFutureOutput: 'guarded',
  },
  kundaliPreview: {
    lane: 'public_preview',
    maturity: 'public_preview',
    profiles: ['developer_preview', 'enterprise_preview', 'full_dev'],
  },
  integrationsPreview: {
    lane: 'public_preview',
    maturity: 'public_preview',
    profiles: ['developer_preview', 'enterprise_preview', 'full_dev'],
  },
  reliabilityPreview: {
    lane: 'developer_preview',
    maturity: 'developer_preview',
    profiles: ['public_reference', 'developer_preview', 'enterprise_preview', 'full_dev'],
  },
  developerPreview: {
    lane: 'developer_preview',
    maturity: 'developer_preview',
    profiles: ['developer_preview', 'enterprise_preview', 'full_dev'],
  },
  protocolDraft: {
    lane: 'protocol_draft',
    maturity: 'protocol_draft',
    profiles: ['public_reference', 'developer_preview', 'enterprise_preview', 'full_dev'],
  },
  billingEnterprise: {
    lane: 'enterprise_preview',
    maturity: 'enterprise_preview',
    profiles: ['enterprise_preview', 'full_dev'],
    privateData: 'customer_payload',
  },
  futureBsExactPrivate: {
    lane: 'research_private',
    maturity: 'research_preview',
    profiles: ['research_private', 'internal_lab', 'full_dev'],
    exactFutureOutput: true,
    privateData: true,
    researchData: true,
  },
});

export function resolveFrontendProfile(env = import.meta.env) {
  const configured = env?.VITE_PARVA_ROUTE_PROFILE || env?.VITE_ROUTE_PROFILE || env?.PARVA_ROUTE_PROFILE;
  return ROUTE_PROFILES[configured] ? configured : DEFAULT_ROUTE_PROFILE;
}

export function isPublicProfile(profile = resolveFrontendProfile()) {
  return Boolean(ROUTE_PROFILES[profile]?.public);
}

export function getCapability(capabilityId) {
  return ROUTE_CAPABILITIES[capabilityId] || null;
}

export function capabilityEnabled(capabilityId, profile = resolveFrontendProfile()) {
  const capability = getCapability(capabilityId);
  return Boolean(capability && capability.profiles.includes(profile));
}

export function isRouteVisibleInProfile(route, profile = resolveFrontendProfile()) {
  if (!route?.requiredCapability) {
    return true;
  }
  return capabilityEnabled(route.requiredCapability, profile);
}

export function filterRoutesByProfile(routes, profile = resolveFrontendProfile()) {
  return routes.filter((route) => isRouteVisibleInProfile(route, profile));
}

export function getPublicResearchExposureFailures(profile = resolveFrontendProfile()) {
  if (!isPublicProfile(profile)) {
    return [];
  }
  return Object.entries(ROUTE_CAPABILITIES)
    .filter(([, capability]) => capability.profiles.includes(profile))
    .filter(([, capability]) => capability.lane === 'research_private' || capability.exactFutureOutput === true || capability.privateData === true)
    .map(([capabilityId]) => capabilityId);
}

export function assertNoPublicResearchExposure(profile = resolveFrontendProfile()) {
  const failures = getPublicResearchExposureFailures(profile);
  if (failures.length) {
    throw new Error(`Public route profile ${profile} exposes private research capabilities: ${failures.join(', ')}`);
  }
  return true;
}
