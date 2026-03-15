const EVENT_TARGET = 'parva:analytics';

export function trackEvent(event, properties = {}) {
  if (typeof window === 'undefined') return;

  const payload = {
    event,
    properties,
    timestamp: new Date().toISOString(),
  };

  const queue = Array.isArray(window.parvaAnalytics) ? window.parvaAnalytics : [];
  window.parvaAnalytics = [...queue, payload];

  try {
    window.dispatchEvent(new CustomEvent(EVENT_TARGET, { detail: payload }));
  } catch {
    // Ignore analytics dispatch issues in non-browser test environments.
  }

  if (import.meta.env.DEV) {
    console.debug('[parva analytics]', payload);
  }
}

export function getAnalyticsEventTarget() {
  return EVENT_TARGET;
}
