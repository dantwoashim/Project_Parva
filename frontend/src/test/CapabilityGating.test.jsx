import {
  ROUTE_CAPABILITIES,
  assertNoPublicResearchExposure,
  capabilityEnabled,
  filterRoutesByProfile,
  getPublicResearchExposureFailures,
} from '../config/routeCapabilities';
import {
  getFooterGroups,
  getPrimaryNavItems,
  getSearchCommands,
} from '../navigation/routeManifest';

function copy(key) {
  const labels = {
    'common.today': 'Today',
    'common.myPlace': 'My Place',
    'common.festivals': 'Festivals',
    'common.bestTime': 'Best Time',
    'common.birthReading': 'Birth Reading',
    'common.integrations': 'Integrations',
    'common.trust': 'Trust',
    'common.methodology': 'Methodology',
    'common.truthLab': 'Truth Lab',
    'common.apiPolicy': 'API Policy',
    'common.panchanga': 'Panchanga',
    'footer.consumer': 'Consumer',
    'footer.utilities': 'Utilities',
    'search.kind.page': 'Page',
    'search.kind.betaPage': 'Beta page',
    'search.kind.supportPage': 'Support page',
  };
  return labels[key] || key;
}

describe('route capability gating', () => {
  it('keeps private future-BS exact outputs out of public profiles', () => {
    ['minimal_public', 'public_demo', 'public_reference', 'developer_preview'].forEach((profile) => {
      expect(getPublicResearchExposureFailures(profile)).toEqual([]);
      expect(() => assertNoPublicResearchExposure(profile)).not.toThrow();
      expect(capabilityEnabled('futureBsExactPrivate', profile)).toBe(false);
    });
  });

  it('allows future-BS methodology without exact future output in public profiles', () => {
    expect(capabilityEnabled('futureBsMethodology', 'public_reference')).toBe(true);
    expect(ROUTE_CAPABILITIES.futureBsMethodology.exactFutureOutput).toBe(false);
    expect(ROUTE_CAPABILITIES.futureBsMethodology.researchData).toBe('metadata_only');
  });

  it('filters route manifests by backend route profile', () => {
    const publicDemoNav = getPrimaryNavItems(copy, { profile: 'public_demo' }).map((route) => route.label);
    expect(publicDemoNav).toEqual(['Today']);

    const developerNav = getPrimaryNavItems(copy, { profile: 'developer_preview' }).map((route) => route.label);
    expect(developerNav).toEqual(['Today', 'My Place', 'Festivals', 'Best Time', 'Birth Reading']);
  });

  it('keeps unsupported footer and search links out of public-demo profile', () => {
    const footerLinks = getFooterGroups(copy, { profile: 'public_demo' })
      .flatMap((group) => group.links.map((link) => link.label));
    expect(footerLinks).toContain('Today');
    expect(footerLinks).toContain('Trust');
    expect(footerLinks).not.toContain('Birth Reading');
    expect(footerLinks).not.toContain('Integrations');

    const searchLabels = getSearchCommands(copy, { includeSupport: true, profile: 'public_demo' })
      .map((command) => command.label);
    expect(searchLabels).toContain('Today');
    expect(searchLabels).toContain('Trust');
    expect(searchLabels).not.toContain('Birth Reading');
  });

  it('keeps billing API controls outside public profiles', () => {
    const links = filterRoutesByProfile([
      { label: 'Pricing', to: '/pricing', requiredCapability: 'billingEnterprise' },
      { label: 'Policy', to: '/policy', requiredCapability: 'policyMetadata' },
    ], 'public_reference');

    expect(links.map((link) => link.label)).toEqual(['Policy']);
    expect(capabilityEnabled('billingEnterprise', 'enterprise_preview')).toBe(true);
  });
});
