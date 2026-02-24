export const PANCHANGA_GLOSSARY = {
  title: "What Today's Panchanga Means",
  intro:
    'Panchanga is a daily ritual-time map built from the Sun, Moon, and weekday cycle. These values help decide observance timing.',
  sections: [
    {
      id: 'five-limbs',
      title: 'The 5 Limbs of Panchanga',
      description: 'Each day is described using five markers:',
      terms: [
        {
          name: 'Tithi',
          meaning: 'The lunar day based on Moon-Sun angle (1 to 30).',
          whyItMatters: 'Most festivals and fasts are tied to a specific tithi at sunrise.',
        },
        {
          name: 'Nakshatra',
          meaning: 'The Moon\'s star sector among 27 nakshatras.',
          whyItMatters: 'Used in puja planning, naming traditions, and muhurta filtering.',
        },
        {
          name: 'Yoga',
          meaning: 'A combined Sun-Moon angle classification among 27 yogas.',
          whyItMatters: 'Traditionally used to classify general day quality.',
        },
        {
          name: 'Karana',
          meaning: 'Half of a tithi; a finer time unit for action windows.',
          whyItMatters: 'Useful when selecting specific periods within a day.',
        },
        {
          name: 'Vaara',
          meaning: 'Weekday (Ravivara, Somavara, etc.).',
          whyItMatters: 'Many rituals have weekday preferences or restrictions.',
        },
      ],
    },
    {
      id: 'related',
      title: 'Related Terms You See in Parva',
      description: 'These appear in details and API metadata:',
      terms: [
        {
          name: 'Paksha',
          meaning: 'Waxing (Shukla) or waning (Krishna) lunar fortnight.',
          whyItMatters: 'Helps identify whether the Moon is growing or shrinking.',
        },
        {
          name: 'Udaya Tithi',
          meaning: 'The tithi active at local sunrise.',
          whyItMatters: 'Parva uses this for religiously correct day assignment.',
        },
        {
          name: 'Bikram Sambat (BS)',
          meaning: 'Nepal\'s civil calendar date shown alongside Gregorian date.',
          whyItMatters: 'Official observances in Nepal are often communicated in BS.',
        },
        {
          name: 'Confidence + Trace',
          meaning: 'Metadata about method certainty and reproducible calculation path.',
          whyItMatters: 'Lets users verify how and why a date was computed.',
        },
      ],
    },
  ],
};

export const PERSONAL_PANCHANGA_GLOSSARY = {
  title: 'How Personal Panchanga Is Different',
  intro:
    'Personal Panchanga recalculates the day using your location and timezone, so sunrise-based results match your city, not only Kathmandu.',
  sections: [
    {
      id: 'personal-inputs',
      title: 'Inputs That Change the Result',
      terms: [
        {
          name: 'Latitude / Longitude',
          meaning: 'Your physical location for sunrise and local sky calculations.',
          whyItMatters: 'A tithi boundary can shift when sunrise changes by location.',
        },
        {
          name: 'Timezone',
          meaning: 'Local civil time context for date boundaries and display.',
          whyItMatters: 'Diaspora users get date labels aligned with their local day.',
        },
        {
          name: 'Method Profile',
          meaning: 'Named ruleset used to compute this personal output.',
          whyItMatters: 'Makes results auditable and consistent across clients.',
        },
      ],
    },
  ],
};

export const MUHURTA_GLOSSARY = {
  title: 'How Muhurta Windows Are Computed',
  intro:
    'Muhurta is about selecting favorable time windows. Parva combines day segmentation with rule filters so users can compare options clearly.',
  sections: [
    {
      id: 'core',
      title: 'Core Muhurta Terms',
      terms: [
        {
          name: 'Muhurta',
          meaning: 'A time window segment used for ritual planning.',
          whyItMatters: 'Different windows have different suitability scores.',
        },
        {
          name: 'Abhijit Muhurta',
          meaning: 'A traditionally favorable midday window.',
          whyItMatters: 'Often used when no other strong window is available.',
        },
        {
          name: 'Rahu Kalam',
          meaning: 'A daily inauspicious segment by weekday pattern.',
          whyItMatters: 'Commonly avoided for new beginnings.',
        },
        {
          name: 'Hora',
          meaning: 'Planetary hour sequence through day and night.',
          whyItMatters: 'Used to prioritize windows by activity type.',
        },
        {
          name: 'Chaughadia',
          meaning: 'Eight daytime and nighttime quality slots.',
          whyItMatters: 'Adds quick favorable/unfavorable classification.',
        },
        {
          name: 'Tara Bala',
          meaning: 'Compatibility signal between birth nakshatra and day nakshatra.',
          whyItMatters: 'Personalizes ranking when birth nakshatra is provided.',
        },
      ],
    },
    {
      id: 'quality',
      title: 'Why You See Scores and Assumptions',
      terms: [
        {
          name: 'Score',
          meaning: 'Relative ranking based on configured rule weights.',
          whyItMatters: 'Helps you compare options, not treat one result as absolute destiny.',
        },
        {
          name: 'Assumption Set',
          meaning: 'Profile controlling how rules are weighted (e.g., mainstream vs diaspora practical).',
          whyItMatters: 'Different communities can choose different interpretation defaults.',
        },
      ],
    },
  ],
};

export const KUNDALI_GLOSSARY = {
  title: 'How to Read Your Kundali Output',
  intro:
    'Kundali summarizes planetary placements at a birth time and location. Parva focuses on transparent computational outputs with clear assumptions.',
  sections: [
    {
      id: 'building-blocks',
      title: 'Main Building Blocks',
      terms: [
        {
          name: 'Lagna (Ascendant)',
          meaning: 'The zodiac sign rising in the east at birth time.',
          whyItMatters: 'Sets house sequence and core chart orientation.',
        },
        {
          name: 'Rashi',
          meaning: 'Zodiac sign occupied by a graha (planetary point).',
          whyItMatters: 'Used to interpret temperament and event patterns.',
        },
        {
          name: 'Graha',
          meaning: 'Nine key Vedic planetary points: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu.',
          whyItMatters: 'Their sign and house positions drive chart interpretation.',
        },
        {
          name: '12 Houses',
          meaning: 'Life domains (self, wealth, family, career, etc.).',
          whyItMatters: 'Shows where planetary influence is expressed.',
        },
        {
          name: 'D1 / D9',
          meaning: 'Rashi chart (D1) and Navamsha chart (D9).',
          whyItMatters: 'D9 is often used as a refinement layer for strengths and relationships.',
        },
      ],
    },
    {
      id: 'signals',
      title: 'Interpretation Signals',
      terms: [
        {
          name: 'Aspects',
          meaning: 'Angular relationships between grahas.',
          whyItMatters: 'Adds interaction context between planetary influences.',
        },
        {
          name: 'Yoga',
          meaning: 'Named planetary combinations with traditional significance.',
          whyItMatters: 'Highlights notable chart patterns quickly.',
        },
        {
          name: 'Dosha',
          meaning: 'Specific condition markers that may need caution in interpretation.',
          whyItMatters: 'Flags areas often discussed in life-event consultation.',
        },
        {
          name: 'Vimshottari Dasha',
          meaning: 'Planetary period timeline (Maha and Antar phases).',
          whyItMatters: 'Used to understand timing emphasis over years.',
        },
      ],
    },
  ],
};
