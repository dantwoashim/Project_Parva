export const navItems = [
  { label: 'Today', to: '/today' },
  { label: 'My Place', to: '/my-place' },
  { label: 'Festivals', to: '/festivals' },
  { label: 'Best Time', to: '/best-time' },
  { label: 'Birth Reading', shortLabel: 'Birth', to: '/birth-reading' },
  { label: 'Panchanga', shortLabel: 'Dates', to: '/panchanga' },
];

export const footerGroups = [
  {
    title: 'Product',
    links: [
      { label: 'Home', to: '/' },
      { label: 'Today', to: '/today' },
      { label: 'My Place', to: '/my-place' },
      { label: 'Festivals', to: '/festivals' },
      { label: 'Best Time', to: '/best-time' },
      { label: 'Birth Reading', to: '/birth-reading' },
      { label: 'Panchanga', to: '/panchanga' },
    ],
  },
  {
    title: 'Workspace',
    links: [
      { label: 'Developers', to: '/developers' },
      { label: 'Enterprise', to: '/enterprise' },
      { label: 'Saved', to: '/saved' },
      { label: 'Profile', to: '/profile' },
      { label: 'Integrations', to: '/integrations' },
    ],
  },
  {
    title: 'Trust',
    links: [
      { label: 'Trust', to: '/trust' },
      { label: 'Methodology', to: '/methodology' },
      { label: 'Truth Lab', to: '/truth-lab' },
      { label: 'About', to: '/about' },
      { label: 'API Policy', to: '/policy' },
    ],
  },
];

export const sourceDots = [1, 2, 3, 4, 5, 6];

export const festivalMonths = ['All', 'Baishakh', 'Jyestha', 'Ashar', 'Shrawan', 'Bhadra', 'Ashwin', 'Kartik', 'Mangsir', 'Poush', 'Magh', 'Falgun', 'Chaitra'];

export const fallbackFestivalCategories = [
  { value: 'national', label: 'National' },
  { value: 'religious', label: 'Religious' },
  { value: 'buddhist', label: 'Buddhist' },
  { value: 'regional', label: 'Regional' },
  { value: 'fast', label: 'Fast / Vrata' },
];

export const festivalSortOptions = [
  { value: 'chronological', label: 'Calendar order' },
  { value: 'recommended', label: 'Recommended' },
  { value: 'popular', label: 'Major first' },
  { value: 'upcoming', label: 'Upcoming' },
];

export const fallbackFestivalRegions = [
  { value: 'nepal', label: 'Nepal-wide' },
  { value: 'Kathmandu Valley', label: 'Kathmandu Valley' },
  { value: 'Madhesh', label: 'Madhesh / Terai' },
  { value: 'Lumbini', label: 'Lumbini' },
];

export const sampleBirthProfile = {
  name: 'Sample reading',
  date: '1994-04-18',
  time: '06:32',
  place: 'Kathmandu, Nepal',
  lat: '27.7172',
  lon: '85.3240',
  tz: 'Asia/Kathmandu',
};

export const festivalQualityOptions = [
  { value: 'all', label: 'All source states' },
  { value: 'computed', label: 'Computed dates' },
  { value: 'provisional', label: 'Provisional dates' },
  { value: 'inventory', label: 'Inventory only' },
];

export const defaultFestivalFilters = {
  month: 'All',
  category: 'All',
  region: 'All',
  qualityBand: 'all',
  sort: 'chronological',
};

export const festivalVisualMeta = {
  dashain: { tone: 'orange', art: 'durga', icon: '✣' },
  tihar: { tone: 'gold', art: 'diya', icon: '◒' },
  'buddha-jayanti': { tone: 'green', art: 'buddha', icon: '◇' },
  chhath: { tone: 'orange', art: 'sun', icon: '✺' },
  holi: { tone: 'red', art: 'holi', icon: '☆' },
  'ekadashi-apara': { tone: 'green', art: 'leaf', icon: '✤' },
};

export const categoryVisualMeta = {
  national: { tone: 'orange', art: 'durga', icon: '✣' },
  buddhist: { tone: 'green', art: 'buddha', icon: '◇' },
  religious: { tone: 'gold', art: 'diya', icon: '◒' },
  fast: { tone: 'green', art: 'leaf', icon: '✤' },
  regional: { tone: 'red', art: 'holi', icon: '✦' },
};


export const grahaShort = {
  sun: 'Su',
  moon: 'Mo',
  mars: 'Ma',
  mercury: 'Me',
  jupiter: 'Ju',
  venus: 'Ve',
  saturn: 'Sa',
  rahu: 'Ra',
  ketu: 'Ke',
};

export const signShort = {
  Aries: 'Ari',
  Taurus: 'Tau',
  Gemini: 'Gem',
  Cancer: 'Can',
  Leo: 'Leo',
  Virgo: 'Vir',
  Libra: 'Lib',
  Scorpio: 'Sco',
  Sagittarius: 'Sag',
  Capricorn: 'Cap',
  Aquarius: 'Aqu',
  Pisces: 'Pis',
};

export const housePositions = {
  1: { x: 50, y: 22 },
  2: { x: 66, y: 30 },
  3: { x: 77, y: 42 },
  4: { x: 66, y: 52 },
  5: { x: 77, y: 64 },
  6: { x: 66, y: 75 },
  7: { x: 50, y: 78 },
  8: { x: 34, y: 75 },
  9: { x: 23, y: 64 },
  10: { x: 34, y: 52 },
  11: { x: 23, y: 42 },
  12: { x: 34, y: 30 },
};

export const readingTraits = {
  Aries: 'direct, decisive, and action-led',
  Taurus: 'steady, tactile, and materially grounded',
  Gemini: 'curious, verbal, and adaptive',
  Cancer: 'protective, memory-rich, and emotionally tuned',
  Leo: 'visible, expressive, and self-directed',
  Virgo: 'precise, service-minded, and pattern-sensitive',
  Libra: 'relational, aesthetic, and balance-seeking',
  Scorpio: 'private, intense, and transformation-oriented',
  Sagittarius: 'searching, principled, and horizon-facing',
  Capricorn: 'structured, patient, and responsibility-led',
  Aquarius: 'independent, systems-minded, and future-facing',
  Pisces: 'intuitive, porous, and symbol-sensitive',
};

export const pricingPlans = [
  {
    slug: 'free',
    name: 'Free',
    price: 'NPR 0',
    limit: '100 requests/day/IP',
    support: 'No support',
    body: 'For testing public calendar endpoints before a product depends on Parva.',
  },
  {
    slug: 'starter',
    name: 'Starter',
    price: 'NPR 500/mo',
    limit: '5,000 requests/month',
    support: 'Email support',
    body: 'For small apps, temple sites, internal dashboards, and early integrations.',
  },
  {
    slug: 'professional',
    name: 'Professional',
    price: 'NPR 2,000/mo',
    limit: '50,000 requests/month',
    support: 'Priority support',
    body: 'For production products that need dependable volume and webhook notifications.',
  },
  {
    slug: 'enterprise',
    name: 'Enterprise',
    price: 'Custom',
    limit: 'Custom volume',
    support: 'SLA',
    body: 'For private deployments, contractual support, and custom calendar surfaces.',
  },
];

export const manualPaymentMethods = {
  manual_bank_qr: {
    label: 'Bank QR',
    shortLabel: 'Bank',
    image: '/payment-qr/bank-qr.png',
    note: 'Best for direct bank transfer. Use the invoice number as remarks if your banking app allows it.',
  },
  manual_esewa_qr: {
    label: 'eSewa QR',
    shortLabel: 'eSewa',
    image: '/payment-qr/esewa-qr.jpg',
    note: 'Use this only as a personal/manual QR payment, not automated eSewa checkout.',
  },
  manual_khalti_qr: {
    label: 'Khalti QR',
    shortLabel: 'Khalti',
    image: '/payment-qr/khalti-qr.png',
    note: 'Use this only as a personal/manual QR payment, not automated Khalti checkout.',
  },
};
