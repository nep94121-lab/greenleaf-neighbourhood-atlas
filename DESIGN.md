# Design system: Greenleaf Neighbourhood

## 1. Visual theme and atmosphere

Greenleaf Neighbourhood is a 12-slide interactive classroom presentation for six Grade-6 students studying English wayfinding and spatial prepositions. The interface uses an Illustrated Atlas aesthetic inspired by architectural site plans and tactile classroom storybooks. Density stays calibrated at level 5 (daily-app balanced, one primary visual stage and one clean reading zone per slide) with asymmetric 60/40 and 70/30 splits on desktop. Variance stays at level 7 (offset asymmetric composition across slides) and motion stays at level 5 (crisp directional view transitions and purposeful route playback). Every element occupies its own spatial zone with clear whitespace, paper borders, and physical 3D landmark renders from Blender 5.2.2 LTS.

## 2. Color palette and roles

All colors share a warm archival paper temperature paired with deep charcoal ink and one primary forest-pine accent. Pure black `#000000` and neon or purple gradients are prohibited.

- **Archival Paper (`#F6F4EE`)**: Primary viewport and slide canvas background.
- **Crisp Plate (`#FFFFFF`)**: Elevated specimen plates, inspector cards, dialogue panels, and modal surfaces.
- **Drafting Sand (`#EFECE3`)**: Secondary inset wells behind 3D landmark renders, legend strips, and table headers.
- **Drafting Border (`#D8D3C8`)**: 1px structural plate borders, grid dividers, and map registration lines.
- **Charcoal Ink (`#171C22`)**: Primary headings, body copy, and road labeling (contrast > 14:1 on `#F6F4EE`).
- **Muted Slate (`#4D5761`)**: Secondary captions, phonetic pronunciation guides, and slide metadata (contrast > 6.4:1 on `#F6F4EE`).
- **Atlas Pine (`#1B6B4A`)**: Primary brand and interactive accent for active tabs, CTA buttons, focus rings, and focus highlights (contrast > 6.2:1 with `#FFFFFF`).
- **Signal Vermilion (`#C84B31`)**: Cartographic wayfinding marker reserved strictly for active direction route paths, turn nodes, start pins, and destination targets.
- **Park Wash (`#DCE8DF`)**: Soft vegetative fill used inside SVG map park parcels and tree canopies.
- **Asphalt Slate (`#E4DFD3`) & Sidewalk Stone (`#EDE9DE`)**: Muted neutral street surfaces inside the SVG Neighbourhood Atlas so colorful 3D landmarks and vermilion routes read clearly.

## 3. Typography rules

All four typefaces are self-hosted locally in `vendor/fonts/` via `vendor/fonts/fonts.css` under SIL OFL 1.1 and verified for complete 151/151 Vietnamese Unicode coverage in NFC form.

- **Display (`Bricolage Grotesque`)**: Slide titles and cover header. Weight 700, tight tracking (`-0.025em`), `line-height: 1.15`, `text-wrap: balance`, sentence case. Zero isolated single-word highlight spans inside headings.
- **Body and UI (`Be Vietnam Pro`)**: Interface controls, location descriptions, tables, and presenter notes. Weight 400 and 600, `line-height: 1.55`, minimum `14px` (`0.875rem`) on labels and `16px` (`1rem`) on body paragraphs, maximum `65ch` measure.
- **Editorial Spoken Quotes (`Fraunces`)**: Character greeting quotes and pair-dialogue spoken bubbles. Weight 500, `line-height: 1.45`, strictly NFC-normalized text. Banned inside navigation bars, data tables, or coordinate tags.
- **Cartographic Metadata (`Geist Mono`)**: Coordinate tags `(-9.5, +10.5)`, street indexes, and slide counter `03 / 12` using `font-variant-numeric: tabular-nums`.
- **Banned Fonts**: `Inter`, `Roboto` defaults, `Times New Roman`, `Georgia`, `Garamond`, and any unverified Google font lacking Vietnamese diacritic coverage.
- **Vietnamese String Rule**: All Vietnamese strings are normalized to NFC. Text splitting never uses `String.prototype.split('')`; it uses `Intl.Segmenter('vi', { granularity: 'grapheme' })`.

## 4. Component stylings

- **Navigation Chrome**: Fixed compact top bar (`52px`) and bottom control dock (`56px`) styled in `#FFFFFF` with `1px solid #D8D3C8` borders. Controls use minimum `44px` tap targets on interactive buttons and visible `2px solid #1B6B4A` focus outlines (`outline-offset: 2px`).
- **Buttons**: Flat tactile surfaces with `1px` crisp borders and subtle `-1px` vertical translate on active press. Primary actions fill `#1B6B4A` with `#FFFFFF` text. Route playback toggle switches label cleanly between `"Play route"` and `"Pause route"` without `aria-pressed` (WCAG 2.2.2 compliance).
- **Plates and Specimen Cards**: Softly calibrated corners (`12px` for interactive plates, `8px` for inner specimen wells) with warm hairline shadows tinted to `#171C22` at `6%` opacity. No identical 3-column horizontal SaaS card rows.
- **Native Modal Dialogs**: Specimen lightbox (`#place-lightbox`) and Slide Grid (`#slide-overview-dialog`) use `<dialog closedby="any">` opened via `showModal()`. Both enforce `overscroll-behavior: contain` on `dialog:modal` and `dialog::backdrop`, `transition-behavior: allow-discrete` with `overlay` and `@starting-style`, `pointerdown`/`pointerup` outside-bounds fallback when `closedBy` is unsupported, and `dialog.returnValue = ''` reset on `close`.
- **Non-Modal Presenter Drawer**: `#presenter-notes` uses `<dialog popover="manual">` with a visible Close button (`command="hide-popover"`) so the presentation stage stays interactive underneath.

## 5. Layout principles

- **Viewport Framing**: Every desktop slide fits comfortably inside `100dvh` (`1280x720` and `1440x900`) between top and bottom chrome without cutting headings or buttons, while allowing smooth vertical scroll on constrained screens and collapsing cleanly to single column below `768px` (`390x844` verified, zero horizontal overflow).
- **CSS Grid First**: All multi-zone slide stages use explicit CSS Grid templates (`60fr 40fr`, `68fr 32fr`, `5x2` desktop grid collapsing to `2x5` / `1x10`). Zero `calc()` percentage layout hacks or absolute-positioned overlapping text over images.
- **Visual Grounding**: Every single slide renders either crisp transparent Blender 5.2.2 LTS PNG assets (`assets/blender/*.png`), the interactive SVG Street Atlas, or geometric vector preposition charts.

## 6. Motion and interaction

- **Directional View Transitions**: Slide changes pass `'forward'` or `'backward'` to `document.startViewTransition({ update, types: [dir] })` targeting `::view-transition-group(slide-stage)` with `transform: translateX()` keyframes (`0.36s cubic-bezier(0.22, 1, 0.36, 1)`), bypassed cleanly under `@media (prefers-reduced-motion: reduce)`.
- **Compositor-Only Route Playback**: Slides 6, 7, and 8 animate a directional marker (`transform` and `opacity` only) along the mathematically verified route polyline via GSAP 3.15.0, paired with step-by-step highlight controls and static full-route fallback when reduced motion is active.
- **No Auto-Blocking Flash or Loops**: Zero flashing elements (>3 Hz banned) and zero decorative looping text animations.

## 7. Anti-patterns (banned)

- Zero Unicode emojis anywhere in HTML, CSS, JS, SVG, or Markdown. Use only offline SVG icons from `assets/icons/sprite.svg` or `vendor/lucide.min.js`.
- Zero `Inter` or generic system fallback headlines.
- Zero pure black `#000000`, neon glows, glassmorphic purple washes, or multi-stop gradient headers.
- Zero 3-column equal SaaS feature cards.
- Zero tracked-out all-caps eyebrow labels above every heading, zero `LABEL // YEAR` tags, zero `WORD (em-dash) fragment` headers, and zero `->` symbols appended to button copy.
- Zero filler phrases (`"Scroll to explore"`, `"Swipe down"`), zero fabricated metrics (`"99.9% accuracy"`), and zero em-dash characters (`U+2014`) in UI or prose.
- Zero external runtime CDN calls so the presentation works 100% offline in class.
