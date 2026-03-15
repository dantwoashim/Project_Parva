# Project Parva UI/UX Trust Research and Redesign Strategy

Date: 2026-03-14

## Executive Summary

Project Parva does not currently feel like a trustworthy consumer product. It feels like an internal dashboard, technical demo, and devotional data tool sharing the same surface.

The current frontend has real strengths:

- It already contains meaningful data and strong backend capabilities.
- It has the beginnings of an atmospheric visual identity.
- It includes explainability and provenance concepts that many competitors hide.

But the current product experience is weak in the exact places that determine trust:

- no true landing page or guided first-run path
- generic top navigation with too many equal-priority choices
- expert controls exposed to normal users
- raw numbers shown before meaning
- raw feed/API links shown in consumer-facing flows
- SVG/data visuals that decorate complexity instead of explaining it
- premium styling attempts that feel ornamental rather than authoritative
- visible polish breaks, including a homepage `Invalid Date` above the fold

The opportunity is still excellent. The strongest market position is not "be a prettier Hamro Patro" and not "be a denser Drik Panchang." The strongest position is:

`the calm, premium, explainable Nepal temporal interface`

That means:

- outcome first
- meaning before mechanics
- ceremony before computation
- proof available, not forced
- cultural trust without visual clutter

If Parva follows that direction, it can occupy a real whitespace:

- more elegant than Hamro Patro
- more accessible than Drik Panchang
- more culturally specific than timeanddate
- more explainable than astrology apps
- more emotionally grounded than raw panchanga tools

## What This Review Covered

I audited:

- core React app structure
- navigation and layout shell
- Temporal Compass, Personal Panchanga, Muhurta, Kundali, Festival Explorer, and Feeds flows
- developer and access portal surfaces
- current browser-rendered pages and mobile behavior
- trust/credibility UX research
- competitor positioning and experience patterns

Primary local evidence came from:

- `frontend/src/App.jsx`
- `frontend/src/App.css`
- `frontend/src/pages/TemporalCompassPage.jsx`
- `frontend/src/pages/PersonalPanchangaPage.jsx`
- `frontend/src/pages/MuhurtaPage.jsx`
- `frontend/src/pages/KundaliPage.jsx`
- `frontend/src/pages/FestivalExplorerPage.jsx`
- `frontend/src/pages/FeedSubscriptionsPage.jsx`
- `frontend/src/components/KundaliGraph/KundaliGraph.jsx`
- `frontend/src/components/MuhurtaHeatmap/MuhurtaHeatmap.jsx`
- `frontend/src/components/Mode/ModeSwitch.jsx`
- `frontend/src/components/UI/AuthorityInspector.jsx`
- `frontend/public/developers/index.html`
- `frontend/public/access/index.html`
- `frontend/public/portals.css`

Rendered visual evidence was captured in:

- `output/playwright/ux-audit/home.png`
- `output/playwright/ux-audit/home-mobile.png`
- `output/playwright/ux-audit/personal.png`
- `output/playwright/ux-audit/muhurta.png`
- `output/playwright/ux-audit/kundali.png`
- `output/playwright/ux-audit/festivals.png`
- `output/playwright/ux-audit/festival-detail.png`
- `output/playwright/ux-audit/feeds.png`
- `output/playwright/ux-audit/developers-portal.png`
- `output/playwright/ux-audit/access-portal.png`

## Brutally Honest Product Review

### What it feels like today

The app currently feels like:

- a developer console with decorative gold gradients
- a dashboard where every tool was given identical importance
- an expert system that expects the user to already understand panchanga concepts
- a premium-looking shell wrapped around a low-priority information hierarchy

It does **not** currently feel like:

- a calm authority
- a ceremonial companion
- a polished premium product
- an experience that helps a new user understand what to do next

### Current trust scorecard

These are subjective but intentionally strict:

| Category | Score / 10 | Honest note |
| --- | --- | --- |
| Visual distinctiveness | 5 | There is a theme, but it still reads as generic dark dashboard UI. |
| First impression trust | 3 | The first screen asks the user to interpret terms and numbers too quickly. |
| Information hierarchy | 3 | Almost everything is visually treated as equally important. |
| Beginner usability | 2 | Too many unexplained concepts appear before value is delivered. |
| Emotional reassurance | 3 | There is little "you are in the right place" guidance. |
| Premium feel | 4 | Glow, dark cards, and serif headlines are not enough to feel premium. |
| Cultural grounding | 6 | The subject matter is culturally grounded; the UX expression is not yet. |
| Product strategy coherence | 4 | Consumer, expert, API, and operations surfaces are mixed together. |
| Mobile clarity | 3 | Navigation and above-the-fold density are poor on mobile. |
| Launch-readiness for normal users | 3 | Strong engine, weak product wrapper. |

## The Biggest Problems

### 1. There is no real homepage

The root route is `TemporalCompassPage`, not a landing experience.

That means the product opens with:

- technical navigation
- mode switches
- language and quality controls
- a date picker
- a ring visualization
- domain words like Tithi, Yoga, Karana, Vaara

This is the wrong order for trust.

A new user should first understand:

- what this product does
- why it is better than alternatives
- what they can do here in plain language
- how to start

### 2. The global chrome is too technical

The header currently exposes:

- 8 primary nav links
- observance/authority toggle
- language control
- quality band control

This creates expert-mode cognitive load before the user has even decided what they want.

For a consumer product, `Authority`, `Computed`, `Inventory`, and `Quality` should not sit in the default top chrome. Those are advanced context controls.

### 3. The product shows abstractions before answers

The user asked for "no abstractions" and they are right.

Current surfaces often lead with:

- taxonomic labels
- raw score values
- low-context glossary blocks
- unexplained categorical distinctions
- long tables of planetary or calendar values

Instead, the first question should always be:

- What matters today?
- What should I do?
- What should I avoid?
- Why is this the result?

Abstractions should come later.

### 4. The visuals are not doing interpretive work

The current visuals are mostly representational, not explanatory.

Examples:

- The orbital ring shows a percentage and a number, but does not tell the user what that means for their day.
- The muhurta heatmap shows many blocks and scores, but does not convert them into a small set of actionable windows.
- The kundali graph shows nodes, houses, and lines, but delivers little immediate human value unless the user already understands chart structure.

The design should translate. Right now it mostly displays.

### 5. The consumer surface leaks internal product structure

Examples:

- The feed page exposes raw `.ics` endpoints as visible consumer content.
- The main footer shows licensing/source every time, even on core ritual/consumer pages.
- The app contains developer-grade access and evidence concepts that belong behind secondary navigation.
- The visual shell of the main app is weaker than the portal pages, which means the product's best positioning is hidden off to the side.

### 6. The trust breaks are visible, not subtle

The homepage currently renders `Invalid Date` for sunrise in the main trust band. This is not a cosmetic issue. It directly damages perceived reliability.

Trust is destroyed by:

- visible invalid values
- unlabeled percentages
- empty states without explanation
- raw JSON traces in end-user pages
- unprioritized metrics
- obvious unfinishedness

### 7. The premium attempt is too ornamental

The product tries to signal quality with:

- dark surfaces
- gold accents
- glass cards
- particles
- gradients

But premium trust does not come from ornament. It comes from:

- restraint
- confidence
- hierarchy
- precision
- silence
- clarity

Right now the product is trying to look special instead of feeling inevitable.

## Browser Audit Findings

### Home / Temporal Compass

Observed in `output/playwright/ux-audit/home.png` and `home-mobile.png`.

Issues:

- Above the fold contains too many controls and too little plain-language value.
- `Invalid Date` appears in the sunrise slot.
- The ring dominates attention but does not explain practical meaning.
- "10" and "80%" are visually prominent but semantically weak.
- There is no onboarding context for first-time users.
- Mobile header height is excessive and pushes the answer down.

What the user should feel:

- "I instantly understand today's situation."
- "I trust this result."
- "I know what to open next."

What they currently feel:

- "I need to decode this."

### Personal Panchanga

Observed in `output/playwright/ux-audit/personal.png`.

Issues:

- Latitude/longitude/timezone are exposed as primary controls.
- The page leads with system parameters rather than user outcome.
- "Local sunrise delta vs Kathmandu baseline" is technically interesting but not user-first.
- Cards still emphasize numbered classification more than interpretation.

What should happen instead:

- ask for place and date in friendly language
- show personal day summary first
- place calculation deltas in secondary detail

### Muhurta

Observed in `output/playwright/ux-audit/muhurta.png`.

Issues:

- "Assumption Set" is expert language and should not be visible by default.
- Scores like `63`, `-153`, `-66` are shown without a strong interpretive layer.
- The heatmap is dense and numerically loud.
- The page should answer "best 2 windows" and "avoid this time" immediately.

What should happen instead:

- best window
- second-best window
- avoid period
- short reason in plain language
- advanced ranking detail behind a disclosure

### Kundali

Observed in `output/playwright/ux-audit/kundali.png`.

Issues:

- The graph is center stage, but it is not the most meaningful first artifact for most users.
- The page presents a chart before a thesis.
- The "Interpretation Sidebar" is too weak relative to the graph and table.
- The graph is more inspectable than insightful.
- The Graha table is high-density, high-jargon, low-conversion content.

The biggest product problem here:

The kundali page answers the expert's question, not the normal user's question.

The normal user's questions are more like:

- What kind of chart is this overall?
- What are my strongest energies?
- What should I pay attention to?
- What three things define this reading?

### Festival Explorer

Observed in `output/playwright/ux-audit/festivals.png`.

Issues:

- The title "Festival Explorer Ribbon" is product-internal language.
- The interface is dense but emotionally flat.
- The timeline is useful, but there is no curation layer.
- Dates dominate visually more than meaning or cultural significance.

The better direction:

- curated "coming soon" cards first
- full timeline second
- lighter filters by default
- stronger story framing

### Feeds

Observed in `output/playwright/ux-audit/feeds.png`.

Issues:

- Raw URLs are shown directly in the main content area.
- This feels operational, not premium.
- Consumers do not need to see endpoint strings to trust a calendar subscription feature.

Better:

- app badges or platform-friendly actions
- "Subscribe to all festivals"
- "Subscribe to national holidays"
- "Build a custom calendar"
- raw link available only after action or in an advanced drawer

### Developer and Access Portals

Observed in `output/playwright/ux-audit/developers-portal.png` and `access-portal.png`.

This is a very important finding:

The portal pages are already better at hierarchy, copy clarity, calm spacing, and premium tone than the main app.

That means the design problem is not a complete lack of taste in the repo. The problem is fragmentation:

- better positioning lives outside the main experience
- better spacing lives outside the main experience
- better consumer-level framing does not drive the main app

These portal patterns should influence the eventual landing and app-shell redesign.

## Why Users Do Not Trust It Yet

The trust problem is not mostly about color, typography, or "making it pretty."

It is about the psychology of credibility.

Research-backed credibility and UX themes relevant to Parva:

- Stanford's web credibility guidance emphasizes verification, visible organization, visible expertise, contactability, professionalism, usefulness, recency, restraint with promotion, and error avoidance.
- Nielsen Norman Group's heuristics emphasize visibility of system status, match between system and the real world, recognition rather than recall, and aesthetic/minimalist design.

Translated into Parva language:

- Show the result first.
- Speak like a person, not a schema.
- Make important uncertainty understandable.
- Let users verify when they want to.
- Never show visible broken states.
- Remove all controls that are not needed for the current task.

### The specific psychological trust chain Parva needs

For this product, trust forms in this order:

1. I understand what this is.
2. It looks serious and calm.
3. It speaks my language.
4. It gives me an answer quickly.
5. The answer feels internally coherent.
6. It shows why I should trust it.
7. It gives me a path to learn more without forcing me to.

Parva currently jumps too fast to step 6 and 7 before fully earning step 1 through 5.

## Competitor Landscape

## 1. Hamro Patro

Official positioning and site copy show Hamro Patro as a broad Nepali lifestyle utility with:

- calendar/patro
- panchanga
- forex
- gold/silver
- horoscopes
- notes
- radio
- news
- widgets
- multiple apps

Its strength:

- habit
- breadth
- diaspora familiarity
- utility bundling

Its weakness:

- sprawl
- clutter
- mixed intent surfaces
- weaker premium signal

The opening for Parva:

Do not out-bloat Hamro Patro. Win by being cleaner, more ceremonial, more premium, and more explainable.

## 2. Drik Panchang

Drik Panchang is extremely strong on:

- breadth of calculation coverage
- explicit methodological stance
- huge geographic support
- festival and panchang depth

Its homepage and copy signal that it supports more than 100,000 cities and makes an explicit calculation choice in favor of precise planetary positions.

Its strength:

- authority
- coverage
- seriousness

Its weakness:

- expert density
- cognitive intimidation
- visual overload for beginners

The opening for Parva:

Be the modern, gentle, outcome-first layer over authority-grade computation.

## 3. timeanddate

timeanddate succeeds because it is:

- broad but calm
- data-rich but structured
- trustworthy without theatrics
- explicit about tools, services, and recency

The site demonstrates strong utility trust through:

- clean categorization
- strong information hierarchy
- highly predictable navigation
- obvious current-state feedback
- professional restraint

The opening for Parva:

Borrow the calm utility confidence, but apply it to Nepal-specific temporal and ritual experiences.

## 4. CHANI

CHANI is valuable as a style and product-positioning reference, not because the subject matter is identical.

CHANI wins on:

- emotional framing
- editorial warmth
- accessibility of language
- strong personality without chaos

Its core lesson:

People stay when they feel guided, not examined.

Parva needs more of this in:

- onboarding
- summary language
- personal surfaces
- kundali interpretation

## 5. The Pattern

The Pattern is important because it leads with:

- feeling seen
- deeper connection
- personalized insights

It turns astrology into a relational, identity-centered product rather than a chart mechanics product.

Parva should not copy its tone, but it should learn from its prioritization:

- identity/value summary first
- system structure second

## 6. AstroSage and similar monetized astrology apps

These products prove there is real appetite for astrology and chart products, but they also show the downside of:

- monetization pressure everywhere
- feature clutter
- pop-spiritual visual noise

Parva should learn the demand, not the tone.

## Market Reality

The market is real, but the winning strategy is not "be everything."

Signals:

- Hamro Patro is still positioned as a mass-market Nepali companion with millions of screens and many adjacent utilities.
- Drik Panchang remains a serious reference destination with deep calculation coverage and explicit methodology.
- timeanddate remains a global standard for trustable temporal tooling because it organizes dense data cleanly.
- CHANI and The Pattern show continued demand for guided, emotionally resonant astrology products.
- Pew's 2025 spirituality research indicates large adjacent demand for practices like consulting astrologers, tarot cards, or fortune tellers, especially among younger groups and in India.

What this means for Parva:

The audience exists.

The problem is not demand.

The problem is packaging.

## The White Space Parva Can Own

The best market position is:

`luxury calm + Nepal specificity + explainable trust + free core utility`

That is a stronger wedge than:

- broad super-app utility
- dense expert-only almanac
- gimmicky astrology aesthetic
- generic calendar dashboard

The product promise should be:

"A beautiful, trustworthy way to understand Nepal's festivals, panchanga, muhurta, and birth-chart signals - with plain-language guidance first, deep evidence second."

## Product Strategy Recommendation

Parva should separate its experience into three layers:

### Layer 1: Consumer surface

For everyday people.

Primary jobs:

- What matters today?
- What festivals are coming?
- What is a good time for this activity?
- What does my chart say in plain language?

### Layer 2: Explainability surface

For curious users and advanced users.

Primary jobs:

- Why is this the answer?
- Which profile or assumption set was used?
- What are the known limits?
- How certain is this?

### Layer 3: Operator / developer surface

For institutions, integrators, and reviewers.

Primary jobs:

- API docs
- evidence artifacts
- reliability and provenance
- access paths

These layers should not share the same default chrome.

## UX Principles for This Exact Product

### 1. Meaning before mechanics

Never show:

- scores
- coordinates
- trace IDs
- quality bands
- method profiles
- house graphs

before showing:

- the answer
- what it means
- what to do next

### 2. One primary question per screen

Each main product route should answer one dominant question.

- Home: What matters today?
- Festivals: What is happening and why does it matter?
- Personal: How is today different for me?
- Muhurta: When is the best time?
- Kundali: What is the shape of my chart?

### 3. Progressive disclosure, not simultaneous exposure

Default:

- simple answer
- one-line reason
- one confidence phrase

Advanced:

- details
- glossary
- metadata
- trace
- raw tables

### 4. Cultural luxury, not dashboard luxury

Avoid:

- gamer darkness
- crypto UI energy
- glowing dashboard cards
- ornamental particles as the main premium signal

Use instead:

- warm paper or lacquered-dark surfaces
- disciplined spacing
- strong typography
- a slower visual tempo
- restrained accenting
- heritage-informed textures and symbols

### 5. Calm authority

Authority should feel:

- deliberate
- reviewed
- current
- humble about limits

Not:

- loud
- over-claiming
- numerically aggressive

## Visual Direction Recommendation

The product needs a more distinct visual system.

### Recommended visual direction

Think:

- Himalayan museum catalog
- ceremonial almanac
- premium print object
- temple archive meets modern product design

Not:

- startup dashboard
- "premium SaaS dark mode"
- sci-fi astronomy app

### Design ingredients

- Use a lighter public-facing landing shell and reserve deeper tones for focused result views.
- Keep one primary metallic accent, not many competing glows.
- Use stronger contrast between primary answer, secondary context, and advanced detail.
- Replace many rounded generic cards with fewer, more deliberate panels.
- Use custom iconography tied to ritual, lunar, seasonal, or calendrical ideas.

### Typography direction

The current serif idea is directionally right, but the system needs more discipline.

Suggested free-font approach:

- Display: Cormorant Garamond or EB Garamond
- UI sans: Instrument Sans, Source Sans 3, or Public Sans
- Devanagari support: Noto Sans Devanagari

Rules:

- large, elegant display only where meaning warrants it
- clean sans for controls and body
- no tiny uppercase labels everywhere
- reduce decorative micro-label noise

## Navigation and Information Architecture Redesign

### Current problem

Current nav:

- Compass
- Explorer
- Panchanga
- Personal
- Muhurta
- Kundali
- Calendar
- Feeds

This is too many top-level choices for a new user.

### Proposed public nav

- Home
- Today
- Festivals
- Good Time
- Personal Day
- Birth Chart
- About

Move out of primary nav:

- Feeds
- Calendar utilities
- developer surfaces
- access/commercial surfaces

Put these in:

- footer
- about page
- dedicated developer link

### Landing page structure

#### Hero

- one sentence on what Parva does
- one sentence on why to trust it
- two CTAs: "See today" and "Set up my personal day"

#### Trust rail

- Explainable
- Nepal-focused
- Public beta with known limits

#### Intent cards

- Understand today
- Find a good time
- Explore festivals
- Read my birth chart

#### Social proof / credibility

- methodology
- what is reviewed
- what varies by region
- what "public beta" means

#### Quiet developer link

- for institutions and integrators

## Route-by-Route Redesign Direction

## Home / Today

Replace the current compass-first experience with:

- Today's headline
- Today's tithi in plain language
- festival status
- best and avoid windows
- one "why" drawer

The ring should either be:

- removed from above the fold, or
- transformed into an annotated, interpretive visualization

## Personal Day

Top section should read like:

- Your day in Kathmandu
- Today favors...
- Today may be less ideal for...
- Sunrise / sunset for your place

Then:

- glossary
- deeper technical context

Place input should feel like place input, not lat/lon engineering input.

## Muhurta

The page should open with an answer stack:

- Best time
- Second-best time
- Avoid window
- Basis of recommendation

Then the heatmap can support, not dominate.

Change raw scores into:

- Strong
- Good
- Mixed
- Avoid

If keeping numbers, hide them behind "show ranking details."

## Kundali

This route needs the largest conceptual redesign.

Recommended structure:

1. Identity summary
2. Three strongest chart themes
3. Key life-area highlights
4. Relationship between Lagna, Moon, and major patterns
5. Optional chart visualization
6. Optional graha table

In other words:

- thesis first
- graph second
- appendix last

The current graph should not be the hero.

### Better kundali value model

Give the user:

- "Your chart leans watery and mutable"
- "Relationships and intuition are strong themes"
- "Current tensions show up in X, not everything"
- "This is a symbolic reading, not destiny"

That gives value immediately.

## Festival Explorer

Turn this from a ribbon-first tool into:

- featured upcoming festivals
- curated editorial summaries
- cultural significance first
- timeline and filters second

The user should be able to browse by:

- upcoming
- month
- festival type
- region
- family/ritual relevance

## Feeds

Move the current feed builder out of top-nav prominence.

Redesign as:

- "Subscribe to calendar"
- platform choice
- optional custom builder
- copy/share action

Do not show the raw feed URL until requested.

## Trust Architecture Parva Should Adopt

### Show these by default

- what the answer means
- why it matters
- what is known
- what may vary
- when it was reviewed or updated

### Hide these by default

- raw scores
- trace IDs
- quality bands
- assumption set IDs
- method profile strings
- provenance hashes
- raw tables

### Keep available

- explain this result
- show method
- show known limits
- show trace
- view raw data

This preserves Parva's truth-first philosophy without overwhelming the user.

## Zero-Budget Implementation Priorities

## Phase 0: Remove visible trust killers

Fix first:

- homepage `Invalid Date`
- any raw localhost references that leak into public docs/surfaces users touch
- any broken or low-value SVGs in primary views
- any above-the-fold jargon labels
- raw feed URL exposure on consumer surfaces
- mobile header overflow

## Phase 1: Build the real front door

- add a landing page at `/`
- move current compass to `/today`
- create 3-4 intent paths
- simplify top navigation
- move expert controls behind a secondary panel

## Phase 2: Reframe the answers

- rewrite result summaries in plain language
- convert numeric-heavy blocks into ranked or labeled outcome cards
- move glossary sections below the main answer
- make "explainability" opt-in, not always co-equal

## Phase 3: Rethink Kundali

- create a narrative-first kundali summary
- reduce graph prominence
- translate chart structure into life-area explanations
- keep raw graha table as advanced view

## Phase 4: Split consumer and operator surfaces

- developer/institution/access content should remain accessible but separate
- do not let API or operational concepts shape the consumer shell
- reuse the calmer portal design language for landing/about pages

## Phase 5: Polish for luxury

- replace dashboard card sameness with deliberate panel types
- remove particle dependence
- add a stronger art direction system
- tighten spacing and rhythm
- use fewer but better animations

## What Should Be Removed or Demoted

- global exposure of `Authority` mode
- global exposure of `Quality` selector
- raw URLs in feeds
- excessive badges and uppercase eyebrow labels
- giant raw tables in the main reading flow
- direct raw trace output in end-user detail pages
- dark-glow everywhere
- any language that sounds like internal implementation

## What Should Be Added

- proper landing page
- plain-language summaries
- a clear "why trust this" section
- result cards with action implications
- a region/context note where applicable
- human-facing known-limits language
- onboarding for place/time/purpose
- more curated festival storytelling

## Success Criteria

You will know the redesign is working when a new user can:

1. explain what Parva does in one sentence after 10 seconds
2. get one useful answer without learning jargon first
3. describe why the result feels trustworthy
4. distinguish consumer and expert surfaces naturally
5. use the product on mobile without header fatigue

## Practical Zero-Budget Research Plan

You asked for zero budget, so the validation loop has to be scrappy.

### Week 1

- show 3 static redesign directions to 5-8 people
- ask them to describe what the product does after 5 seconds
- ask what they trust and what confuses them

### Week 2

- test a clickable first-run flow
- watch whether they choose Today, Personal Day, Good Time, or Birth Chart
- record where they hesitate

### Week 3

- test the new kundali summary with users who are curious but not expert
- ask them what value they got before seeing the chart

### Week 4

- test with 2 groups
- Nepali users familiar with patro/panchanga
- diaspora or adjacent users who need more explanation

Success metric:

- users should speak in outcomes, not interface labels

If they say:

- "I saw my best time"
- "I understood today's significance"
- "I trusted the chart summary"

that is good.

If they say:

- "I changed the quality band"
- "I opened the trace"
- "I saw a graph"

that means the product is still leading with the wrong things.

## Final Judgment

Project Parva has the raw ingredients for a genuinely exceptional product.

But the frontend currently undersells the engine and overexposes the machinery.

The most important change is not "make it prettier."

It is:

`change the product from a visible computation surface into a guided trust experience`

If you do that well, Parva can become:

- culturally resonant
- visually memorable
- emotionally reassuring
- operationally credible
- commercially viable even with generous free access

If you do not, it will continue to look like a smart project that normal users admire briefly and then abandon.

## External Sources

- Stanford Web Credibility Guidelines: https://credibility.stanford.edu/guidelines/
- Nielsen Norman Group, 10 Usability Heuristics for User Interface Design: https://www.nngroup.com/articles/ten-usability-heuristics/
- Hamro Patro app and feature surfaces: https://www.hamropatro.com/apps/nepali-patro and https://hamropatro.com/features
- Drik Panchang: https://www.drikpanchang.com/
- timeanddate: https://www.timeanddate.com/
- CHANI: https://www.chani.com/
- The Pattern: https://www.thepattern.com/
- Pew Research Center, spirituality among Americans: https://www.pewresearch.org/religion/2025/05/14/spirituality-among-americans/
