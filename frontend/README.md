# Project Parva — Frontend

> Nepal Festival Discovery Application

A premium web experience for exploring Nepal's rich festival traditions, featuring an accurate ritual time engine, interactive maps, and deep cultural content.

## Features

- **Festival Discovery**: Browse 50+ festivals with mythology, rituals, and sacred locations
- **Ritual Time Engine**: Accurate date calculations across Bikram Sambat, Nepal Sambat, and Gregorian calendars
- **Interactive Maps**: Explore temple locations with festival connections
- **Lunar Calendar**: Real-time tithi and moon phase display
- **Responsive Design**: Premium experience on desktop and mobile

## Tech Stack

- **React 18** with Vite
- **Leaflet** for mapping
- **CSS Custom Properties** for theming
- **Fetch API** for backend communication

## Development Setup

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The app runs at `http://localhost:5173` and expects the backend at `http://localhost:8000`.

## Environment Variables

Create a `.env` file for production deployment:

```env
# API endpoint (defaults to localhost:8000/api)
VITE_API_BASE=https://your-api-domain.com/api
```

## Project Structure

```
src/
├── components/
│   ├── Calendar/       # Temporal navigator, lunar phase
│   ├── Festival/       # Cards, detail view, mythology, rituals
│   └── Map/            # Festival map with temple markers
├── hooks/              # useFestivals, useCalendar, etc.
├── pages/              # ParvaPage main view
├── services/           # API client
└── index.css           # Design system tokens
```

## Building for Production

```bash
npm run build
```

Output is in `dist/` directory, ready for static hosting.

## Related

- [Backend API](../backend/README.md) — FastAPI backend with calendar engine
- [PROJECT_BIBLE.md](../PROJECT_BIBLE.md) — Complete project specification

---

**Part of Project Parva** — BSc CSIT Final Year Project  
*Exploring Nepal through its sacred calendar*
