(function () {
  const widgetMap = {
    'temporal-compass': 'temporal-compass.html',
    'upcoming-festivals': 'upcoming-festivals.html',
  };

  function ownScript() {
    return document.currentScript || document.querySelector('script[src*="parva-embed.js"]');
  }

  function baseUrl() {
    const script = ownScript();
    if (!script) {
      return null;
    }
    return new URL('.', script.src);
  }

  function buildSrc(widgetName, dataset) {
    const fileName = widgetMap[widgetName];
    const base = baseUrl();
    if (!fileName || !base) {
      return null;
    }

    const url = new URL(fileName, base);
    Object.entries(dataset).forEach(([key, value]) => {
      if (!value || key === 'parvaWidget' || key === 'height' || key === 'parvaMounted') {
        return;
      }
      const queryKey = key.replace(/[A-Z]/g, (char) => `_${char.toLowerCase()}`);
      url.searchParams.set(queryKey, value);
    });
    return url.toString();
  }

  function mount(target) {
    if (!target || target.dataset.parvaMounted === 'true') {
      return;
    }

    const widgetName = target.dataset.parvaWidget;
    const src = buildSrc(widgetName, target.dataset);
    if (!src) {
      return;
    }

    const iframe = document.createElement('iframe');
    iframe.src = src;
    iframe.loading = 'lazy';
    iframe.referrerPolicy = 'strict-origin-when-cross-origin';
    iframe.title = `Project Parva ${widgetName}`;
    iframe.width = '100%';
    iframe.height = target.dataset.height || (widgetName === 'upcoming-festivals' ? '420' : '320');
    iframe.style.border = '0';
    iframe.style.width = '100%';
    iframe.style.display = 'block';
    iframe.style.background = 'transparent';

    target.replaceChildren(iframe);
    target.dataset.parvaMounted = 'true';
  }

  function mountAll() {
    document.querySelectorAll('[data-parva-widget]').forEach(mount);
  }

  window.ParvaEmbed = { mount, mountAll };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mountAll, { once: true });
  } else {
    mountAll();
  }
})();
