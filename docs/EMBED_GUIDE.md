# Embed Guide

Project Parva ships lightweight static embed surfaces under `frontend/public/embed/`.
They are meant for institutions that want a live widget without adopting the full app.

## Available widgets

- `temporal-compass.html`
- `upcoming-festivals.html`
- `parva-embed.js` loader for iframe-based mounting

When the built frontend is served from the same domain as the API, these URLs work directly:

```text
/embed/temporal-compass.html
/embed/upcoming-festivals.html
/embed/parva-embed.js
```

## Option 1: Plain iframe

Temporal Compass:

```html
<iframe
  src="https://your-parva-host.example/embed/temporal-compass.html?date=2026-10-21&lat=27.7172&lon=85.3240&tz=Asia%2FKathmandu"
  title="Project Parva Temporal Compass"
  width="100%"
  height="320"
  loading="lazy"
  style="border:0;"
></iframe>
```

Upcoming Festivals:

```html
<iframe
  src="https://your-parva-host.example/embed/upcoming-festivals.html?days=45&limit=6"
  title="Project Parva Upcoming Festivals"
  width="100%"
  height="420"
  loading="lazy"
  style="border:0;"
></iframe>
```

## Option 2: Loader script

```html
<div
  data-parva-widget="temporal-compass"
  data-date="2026-10-21"
  data-lat="27.7172"
  data-lon="85.3240"
  data-tz="Asia/Kathmandu"
  data-height="320"
></div>

<script async src="https://your-parva-host.example/embed/parva-embed.js"></script>
```

Upcoming festivals example:

```html
<div
  data-parva-widget="upcoming-festivals"
  data-days="45"
  data-limit="6"
  data-height="420"
></div>

<script async src="https://your-parva-host.example/embed/parva-embed.js"></script>
```

## Supported query and data attributes

Temporal Compass:

- `date`
- `lat`
- `lon`
- `tz`
- `quality_band`
- `height`

Upcoming Festivals:

- `days`
- `quality_band`
- `limit`
- `lang`
- `height`

## Deployment notes

- These widgets call the stable `v3` API only.
- They assume the embed page and API are hosted on the same origin.
- Personal/location-sensitive widgets still use POST JSON inside the iframe and do not expose coordinates in the request URL to the API.
- The embed surfaces are public-beta, explainable, and known-limits-first, just like the main app.

## Recommended institutional use

- Municipal or tourism sites: `upcoming-festivals.html`
- Temple, school, or community sites: `temporal-compass.html`
- Internal dashboards: use the API directly and preserve trace/provenance metadata
