import { useMemo } from 'react';
import {
  ROUTE_CAPABILITIES,
  assertNoPublicResearchExposure,
  capabilityEnabled,
  filterRoutesByProfile,
  getCapability,
  getPublicResearchExposureFailures,
  isRouteVisibleInProfile,
  resolveFrontendProfile,
} from '../config/routeCapabilities';

export function useBackendCapabilities(profileOverride) {
  const profile = profileOverride || resolveFrontendProfile();

  return useMemo(() => ({
    profile,
    capabilities: ROUTE_CAPABILITIES,
    getCapability,
    isEnabled: (capabilityId) => capabilityEnabled(capabilityId, profile),
    isRouteVisible: (route) => isRouteVisibleInProfile(route, profile),
    filterRoutes: (routes) => filterRoutesByProfile(routes, profile),
    assertNoPublicResearchExposure: () => assertNoPublicResearchExposure(profile),
    publicResearchExposureFailures: getPublicResearchExposureFailures(profile),
  }), [profile]);
}

export default useBackendCapabilities;
