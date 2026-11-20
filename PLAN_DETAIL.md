# Detailed implementation plan: My Neighbourhood presentation

## 1. Project alignment with school rubric

Source rubric: `HƯỚNG DẪN LÀM BÀI PROJECT.docx` (Grade 6 English, Topic: My Neighbourhood, Deadline: 24:00 Sunday 29/11/2026).

- **Group name and members (6 students)**:
  1. **Gia Khanh** (Group Leader): Planning, coordination, opening greeting, Pair 1 questioner (to Market), contribution ledger owner.
  2. **Phuoc**: Content writer and speaker, neighbourhood places overview, Pair 1 guide (to Market).
  3. **Yen Nhi**: Content writer and speaker, location prepositions lead, Pair 2 questioner (to Hospital).
  4. **Anh Thi**: Speaker and pronunciation checker, key vocabulary guide, Pair 2 guide (to Hospital).
  5. **Tung Lam**: Speaker and map decorator, Pair 3 questioner (to Park), closing favourite place speaker.
  6. **Tuan Anh**: Slide designer and speaker, Pair 3 guide (to Park), closing thank-you and Q&A map navigator.
- **Required three-part flow**:
  - **Part 1 (Introduction)**: Slides 1 and 2 greet the class, introduce all 6 students, name the imagined neighbourhood (`Greenleaf Neighbourhood`), and deliver the suggested prompt sentence.
  - **Part 2A (Designing the map)**: Slide 3 renders an interactive Street Atlas and 3D Blender Diorama toggle with 10 places (exceeding the minimum 5), 4 named streets, N/E/S/W compass rose, and map legend.
  - **Part 2B (Describing places and locations)**: Slides 4 and 5 present all 10 places with pronunciation and English sentences, then demonstrate all 6 required prepositions (`next to`, `opposite`, `between`, `in front of`, `behind`, `near`) paired with the 3 rubric Q&A prompts.
  - **Part 2C (Asking and giving directions)**: Slides 6, 7, and 8 stage three live pair dialogues matching exact verified street turns and left/right geometry.
  - **Part 3 (Conclusion & Team Accountability)**: Slides 9, 10, 11, and 12 summarize key vocabulary, report individual contributions per group-leader requirements, highlight the favourite place (`Park`), deliver the exact closing speech, and jump back to the live map for Q&A.

## 2. Single-source-of-truth coordinate and route geometry

Coordinate frame: `+X` = East, `+Y` = North (`-Y` in SVG canvas), ground plane `Z = 0.0m`. SVG viewport maps `x in [-18, +21]` and `y in [-11, +15]` at `20px/m` into `viewBox="0 0 780 520"`.

### Street corridors (2.6m asphalt, 3.6m total corridor including sidewalks)

| Street | Axis | Center (m) | Corridor bounds (m) | Span (m) | Role |
|---|---|---|---|---|---|
| Oak Street | East-West | `y = +6.0` | `y in [+4.2, +7.8]` | `x in [-16, +19]` | Upper street (My House, School, Park) |
| Maple Street | East-West | `y = -6.0` | `y in [-7.8, -4.2]` | `x in [-16, +19]` | Lower main street (Post Office, Restaurant, Bookstore, Bus Stop) |
| Pine Street | North-South | `x = -2.0` | `x in [-3.8, -0.2]` | `y in [-11, +14]` | 1st cross street from West (Market faces West) |
| River Road | North-South | `x = +12.0` | `x in [+10.2, +13.8]` | `y in [-11, +14]` | 2nd cross street from West (Supermarket faces East, Hospital faces West) |

### Landmarks (10 buildings, zero overlaps)

| ID | Name | Center `(x, y)` | Size `W x D` (m) | Facing | Blender Asset |
|---|---|---|---|---|---|
| `my-house` | My House | `(-9.5, +10.5)` | `4.0 x 3.4` | South onto Oak St | `assets/blender/my-house.png` |
| `school` | School | `(+2.2, +10.5)` | `4.2 x 3.6` | South onto Oak St | `assets/blender/school.png` |
| `park` | Park | `(+7.5, +10.5)` | `4.8 x 3.6` | South onto Oak St | `assets/blender/park.png` |
| `post-office` | Post Office | `(-13.0, -1.5)` | `3.2 x 3.0` | South onto Maple St | `assets/blender/post-office.png` |
| `restaurant` | Restaurant | `(-9.2, -1.5)` | `3.4 x 3.0` | South onto Maple St | `assets/blender/restaurant.png` |
| `bookstore` | Bookstore | `(-5.6, -1.5)` | `2.8 x 3.0` | South onto Maple St | `assets/blender/bookstore.png` |
| `bus-stop` | Bus Stop | `(-5.6, -4.3)` | `2.2 x 1.1` | South curb of Maple St | `assets/blender/bus-stop.png` |
| `market` | Market | `(+2.5, 0.0)` | `4.2 x 4.6` | West onto Pine St | `assets/blender/market.png` |
| `supermarket` | Supermarket | `(+7.6, 0.0)` | `4.2 x 4.6` | East onto River Rd | `assets/blender/supermarket.png` |
| `hospital` | Hospital | `(+16.2, 0.0)` | `4.4 x 4.8` | West onto River Rd | `assets/blender/hospital.png` |

### Verified preposition pairs (Slide 5)

1. `next to`: School `(+2.2, +10.5)` and Park `(+7.5, +10.5)` share the north block of Oak Street (`0.8m` clearance).
2. `opposite`: Hospital `(+16.2, 0.0)` and Supermarket `(+7.6, 0.0)` face directly across River Road.
3. `between`: Restaurant `(-9.2, -1.5)` stands directly between Post Office `(-13.0, -1.5)` and Bookstore `(-5.6, -1.5)`.
4. `in front of`: Bus Stop `(-5.6, -4.3)` sits on the Maple Street north sidewalk directly in front of Bookstore `(-5.6, -1.5)`.
5. `behind`: Bookstore `(-5.6, -1.5)` stands directly behind Bus Stop `(-5.6, -4.3)` when viewed from Maple Street.
6. `near`: My House `(-9.5, +10.5)` is near School `(+2.2, +10.5)` along Oak Street.

### Verified direction routes (Slides 6, 7, 8)

1. **Slide 6 (Gia Khanh to Phuoc: Market)**: Waypoints `(-15.0, -6.0)` -> `(-2.0, -6.0)` -> `(-2.0, 0.0)` -> target `(+2.5, 0.0)`. Cross product at Pine St turn: `+13 * (+6) = +78 > 0` (turn left at first street). Cross product to Market from Pine St going North: `-(+6 * +4.5) = -27 < 0` (on your right).
2. **Slide 7 (Yen Nhi to Anh Thi: Hospital)**: Waypoints `(-15.0, -6.0)` -> `(-2.0, -6.0)` -> `(+12.0, -6.0)` -> `(+12.0, 0.0)` -> target `(+16.2, 0.0)`. Passes 1st street (Pine St) to 2nd street (River Rd). Cross product at River Rd turn: `+27 * (+6) = +162 > 0` (second turning on the left). Cross product to Hospital going North: `-(+6 * +4.2) = -25.2 < 0` (on your right, opposite Supermarket).
3. **Slide 8 (Tung Lam to Tuan Anh: Park)**: Waypoints `(-2.0, 0.0)` -> `(-2.0, +6.0)` -> `(+7.5, +6.0)` -> target `(+7.5, +10.5)`. Starts outside Market on Pine St facing North. Cross product at Oak St turn: `-(+6 * +9.5) = -57 < 0` (turn right onto Oak St). Cross product to Park going East past School: `+9.5 * (+4.5) = +42.75 > 0` (on your left, next to School).

## 3. Twelve-slide structure and interactive modules

- **Slide 1 (Cover Plate)**: 60/40 split with title, subtitle, 6-member speaker strip, and `overview-diorama.png` hero plate + compass seal.
- **Slide 2 (Introduction)**: Spoken greeting quote in Fraunces plus `my-house.png` and `park.png` specimen plates and speaker introduction badges.
- **Slide 3 (Interactive Neighbourhood Atlas)**: Mode toggle between crisp SVG Street Atlas and 3D Blender Diorama pin overlay, clickable 10-landmark pins updating a live Inspector Card (`*.png` preview, pronunciation, street, description), compass rose, and legend.
- **Slide 4 (Places in Our Neighbourhood)**: `5x2` desktop grid (`2x5` tablet, `1x10` mobile) displaying all 10 Blender PNGs with phonetic tips and English sentences. Clicking any card opens `<dialog id="place-lightbox" closedby="any">`.
- **Slide 5 (Describing Locations)**: Interactive 6-preposition selector + 3 rubric Q&A prompt tabs (`What places are there?`, `Where is the...?`, `Is it near or far from...?`) driving live SVG sightline brackets and Blender pair thumbnails.
- **Slide 6 (Directions Pair 1: Market)**: Gia Khanh and Phuoc dialogue transcript + step-by-step GSAP route map with `Play route` / `Pause route`, `Replay`, `Next step`, and `market.png` preview.
- **Slide 7 (Directions Pair 2: Hospital)**: Yen Nhi and Anh Thi dialogue transcript + animated route map passing Pine St to River Rd + `hospital.png` and `supermarket.png` preview.
- **Slide 8 (Directions Pair 3: Park)**: Tung Lam and Tuan Anh dialogue transcript + animated route map from Market up Pine St onto Oak St + `park.png` and `school.png` preview.
- **Slide 9 (Key Vocabulary & Spatial Reference)**: 10 places ledger strip + 6 crisp geometric SVG spatial diagrams + 4 wayfinding arrow diagrams.
- **Slide 10 (Teamwork & Contribution Ledger)**: Group leader Gia Khanh overview + full 6-student contribution table (Role, Tasks, Speaking Turn, Status).
- **Slide 11 (Conclusion & Favourite Place)**: Featured `park.png` plate + summary points + exact rubric closing speech quote.
- **Slide 12 (Thank You & Live Q&A)**: Final credits plate with `overview-diorama.png` and a single primary CTA button jumping directly to Slide 3 Interactive Map for classroom Q&A.

## 4. File structure and offline integration

- `index.html`: Single-page 12-slide presentation shell with global header, stage, footer dock, `<dialog id="place-lightbox">`, `<dialog id="slide-overview-dialog">`, and `<dialog id="presenter-notes" popover="manual">`.
- `styles/tokens.css`: Palette, typography, spacing, and z-index custom properties.
- `styles/base.css`: Reset, typography defaults, top bar, bottom dock, focus rings, and responsive breakpoints.
- `styles/slides.css`: Per-slide asymmetric grids, SVG Atlas theme, preposition badges, and route canvas styling.
- `styles/dialogs.css`: View Transitions (`slide-stage`), `@starting-style`, `overlay`, `transition-behavior: allow-discrete`, `overscroll-behavior: contain`, and popover drawer styles.
- `scripts/map-data.js`: Pure declarative data module (`window.ATLAS_DATA`) matching Blender 1:1.
- `scripts/icons.js`: Offline SVG icon resolver backed by `assets/icons/sprite.svg` and `vendor/lucide.min.js`.
- `scripts/atlas-svg.js`: Interactive SVG Atlas builder, sightline highlight renderer, and GSAP route animator.
- `scripts/deck.js`: Navigation state, directional View Transitions, keyboard controls, `<dialog>` lightbox & grid handlers, `closedby="any"` and `data-closing` fallbacks, and `<dialog popover="manual">` presenter script drawer.
