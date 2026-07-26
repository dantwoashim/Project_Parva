function params() {
  return new URLSearchParams(window.location.search);
}

function apiBase(query) {
  const configured = document.body.dataset.apiBase || query.get('api_base');
  return (configured || 'https://api.prabinghimire1.com.np/v3/api').replace(/\/+$/, '');
}

function festivalRange(item) {
  if (!item) return '-';
  if (!item.end_date || item.end_date === item.start_date) {
    return item.start_date || '-';
  }
  return item.start_date + ' -> ' + item.end_date;
}

function createFestivalRow(item) {
  const li = document.createElement('li');
  const left = document.createElement('span');
  const right = document.createElement('strong');
  left.textContent = item.display_name || item.name || item.id || 'Festival';
  right.textContent = festivalRange(item);
  li.append(left, right);
  return li;
}

async function loadWidget() {
  const query = params();
  const base = apiBase(query);
  const days = query.get('days') || '30';
  const limit = Number(query.get('limit') || '5');
  const qualityBand = query.get('quality_band') || 'computed';
  const lang = query.get('lang') || 'en';

  try {
    const response = await fetch(
      base
        + '/festivals/upcoming?days='
        + encodeURIComponent(days)
        + '&quality_band='
        + encodeURIComponent(qualityBand)
        + '&lang='
        + encodeURIComponent(lang),
    );
    const envelope = await response.json();
    if (!response.ok) {
      throw new Error(envelope.detail || 'Request failed');
    }

    const data = envelope.data || envelope;
    const items = (data.festivals || []).slice(0, Math.max(limit, 1));
    const status = document.getElementById('status');
    const list = document.getElementById('festival-list');

    status.hidden = true;
    list.hidden = false;
    document.getElementById('subtitle').textContent = 'Next ' + days + ' days';

    if (!items.length) {
      const empty = document.createElement('li');
      const label = document.createElement('span');
      label.textContent = 'No festivals in this window.';
      const count = document.createElement('strong');
      count.textContent = '-';
      empty.append(label, count);
      list.appendChild(empty);
      return;
    }

    items.forEach((item) => {
      list.appendChild(createFestivalRow(item));
    });
  } catch (error) {
    const status = document.getElementById('status');
    status.dataset.state = 'error';
    status.textContent = 'Unable to load widget: ' + (error && error.message ? error.message : String(error));
  }
}

loadWidget();
