# Design System Documentation: The Sacred Almanac

## 1. Overview & Creative North Star
**Creative North Star: "The Digital Mandir"**

This design system transcends the utility of a standard calendar to become a high-end digital sanctuary. It rejects the "app-like" density of modern productivity tools in favor of **High-End Editorial** aesthetics—mimicking the tactile experience of a bespoke art book or a hand-pressed lithograph. 

The system breaks the "template" look through:
*   **Intentional Asymmetry:** Off-center typography and staggered image placements that mirror the organic flow of spiritual contemplation.
*   **Breathing Room:** Utilizing extreme whitespace (Scaling 16–24) to frame content as art rather than data.
*   **Devanagari Integration:** Treating script not just as text, but as a decorative, structural element that grounds the interface in Nepali/Hindu heritage.

---

## 2. Colors & Surface Philosophy
The palette is a dialogue between the earth (Sandalwood), the divine (Saffron), and the celestial (Charcoal).

### The "No-Line" Rule
Traditional 1px solid borders are strictly prohibited for sectioning. Structural boundaries must be defined through:
*   **Tonal Shifts:** Transitioning from `surface` (#fff8f3) to `surface-container-low` (#fff2e2).
*   **Negative Space:** Using large gaps (Scale 12+) to imply the end of a content block.

### Surface Hierarchy & Nesting
Treat the UI as a series of stacked, fine-paper sheets. 
*   **Base:** `surface` (#fff8f3).
*   **Sectioning:** Use `surface-container` (#fbecd9) for large content areas.
*   **Focus Elements:** Use `surface-container-highest` (#efe0cd) for cards or highlighted spiritual events.

### The "Glass & Gold" Rule
To achieve a premium feel, floating elements (modals, navigation bars, moon phase details) must use **Glassmorphism**.
*   **Spec:** `surface-variant` (#efe0cd) at 60% opacity with a `20px` backdrop-blur.
*   **Gold Accents:** Use `tertiary` (#735c00) for thin (0.5px) "Ghost Borders" on glass elements to mimic metallic gold leafing.

---

## 3. Typography
The typography is a marriage of authoritative tradition and modern clarity.

*   **Display & Headlines (Playfair Display/Noto Serif):** Use `display-lg` for dates and major festivals. These should feel like titles in a premium editorial.
*   **Body (Inter):** Reserved for descriptions, astronomical data, and ritual instructions. It provides a neutral, grounding counterpoint to the serif's flair.
*   **Labels (Inter + Devanagari):** Labels should pair a small `label-sm` English tag with its Devanagari equivalent in a slightly larger, lighter weight to create a bilingual tapestry.

**Hierarchy Note:** Always favor extreme contrast. Pair a `display-lg` headline with a `body-sm` description to create visual "soul."

---

## 4. Elevation & Depth
In this system, depth is "felt" through light and texture, never "forced" through heavy shadows.

*   **The Layering Principle:** Depth is achieved by stacking. A `surface-container-lowest` card placed on a `surface-container-low` background creates a "lift" that is felt by the eye without the clutter of a shadow.
*   **Ambient Shadows:** If a floating state is required (e.g., a ritual picker), use an extra-diffused shadow: `box-shadow: 0 20px 50px rgba(88, 66, 56, 0.08)`. The color is a tint of `on-surface-variant`, not grey.
*   **Ghost Borders:** If accessibility requires a container boundary, use the `outline-variant` (#e0c0b2) at 20% opacity. 

---

## 5. Components

### Cards & Event Lists
*   **Rule:** Forbid divider lines. Use `spacing-8` or `spacing-10` between items.
*   **Styling:** Use `surface-container-low` for the card body. Use an asymmetrical `0.25rem` (sm) corner radius on the top-left and bottom-right only to create a "leaf-like" custom feel.

### Buttons
*   **Primary:** `primary` (#9c3f00) background with `on-primary` text. No rounded corners (`none`). Use a `0.5px` gold border (`tertiary`).
*   **Secondary/Tertiary:** Text-only with a subtle `tertiary-fixed` underline that only spans 50% of the text width.

### Moon Phase Chips
*   **Design:** Circular icons using `outline-variant` for the "dark" side of the moon and `tertiary-fixed-dim` for the "lit" side. Pair with `label-md` typography.

### Input Fields
*   **Style:** Minimalist under-line only. Use `outline` (#8c7166) at 40% opacity. Upon focus, the line transitions to `primary` (#9c3f00) and the label shifts upward using `label-sm`.

---

## 6. Do’s and Don’ts

### Do:
*   **Do** use the `24` (8.5rem) spacing token for hero section margins to create an "Art Gallery" feel.
*   **Do** let the `secondary-container` color act as a soft "wash" over image backgrounds to ensure text legibility.
*   **Do** use glassmorphism for top navigation bars so the spiritual imagery "bleeds" through as the user scrolls.

### Don’t:
*   **Don’t** use pure black (#000000). Use `on-surface` (#221a0f) for all "black" text to maintain warmth.
*   **Don’t** use standard `lg` or `xl` rounded corners. This system is "High-End Editorial"; keep corners sharp (`none`) or very subtle (`sm`) to mimic trimmed paper.
*   **Don’t** use icons from standard libraries (Material, FontAwesome). Use custom, thin-stroke (0.75px) iconography that mimics ink drawings.