import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import '@fontsource-variable/manrope';
import '@fontsource/ibm-plex-mono/latin-400.css';
import '@fontsource/ibm-plex-mono/latin-500.css';
import '@fontsource/ibm-plex-mono/latin-600.css';
import '@fontsource/ibm-plex-mono/latin-700.css';
import '@fontsource-variable/noto-sans-devanagari';
import App from './App.jsx';

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    // Register for production builds; keep dev deterministic.
    const isLocalhost = ['localhost', '127.0.0.1'].includes(window.location.hostname);
    if (!isLocalhost) {
      navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' }).then((registration) => {
        registration.update().catch(() => {});
      }).catch(() => {
        // Ignore SW registration failures.
      });
    }
  });
}

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>,
);
