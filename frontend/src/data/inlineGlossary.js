import { KUNDALI_GLOSSARY, MUHURTA_GLOSSARY, PANCHANGA_GLOSSARY } from './temporalGlossary';

function normalizeTerm(value) {
  return String(value || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .replace(/[()]/g, '');
}

function flattenSections(source, domain, route) {
  return (source.sections || []).flatMap((section) => (
    (section.terms || []).map((term) => ({
      term: term.name,
      meaning: term.meaning,
      whyItMatters: term.whyItMatters,
      domain,
      route,
      kind: `${domain} term`,
    }))
  ));
}

const EXTRA_TERMS = [
  {
    term: 'Panchanga',
    meaning: 'The five-part daily almanac used to read ritual timing through tithi, nakshatra, yoga, karana, and vaara.',
    whyItMatters: 'It gives the compact daily language behind most of Parva’s calendar and timing surfaces.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Panchanga term',
    aliases: ['almanac'],
  },
  {
    term: 'Paksha',
    meaning: 'The waxing or waning lunar fortnight.',
    whyItMatters: 'It tells you whether the Moon is building toward fullness or receding toward amavasya.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Panchanga term',
  },
  {
    term: 'Shukla Paksha',
    meaning: 'The bright fortnight, when the Moon waxes toward purnima.',
    whyItMatters: 'Many observances care whether a tithi lands in the bright or dark half of the month.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Panchanga term',
    aliases: ['waxing fortnight'],
  },
  {
    term: 'Krishna Paksha',
    meaning: 'The dark fortnight, when the Moon wanes toward amavasya.',
    whyItMatters: 'It changes how the same numbered tithi is interpreted in ritual practice.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Panchanga term',
    aliases: ['waning fortnight'],
  },
  {
    term: 'Pratipada',
    meaning: 'The first lunar day of a paksha.',
    whyItMatters: 'It marks a fresh lunar opening after amavasya or purnima.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
    aliases: ['pratipat'],
  },
  {
    term: 'Dwitiya',
    meaning: 'The second lunar day.',
    whyItMatters: 'It is early in the fortnight, often used to track the settling rhythm after the lunar reset.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
    aliases: ['dvitiya'],
  },
  {
    term: 'Tritiya',
    meaning: 'The third lunar day.',
    whyItMatters: 'It often appears in fasts and vrata sequences tied to the early waxing or waning cycle.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Chaturthi',
    meaning: 'The fourth lunar day.',
    whyItMatters: 'It is strongly associated with Ganesha-related observances and sankata-style fasts.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Panchami',
    meaning: 'The fifth lunar day.',
    whyItMatters: 'It is a mid-early lunar marker and is used by several serpent and seasonal observances.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Shashthi',
    meaning: 'The sixth lunar day.',
    whyItMatters: 'It often carries guardian, fertility, and protection associations in ritual calendars.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
    aliases: ['षष्ठी', 'sasthi'],
  },
  {
    term: 'Saptami',
    meaning: 'The seventh lunar day.',
    whyItMatters: 'It frequently appears in Sun-related observances and health-focused vrata traditions.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Ashtami',
    meaning: 'The eighth lunar day.',
    whyItMatters: 'It often marks intense or deity-specific observances such as Durga and Krishna-related dates.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Navami',
    meaning: 'The ninth lunar day.',
    whyItMatters: 'It is part of many major festival sequences, especially in Shakti and Rama traditions.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Dashami',
    meaning: 'The tenth lunar day.',
    whyItMatters: 'It commonly marks culmination or victory stages inside larger observance cycles.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Ekadashi',
    meaning: 'The eleventh lunar day.',
    whyItMatters: 'It is one of the most widely observed fasting tithis in Vaishnava practice.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Dwadashi',
    meaning: 'The twelfth lunar day.',
    whyItMatters: 'It often carries the break-fast or follow-through stage after Ekadashi observance.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
    aliases: ['dvadashi'],
  },
  {
    term: 'Trayodashi',
    meaning: 'The thirteenth lunar day.',
    whyItMatters: 'It frequently appears in Shiva-related observances and preparation windows before Chaturdashi.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Chaturdashi',
    meaning: 'The fourteenth lunar day.',
    whyItMatters: 'It often sits at a high-intensity lunar edge, close to amavasya or purnima.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Purnima',
    meaning: 'The full-moon tithi.',
    whyItMatters: 'Full-moon observances and month names often key off this point.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Amavasya',
    meaning: 'The new-moon tithi.',
    whyItMatters: 'Ancestor rites, monthly resets, and several major observances pivot on amavasya.',
    domain: 'panchanga',
    route: '/panchanga',
    kind: 'Tithi name',
  },
  {
    term: 'Shubha',
    meaning: 'A favorable or clean-quality slot.',
    whyItMatters: 'It suggests the window is generally more supportive for meaningful activity.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Timing quality',
  },
  {
    term: 'Labh',
    meaning: 'A gain-oriented slot associated with benefit and progress.',
    whyItMatters: 'It is often read as productive for work that should move forward smoothly.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Timing quality',
  },
  {
    term: 'Amrit',
    meaning: 'A nectar-like, highly favorable slot.',
    whyItMatters: 'It usually signals one of the cleaner windows for beginning or blessing an action.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Timing quality',
  },
  {
    term: 'Char',
    meaning: 'A moving or mobile slot.',
    whyItMatters: 'It can work well for travel or flexible tasks, but is not the strongest blessing-style window.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Timing quality',
  },
  {
    term: 'Kal',
    meaning: 'A hard or cautionary slot associated with pressure and loss of ease.',
    whyItMatters: 'It is usually treated as a poor fit for fresh beginnings.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Timing quality',
    aliases: ['kaal'],
  },
  {
    term: 'Rog',
    meaning: 'A disease or friction-oriented slot.',
    whyItMatters: 'It is usually avoided for important new work.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Timing quality',
  },
  {
    term: 'Udveg',
    meaning: 'An agitating or unsettled slot.',
    whyItMatters: 'It often signals stress, hurry, or instability rather than ease.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Timing quality',
  },
  {
    term: 'Rudra',
    meaning: 'A fierce Shiva-associated muhurta name linked with force and disruption.',
    whyItMatters: 'It reads as intense rather than gentle, so Parva treats it with caution.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Ahi',
    meaning: 'A serpent-associated muhurta name linked with coiled or hidden force.',
    whyItMatters: 'It suggests guarded, inward, or less open timing energy.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Mitra',
    meaning: 'A friendship and alliance-oriented muhurta name.',
    whyItMatters: 'It is traditionally read as socially supportive and cooperative.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Pitru',
    meaning: 'An ancestor-oriented muhurta name.',
    whyItMatters: 'It carries lineage and remembrance associations more than worldly momentum.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Vasu',
    meaning: 'A resource and abundance-oriented muhurta name.',
    whyItMatters: 'It is often read as materially supportive and steady.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Vara',
    meaning: 'A boon or blessing-oriented muhurta name.',
    whyItMatters: 'It suggests permission, favor, or a grant of support.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Vishvedeva',
    meaning: 'A muhurta name tied to the collective gods.',
    whyItMatters: 'It suggests shared support rather than one sharply personal force.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Vidhi',
    meaning: 'A rule, ordering, or arrangement-oriented muhurta name.',
    whyItMatters: 'It points toward structure, procedure, and doing things in the proper sequence.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Satamukhi',
    meaning: 'A hundred-faced or multi-sided muhurta name.',
    whyItMatters: 'It suggests complexity and many-facing outcomes rather than one clean line.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Puruhuta',
    meaning: 'An Indra-linked muhurta name associated with public force and command.',
    whyItMatters: 'It often carries visibility and leadership energy.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Vahini',
    meaning: 'A carrying or flowing muhurta name.',
    whyItMatters: 'It suggests movement and conveyance rather than stillness.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Naktankara',
    meaning: 'A night-leaning muhurta name tied to transition into darker hours.',
    whyItMatters: 'It often reads as a threshold window rather than a broad daytime opening.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Varuna',
    meaning: 'A muhurta name tied to cosmic waters, vows, and containment.',
    whyItMatters: 'It suggests depth, seriousness, and boundary-keeping.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Aryaman',
    meaning: 'A muhurta name linked with hospitality, agreements, and noble conduct.',
    whyItMatters: 'It is often read as supportive for socially ordered and well-held actions.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Bhaga',
    meaning: 'A muhurta name linked with good fortune, share, and enjoyment.',
    whyItMatters: 'It is often read as a graceful, benefit-oriented opening.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Girisha',
    meaning: 'A Shiva-linked muhurta name meaning lord of the mountain.',
    whyItMatters: 'It carries austerity, altitude, and seriousness rather than softness.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Ajapada',
    meaning: 'A steady, axial muhurta name traditionally tied to Aja Ekapada.',
    whyItMatters: 'It suggests singular support and fixed grounding.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Ahirbudhnya',
    meaning: 'A deep-foundation serpent muhurta name.',
    whyItMatters: 'It points toward hidden roots, depth, and what sits below the surface.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Pushya',
    meaning: 'A nourishing muhurta name.',
    whyItMatters: 'It is often read as supportive, sustaining, and growth-friendly.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Ashvini',
    meaning: 'A quick, healing, and swift-start muhurta name.',
    whyItMatters: 'It suggests movement, remedy, and a fast opening.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Yama',
    meaning: 'A restraint and endings-oriented muhurta name.',
    whyItMatters: 'It tends to read as severe and less suitable for joyful beginnings.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Agni',
    meaning: 'A fire and ignition-oriented muhurta name.',
    whyItMatters: 'It suggests activation and heat, but can also feel sharp if mishandled.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Vidhatri',
    meaning: 'An ordaining or arranging muhurta name.',
    whyItMatters: 'It points toward structure, allotment, and putting things in their place.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Chanda',
    meaning: 'A fierce or intense muhurta name.',
    whyItMatters: 'It is usually treated as forceful rather than calm or blessing-oriented.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Aditi',
    meaning: 'A spacious, protective, and boundless muhurta name.',
    whyItMatters: 'It suggests openness, shelter, and expansion.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Jiva',
    meaning: 'A life-force oriented muhurta name.',
    whyItMatters: 'It suggests vitality, continuity, and animation.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Vishnu',
    meaning: 'A preserving and sustaining muhurta name.',
    whyItMatters: 'It suggests maintenance, continuity, and long-form steadiness.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Dyumadgadyuti',
    meaning: 'A radiant, shining muhurta name.',
    whyItMatters: 'It points toward brilliance, visibility, and a more outward expression.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Brahma',
    meaning: 'A creation and ordering muhurta name.',
    whyItMatters: 'It suggests building, shaping, and giving structure to what begins.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
  {
    term: 'Samudra',
    meaning: 'An oceanic muhurta name.',
    whyItMatters: 'It suggests breadth, immersion, and a larger field than the immediate task.',
    domain: 'muhurta',
    route: '/best-time',
    kind: 'Muhurta name',
  },
];

const ALL_ENTRIES = [
  ...flattenSections(PANCHANGA_GLOSSARY, 'panchanga', '/panchanga'),
  ...flattenSections(MUHURTA_GLOSSARY, 'muhurta', '/best-time'),
  ...flattenSections(KUNDALI_GLOSSARY, 'kundali', '/birth-reading'),
  ...EXTRA_TERMS,
];

const ENTRY_MAP = new Map();

for (const entry of ALL_ENTRIES) {
  const keys = [entry.term, ...(entry.aliases || [])];
  for (const key of keys) {
    const normalized = normalizeTerm(key);
    if (normalized && !ENTRY_MAP.has(normalized)) {
      ENTRY_MAP.set(normalized, entry);
    }
  }
}

function searchScore(entry, query) {
  const normalizedQuery = normalizeTerm(query);
  if (!normalizedQuery) return -1;

  const haystack = [
    entry.term,
    entry.meaning,
    entry.whyItMatters,
    ...(entry.aliases || []),
    entry.kind,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase();

  if (normalizeTerm(entry.term) === normalizedQuery) return 120;
  if (normalizeTerm(entry.term).startsWith(normalizedQuery)) return 100;
  if (haystack.includes(normalizedQuery)) return 75;

  const tokens = normalizedQuery.split(' ').filter(Boolean);
  if (tokens.length && tokens.every((token) => haystack.includes(token))) {
    return 52;
  }

  return -1;
}

export function getInlineGlossaryEntry(term) {
  return ENTRY_MAP.get(normalizeTerm(term)) || null;
}

export function searchInlineGlossary(query, limit = 6) {
  if (!String(query || '').trim()) return [];

  const matches = ALL_ENTRIES
    .map((entry) => ({ entry, score: searchScore(entry, query) }))
    .filter((item) => item.score >= 0)
    .sort((left, right) => right.score - left.score || left.entry.term.localeCompare(right.entry.term))
    .slice(0, limit)
    .map(({ entry }) => entry);

  const seen = new Set();
  return matches.filter((entry) => {
    const key = normalizeTerm(entry.term);
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}
