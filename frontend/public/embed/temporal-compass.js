function todayIso(timeZone) {
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
  const parts = Object.fromEntries(
    formatter.formatToParts(new Date()).map((part) => [part.type, part.value]),
  );
  return parts.year + '-' + parts.month + '-' + parts.day;
}

function params() {
  return new URLSearchParams(window.location.search);
}

function apiBase(query) {
  const configured = document.body.dataset.apiBase || query.get('api_base');
  return (configured || 'https://api.prabinghimire1.com.np/v3/api').replace(/\/+$/, '');
}

function text(id, value) {
  document.getElementById(id).textContent = value || '-';
}

function formatBs(bs) {
  if (!bs) return '-';
  if (bs.formatted) return bs.formatted;
  if (bs.year && bs.month_name && bs.day) return bs.year + ' ' + bs.month_name + ' ' + bs.day;
  return '-';
}

function formatTime(value, timeZone) {
  if (!value) return '-';

  const timestamp = typeof value === 'object'
    ? value.local || value.utc
    : value;
  if (!timestamp) {
    return typeof value === 'object' && value.local_time ? value.local_time : '-';
  }

  const parsed = new Date(timestamp);
  if (Number.isNaN(parsed.getTime())) return '-';

  return parsed.toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
    hour12: true,
    timeZone,
  });
}

async function loadWidget() {
  const query = params();
  const base = apiBase(query);
  const tz = query.get('tz') || 'Asia/Kathmandu';
  const payload = {
    date: query.get('date') || todayIso(tz),
    lat: query.get('lat') || '27.7172',
    lon: query.get('lon') || '85.3240',
    tz,
    quality_band: query.get('quality_band') || 'computed',
  };

  try {
    const response = await fetch(base + '/temporal/compass', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const envelope = await response.json();
    if (!response.ok) {
      throw new Error(envelope.detail || 'Request failed');
    }

    const data = envelope.data || envelope;
    const status = document.getElementById('status');
    status.hidden = true;
    document.getElementById('summary').hidden = false;
    document.getElementById('meta').hidden = false;
    document.getElementById('subtitle').textContent = payload.date + ' in ' + payload.tz;

    text('bs-value', formatBs(data.bikram_sambat));
    text('tithi-value', data.primary_readout && data.primary_readout.tithi_name);
    text('nakshatra-value', data.signals && data.signals.nakshatra && data.signals.nakshatra.name);
    text('muhurta-value', data.horizon && data.horizon.current_muhurta && data.horizon.current_muhurta.name);
    text('sunrise-value', formatTime(data.horizon && data.horizon.sunrise, tz));
    text('sunset-value', formatTime(data.horizon && data.horizon.sunset, tz));
    text('method-value', data.method_profile || data.method || '-');
    text('trace-value', data.calculation_trace_id || '-');
  } catch (error) {
    const status = document.getElementById('status');
    status.dataset.state = 'error';
    status.textContent = 'Unable to load widget: ' + (error && error.message ? error.message : String(error));
  }
}

loadWidget();
