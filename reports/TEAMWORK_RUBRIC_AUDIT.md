# Read-Only Rubric, Grade-6 English, and Anti-Slop Audit Report

Target project: `c:\Users\LENOVO\Desktop\test 4 agron\my-neighbourhood-slides\`
Audit date: 2026-11-20
Audit scope: Read-only evaluation of `index.html`, `styles/`, `scripts/`, `DESIGN.md`, `PLAN_DETAIL.md`, `assets/manifests/resources-verified.json`, `qa/geometry_proof_results.json`, `qa/playwright_audit_results.json`, `qa/blender_asset_metrics.json`, `qa/license_audit_results.json`, `reports/QA_AUDIT_LOG.md`, and `qa/screenshots/`.

---

## Executive summary and verdict

**Overall verdict: PASS WITH REMEDIATION ITEMS (CONDITIONAL PASS)**

The 12-slide presentation passes all five teacher grading criteria, all mandatory project sections, 6-student balanced participation, spatial geometry truthfulness against the SVG map and 3D diorama, offline vendor bundling, 48/48 SHA-256 manifest verification, visual screenshot quality, and anti-slop encoding rules. Before final submission, two Major British English IPA errors (`IPA-02`, `IPA-03`) and five Minor editorial, grammar, attribution, and speaker-tip defects (`EN-02`, `EN-03`, `EN-04`, `EN-05`/`D-R1`, `VI-03`) should be corrected for textbook consistency. Four non-blocking informational notes (`D-R2`, `D-R3`, `D-R4`, optional multi-word IPA stress marks in `IPA-01`, and the curbside bus-bay note) are also logged below.

### Summary scorecard across audit pillars

| Pillar | Items checked | Pass | Fail (Major) | Fail (Minor) | Pillar verdict |
|---|---|---|---|---|---|
| 1. Teacher rubric, content, and 6-student teamwork | 19 (`R-01`..`R-19`) | 19 | 0 | 0 (4 wording/metadata notes) | **PASS** |
| 2. Grade-6 English, IPA, Vietnamese NFC, and spatial truthfulness | 21 (`EN-01`..`EN-06`, `IPA-01`..`IPA-03`, `VI-01`..`VI-03`, `SP-01`..`SP-09`) | 14 | 2 (`IPA-02`, `IPA-03`) | 5 (`EN-02`..`EN-05`, `VI-03`) | **CONDITIONAL PASS** |
| 3. Anti-slop, encoding, offline vendor, contrast, and visuals | 10 (`AS-01`..`AS-10`) | 10 | 0 | 0 | **PASS** |
| **Total** | **50** | **43** | **2** | **5** | **PASS WITH REMEDIATION ITEMS** |

---

## Section 1: Teacher rubric, mandatory content, and 6-student teamwork audit

### 1.1 Numbered rubric and manifest checklist (`R-01` to `R-19`)

| ID | Rubric / manifest item | Status | Verified evidence (file paths and lines) |
|---|---|---|---|
| `R-01` | Topic and title ("CHỦ ĐỀ: MY NEIGHBOURHOOD" / "MY NEIGHBOURHOOD MAP - LET'S FIND THE WAY!") | **PASS** | `index.html:6` (`My Neighbourhood: Let's Find the Way! | Greenleaf Neighbourhood`), `index.html:57-58` (`My Neighbourhood` / `Let's Find the Way! (Greenleaf Neighbourhood)`), `scripts/map-data.js:6`, `scripts/map-data.js:546`. See note `D-R2` for omitted `"Map"` in Slide 1 subtitle. |
| `R-02` | Deadline context (before 24:00 Sunday 29/11/2026) | **PASS** | `PLAN_DETAIL.md:5` (`24:00 Sunday 29/11/2026`), `scripts/map-data.js:9` (`29/11/2026`), `index.html:455` (`Submission Deadline: 29/11/2026`). See note `D-R3` for full time-of-day phrase. |
| `R-03` | Part 1: Greet class and sample lead-in | **PASS** | `scripts/map-data.js:546` (`"Good morning teacher and classmates!"`), `index.html:103-105` (`"Hello everyone! Welcome to our neighbourhood. This is our map. It shows some interesting places in our neighbourhood. Let's have a look!"`), `scripts/map-data.js:552`. |
| `R-04` | Part 1: Introduce all 6 members | **PASS** | `index.html:62` (`#cover-roster`), `index.html:119` (lists Gia Khanh, Phước, Yến Nhi, Anh Thi, Tùng Lâm, Tuấn Anh), `scripts/map-data.js:481-541`, `scripts/map-data.js:546`. |
| `R-05` | Part 1: Name neighbourhood and state real vs imagined | **PASS** | Named `"Greenleaf Neighbourhood"` (`index.html:22,58,93`, `scripts/map-data.js:7`). Stated as imagined on Slide 2 (`index.html:111`: `"An imagined neighbourhood designed by our team"`) and in presenter script (`scripts/map-data.js:552`). |
| `R-06` | Part 2A: Clear streets and >=5 English-labeled places (10 provided) | **PASS** | Four named streets (`Oak Street`, `Maple Street`, `Pine Street`, `River Road`) in `scripts/map-data.js:20-73` and `scripts/atlas-svg.js:194-199`. All 10 English-labeled places (`My House`, `School`, `Park`, `Post Office`, `Restaurant`, `Bookstore`, `Bus Stop`, `Market`, `Supermarket`, `Hospital`) in `scripts/map-data.js:74-245`, `index.html:183-190,223`, and `scripts/atlas-svg.js:203-298`. |
| `R-07` | Part 2A: Compass, scale/arrows, and legend | **PASS** | Compass rose N/S/E/W (`scripts/atlas-svg.js:309-317`), 3 m scale bar (`scripts/atlas-svg.js:320-326`), map legend (`index.html:176-180`: `Building`, `Park`, `Door facing street`), entrance door notches (`scripts/atlas-svg.js:250-256`), route arrows (`scripts/atlas-svg.js:541-546,587-590`), and Slide 9 direction cards (`scripts/map-data.js:475-480`). |
| `R-08` | Part 2B: Required Q&A prompts | **PASS** | `index.html:248-251` and `scripts/map-data.js:320-336` present all three required question stems: `"What places are there in your neighbourhood?"`, `"Where is the market?"`, and `"Is your house near or far from the hospital?"`. |
| `R-09` | Part 2B: All 6 prepositions (`next to`, `opposite`, `between`, `behind`, `in front of`, `near`) | **PASS** | `scripts/map-data.js:246-319` defines all 6 prepositions. Interactive on Slide 5 (`index.html:241-256`), summarized on Slide 9 (`index.html:430-433`), and verified in `qa/geometry_proof_results.json:58-111`. |
| `R-10` | Part 2C: Pairs roleplay and required direction phrases | **PASS** | Three pairs on Slides 6-8 (`scripts/map-data.js:337-474`, `index.html:261-408`): Pair 1 Gia Khanh & Phước (Market), Pair 2 Yến Nhi & Anh Thi (Hospital), Pair 3 Tùng Lâm & Tuấn Anh (Park). Covers `"Could you tell me the way to..."`, `"How can I get to..."`, `"Go straight ahead"`, `"Turn left / Turn right"`, `"take the second turning on the left"`, and `"on your left / right"`. |
| `R-11` | Part 3: Conclusion (summary, favourite place, closing) | **PASS** | Slide 11 (`index.html:476-514`) states summary points (`502-506`), favourite place `Greenleaf Park` (`480,489-497,501,504`), and closing quote (`509-511`: `"That is our neighbourhood map. We hope you like it. Thank you for listening!"`). Slide 12 provides a live Q&A jump button to Slide 3 (`532-535`). |
| `R-12` | Criterion 1: Content | **PASS** | Covers all three required parts, 10 landmarks (>=5 required), 4 streets, 6 prepositions, 3 verified routes, and team contribution ledger. |
| `R-13` | Criterion 2: English skills | **PASS** | Grade-6 vocabulary, full IPA transcriptions for 10 places, 6 prepositions, and 4 direction phrases (`scripts/map-data.js:78-480`), plus Vietnamese pronunciation tips (`547-613`). Two Major IPA defects (`IPA-02`, `IPA-03`) and four Minor copy/grammar slips (`EN-02`..`EN-04`, `VI-03`) are logged in Section 2 and Section 4. |
| `R-14` | Criterion 3: Creativity | **PASS** | Warm archival Illustrated Atlas (`#F6F4EE`), 10 transparent `1024x1024` Blender 5.2.2 LTS PNGs plus 1 `1920x1080` RGB overview diorama (`assets/blender/*.png`), Street Atlas / 3D Diorama toggle (Slide 3), 5x2 lightbox gallery (Slide 4), preposition lab (Slide 5), and GSAP 3.15.0 animated route playback (Slides 6-8). |
| `R-15` | Criterion 4: Teamwork | **PASS** | Slide 10 (`index.html:437-473`) displays Group Leader Gia Khanh's summary banner and 6-member contribution table. All 6 students participate across speaking turns and production roles. Minor Slide 4 metadata mismatch (`EN-05`/`D-R1`) is noted in Section 4. |
| `R-16` | Criterion 5: Presentation and QA status | **PASS** | 12-slide navigation with `<dialog popover="manual">` presenter notes (`index.html:616-638`) and slide grid overview (`602-613`). Both `qa/geometry_proof_results.json` and `qa/playwright_audit_results.json` record `"status": "PASS"` and `"failure_count": 0`. See note `D-R4` on speaker timing cue. |
| `R-17` | Blender assets (10 PNGs + 1 overview diorama) | **PASS** | All 11 PNG files exist in `assets/blender/` (`bookstore.png`, `bus-stop.png`, `hospital.png`, `market.png`, `my-house.png`, `overview-diorama.png`, `park.png`, `post-office.png`, `restaurant.png`, `school.png`, `supermarket.png`) and are referenced in `index.html` and `scripts/map-data.js:87-240`. `qa/blender_asset_metrics.json` reports `PASS` (`11/11`). |
| `R-18` | Offline vendor bundling and zero runtime CDN URLs | **PASS** | Independent scan confirmed 0 external `http://` or `https://` runtime URLs in `index.html`, `styles/*.css`, `scripts/*.js`, `vendor/fonts/fonts.css`, and `assets/icons/sprite.svg`. Verified local `vendor/gsap.min.js`, `vendor/lucide.min.js`, `assets/icons/sprite.svg` (37 symbols), and 40/40 `.woff2` font files. |
| `R-19` | Manifest consistency (`resources-verified.json`) | **PASS** | Independent SHA-256 verification of all 48 entries in `assets/manifests/resources-verified.json` returned 0 missing files and 0 hash mismatches (`48/48` exact match), matching `qa/license_audit_results.json`. |

### 1.2 Six-student balanced participation and Slide 10 ledger cross-check

Data below is cross-checked directly from `scripts/map-data.js` (`students[]` lines 481-541, `routes[]` lines 337-474, `presenterNotes` lines 542-615) and `index.html` speaker chips (`lines 97,158,217-220,235,270,319,369,419,446,484,529`):

| Student | Ledger role (`map-data.js`) | Assigned production tasks | Listed `speakingSlides` (`map-data.js`) | `index.html` speaker chips | `presenterNotes` turns (script words) | Part 2C live dialogue | Balance verdict |
|---|---|---|---|---|---|---|---|
| **Gia Khanh** | Group Leader and MC | Project plan, member tracking, opening welcome, Pair 1 asking directions; led rehearsals & ledger | `Slides 1, 2, 6, 10` (4 slides) | Cover Leader pill, Slides 2, 6, 10 | Slide 1 (32w solo), Slide 2 (32w shared), Slide 6 (40w shared), Slide 10 (23w solo) | Slide 6: 2 turns, 16 words | **Balanced** |
| **Phước** | Content and Pair 1 Guide | Drafted 10-place sentences, gave directions to the Market | `Slides 3, 4, 6` (3 slides) | Slides 3, 6 (Slide 4 chip omits names) | Slide 3 (34w shared), Slide 4 (24w shared), Slide 6 (40w shared) | Slide 6: 2 turns, 18 words | **Balanced** |
| **Yến Nhi** | Content and Pair 2 Asker | Wrote introduction lines, led 6 preposition examples, asked way to Hospital | `Slides 2, 5, 7` (3 slides) | Slides 2, 5, 7 | Slide 2 (32w shared), Slide 5 (50w shared), Slide 7 (49w shared) | Slide 7: 2 turns, 12 words | **Balanced** |
| **Anh Thi** | Pronunciation Checker and Pair 2 Guide | Checked IPA pronunciation, gave directions to Hospital, reviewed vocabulary | `Slides 5, 7, 9` (3 listed; 4 in notes) | Slides 5, 7, 9 (Slide 4 chip omits names) | Slide 4 (24w shared*), Slide 5 (50w shared), Slide 7 (49w shared), Slide 9 (20w solo) | Slide 7: 2 turns, 29 words | **Balanced** (*see `EN-05`/`D-R1`) |
| **Tùng Lâm** | Map Decorator and Pair 3 Asker | Checked street layout and signs, asked way to Park, presented favourite place | `Slides 3, 8, 11` (3 slides) | Slides 3, 8, 11 | Slide 3 (34w shared), Slide 8 (39w shared), Slide 11 (40w shared) | Slide 8: 2 turns, 16 words | **Balanced** |
| **Tuấn Anh** | Slide Designer and Pair 3 Guide | Designed interactive atlas and slides, gave directions to Park, led Q&A map jump | `Slides 8, 11, 12` (3 slides) | Slides 8, 11 (Slide 12 has no chip) | Slide 8 (39w shared), Slide 11 (40w shared), Slide 12 (22w group) | Slide 8: 2 turns, 25 words | **Balanced** |

Cross-check result: Slide 10 (`#teamwork-ledger-body`, `index.html:469`) renders `DATA.students` verbatim (`scripts/deck.js:212-243`). Every student has both non-speaking production responsibilities and 3 to 4 English speaking turns (12 to 29 live Part 2C dialogue words plus slide narration), directly satisfying Section III and Criterion 4.

---

## Section 2: Grade-6 English, IPA accuracy, Vietnamese NFC, and spatial truthfulness audit

### 2.1 Grade-6 English (`EN-01` to `EN-06`)

| ID | Category | Location and verbatim quote | Verdict |
|---|---|---|---|
| `EN-01` | Grade-6 register and mandatory rubric phrases | `index.html:104` (`"Hello everyone! Welcome to our neighbourhood. This is our map. It shows some interesting places in our neighbourhood. Let's have a look!"`) and `index.html:510` (`"That is our neighbourhood map. We hope you like it. Thank you for listening!"`). | **PASS** |
| `EN-02` | BrE/AmE spelling consistency | Project standard is British English (`neighbourhood`, `favourite`, `practised` at `scripts/map-data.js:600`, `Two-storey` at `scripts/map-data.js:242`). Exceptions: `scripts/map-data.js:157` (`"A cozy family bistro..."`), `scripts/map-data.js:281` (`"Centered at x = -9.2m..."`), `scripts/map-data.js:174` (`"bookshop"` vs `"Bookstore"` at `163`), and `scripts/map-data.js:292` (`"sidewalk"`). | **FAIL (Minor)** |
| `EN-03` | Grammar and articles in captions, ledger, and opener | `index.html:331` (`"...on your right opposite Supermarket."`), `index.html:381` (`"North up Pine Street, turn right onto Oak Street past School. On your left."`), `scripts/map-data.js:507` (`"asked way to Hospital"`), `scripts/map-data.js:527` (`"asked way to the Park"`), `scripts/map-data.js:546` (`"Good morning teacher and classmates!"` missing vocative comma / `"teacher"` transfer). | **FAIL (Minor)** |
| `EN-04` | Route 3 dialogue phrasing | `scripts/map-data.js:460` and `588`: `"Go straight ahead onto Oak Street, then turn right."` Walking north on Pine Street, you walk **to** Oak Street before turning right **onto** Oak Street (cf. `steps[1]` at `447`: `"Go straight ahead to Oak Street."`). | **FAIL (Minor)** |
| `EN-05` | Slide 4 speaker credit consistency (`D-R1`) | `scripts/map-data.js:563` (`presenterNotes[4].speakers`) lists `"Phước & Anh Thi"`, whereas `scripts/map-data.js:518` sets Anh Thi's `speakingSlides` to `"Slides 5, 7, 9"` (omitting Slide 4). | **FAIL (Minor)** |
| `EN-06` | General Grade-6 grammar across Slides 1, 2, 4, 5, 6, 7, 9, 10, 11, 12 | Subject-verb agreement, plural forms, capitalization, punctuation, Q&A tabs, specimen sentences, and closing bullets are grammatically accurate and level-appropriate. | **PASS** |

### 2.2 IPA phonemic accuracy (`IPA-01` to `IPA-03`)

| ID | Category | Location and verbatim quote | Verdict |
|---|---|---|---|
| `IPA-01` | BrE phonemic accuracy (17 of 20 citation entries + 2 script tips) | Accurate RP/BrE transcriptions: `/maɪ haʊs/` (`scripts/map-data.js:79`), `/skuːl/` (`96`), `/pɑːk/` (`113`), `/ˈpəʊst ˌɒf.ɪs/` (`130`), `/ˈres.tər.ɒnt/` (`147`), `/ˈbʌs stɒp/` (`181`), `/ˈmɑː.kɪt/` (`198`), `/ˈsuː.pəˌmɑː.kɪt/` (`215`), `/ˈhɒs.pɪ.təl/` (`232,583`), `/nekst tuː/` (`250`), `/ˈɒp.ə.zɪt/` (`262`), `/bɪˈtwiːn/` (`274`), `/ɪn frʌnt əv/` (`286`), `/bɪˈhaɪnd/` (`298`), `/ɡəʊ streɪt əˈhed/` (`476`), `/tɜːn left/` (`477`), `/tɜːn raɪt/` (`478`), `/ˈpleɪ.sɪz/` and `/ˈneɪ.bə.hʊd/` (`553`). Multi-word items (`/maɪ haʊs/`, `/nekst tuː/`, `/ɪn frʌnt əv/`, `/tɜːn left/`, `/tɜːn raɪt/`) can optionally add primary stress marks (`ˈ`). | **PASS** |
| `IPA-02` | BrE rhoticity errors in `Bookstore` and `near` | `scripts/map-data.js:164`: `"/ˈbʊk.stɔːr/"` and `scripts/map-data.js:310`: `"/nɪər/"`. Both append rhotic `-r`, contradicting the project's non-rhotic British English IPA system (`/pɑːk/`, `/ˈsuː.pəˌmɑː.kɪt/`, `/tɜːn/`). BrE citation forms are `/ˈbʊk.stɔː/` and `/nɪə/`. | **FAIL (Major)** |
| `IPA-03` | Phonological and delimiter error in `on your left / right` | `scripts/map-data.js:479`: `"/ɒn jɔːr left / raɪt/"`. In British English, linking `/r/` does not occur before the consonant `/l/` in `left` (`jɔːr left` is invalid BrE, and `/ɒn/` is BrE rather than AmE). The inner `/` also splits the phonemic slash delimiters awkwardly. Replace with `/ɒn jɔː ˈleft/` and `/ɒn jɔː ˈraɪt/` (or `/ɒn jɔː left | raɪt/`). | **FAIL (Major)** |

### 2.3 Vietnamese NFC and speaker-note accuracy (`VI-01` to `VI-03`)

| ID | Category | Evidence | Verdict |
|---|---|---|---|
| `VI-01` | Unicode NFC, BOM, and line endings | Direct Python byte-level check across 33 workspace text files confirms `utf8=True`, `bom=False`, `crlf=0`, `nfc=True` (33/33). `scripts/deck.js:21-37` and `scripts/atlas-svg.js:16` enforce `.normalize("NFC")` and `Intl.Segmenter("vi", { granularity: "grapheme" })`. | **PASS** |
| `VI-02` | Vietnamese student names, glosses, and tone marks | `Gia Khanh`, `Phước`, `Yến Nhi`, `Anh Thi`, `Tùng Lâm`, `Tuấn Anh`, all `meaningVi` entries (`scripts/map-data.js:251-479`), and all `vietnameseTips` (`547-613`) have accurate spelling and tone placement. | **PASS** |
| `VI-03` | Slide 3 Vietnamese speaker tip accuracy | `scripts/map-data.js:559`: `"...để lớp thấy hình 3D xoay góc và câu mô tả."` Slide 3 displays static Blender PNG renders (`my-house.png`, `park.png`, `hospital.png`, etc.), not an interactive rotatable 3D viewport. | **FAIL (Minor)** |

### 2.4 Spatial truthfulness against the SVG atlas and 3D diorama (`SP-01` to `SP-09`)

World coordinate convention verified in `scripts/map-data.js:11-72`, `scripts/atlas-svg.js:308-317`, `blender/spec.py`, and `qa/geometry_proof_results.json`: `+X = East`, `+Y = North` (`-Y` in SVG), `scale = 20 px/m`, `viewBox="0 0 780 520"`. Cross-product convention in world coordinates (`+X` East, `+Y` North): `cross(v_in, v_out) = dx1*dy2 - dy1*dx2`, where `> 0` is **LEFT** and `< 0` is **RIGHT**.

| ID | Spatial claim / route | Coordinate and cross-product proof summary | Verdict |
|---|---|---|---|
| `SP-01` | Coordinate parity, compass rose, and 45 AABB clearances | `scripts/map-data.js` matches `blender/spec.py` and `assets/blender/overview-diorama.png` 1:1. Compass puts N up (`+Y`), S down (`-Y`), E right (`+X`), W left (`-X`). Minimum building-to-building clearance across 45 pairs is `0.5 m` (`post-office`/`restaurant`, `restaurant`/`bookstore`). | **PASS** |
| `SP-02` | `next to` (`School` and `Park`) | `School` `(+2.2, +10.5)` `[0.1, 4.3] x [8.7, 12.3]` and `Park` `(+7.5, +10.5)` `[5.1, 9.9] x [8.7, 12.3]` sit side by side on the north side of Oak Street (`y = +6.0`) in the same block `[Pine St, River Rd]` with a `0.8 m` gap and 0 intervening buildings. | **PASS** |
| `SP-03` | `opposite` (`Hospital` and `Supermarket`) | `Supermarket` `(+7.6, 0.0)` facing east (`x_max = 9.7`) and `Hospital` `(+16.2, 0.0)` facing west (`x_min = 14.0`) face each other (`facing_dot = -1.0`) directly across `River Road` (`x = 12.0`) aligned at `y = 0.0`. | **PASS** |
| `SP-04` | `between` (`Restaurant` between `Post Office` and `Bookstore`) | `Post Office` `x = -13.0` (`[-14.6, -11.4]`), `Restaurant` `x = -9.2` (`[-10.9, -7.5]`), `Bookstore` `x = -5.6` (`[-7.0, -4.2]`), all at `y = -1.5` facing south onto Maple Street with `0.5 m` west and east gaps (`collinear_cross = 0.0`). | **PASS** |
| `SP-05` | `in front of` and `behind` (`Bus Stop` and `Bookstore`) | `Bookstore` at `(-5.6, -1.5)` faces south onto Maple Street (`y_min = -3.0`). `Bus Stop` at `(-5.6, -4.3)` sits `0.75 m` south of `Bookstore` (`y in [-4.85, -3.75]`), facing south. From Maple Street (`y = -6.0`), `Bus Stop` is in front of `Bookstore` and `Bookstore` is behind `Bus Stop`. Note: `Bus Stop` south edge (`-4.85`) extends `0.15 m` past the `-4.70` curb edge as a curbside bay, matching `overview-diorama.png`. | **PASS** |
| `SP-06` | `near` (`My House` and `School`) and Q&A `near/far` | `My House` `(-9.5, +10.5)` to `School` `(+2.2, +10.5)` is `11.7 m` center-to-center (`7.6 m` edge-to-edge), below the `13.7 m` neighbourhood median, whereas `My House` to `Hospital` `(+16.2, 0.0)` is `27.76 m` (farthest corner). `qaPrompts[1]` (`scripts/map-data.js:329`: `"behind the supermarket block and south of the school"`) is true (`Market` at `x = +2.5` is west/behind east-facing `Supermarket` at `x = +7.6` and south of `School` at `x = +2.2, y = +10.5`), though `"behind the supermarket"` is plainer. | **PASS** |
| `SP-07` | Route 1 (Slide 6: Market) | Start `(-15.0, -6.0)` heading East `(1, 0)` on Maple Street. Reach 1st cross street `Pine Street` (`x = -2.0`). `cross((1,0), (0,1)) = +1.0 > 0` = **LEFT** turn heading North `(0, 1)`. At `y = 0.0`, vector to `Market` `(+2.5, 0.0)` is `(+4.5, 0.0)`; `cross((0,1), (4.5,0)) = -4.5 < 0` = **RIGHT**. Matches `scripts/map-data.js:348-380` and `qa/screenshots/slide_06.png`. | **PASS** |
| `SP-08` | Route 2 (Slide 7: Hospital) | Start `(-15.0, -6.0)` heading East `(1, 0)` on Maple Street. Pass 1st street (`Pine Street`, `x = -2.0`) to 2nd cross street (`River Road`, `x = +12.0`). `cross((1,0), (0,1)) = +1.0 > 0` = **LEFT** turn (2nd turning on the left) heading North `(0, 1)`. At `y = 0.0`, vector to `Hospital` `(+16.2, 0.0)` is `(+4.2, 0.0)`; `cross((0,1), (4.2,0)) = -4.2 < 0` = **RIGHT**, directly opposite `Supermarket` (`+7.6, 0.0`) on the left. Matches `scripts/map-data.js:393-427`. | **PASS** |
| `SP-09` | Route 3 (Slide 8: Park) | Start `(-2.0, 0.0)` outside Market's west-facing gate on Pine Street heading North `(0, 1)`. Reach `Oak Street` (`y = +6.0`). `cross((0,1), (1,0)) = -1.0 < 0` = **RIGHT** turn heading East `(1, 0)`. Walk east past `School` (`x = +2.2`) to `Park` (`x = +7.5, y = +10.5`). Vector to `Park` is `(0, +4.5)`; `cross((1,0), (0,4.5)) = +4.5 > 0` = **LEFT**, next to School. Matches `scripts/map-data.js:439-472`. | **PASS** |

---

## Section 3: Anti-slop (`unslop`), encoding, offline vendor, contrast, and visual screenshot audit

| ID | Audit item | Measured evidence | Verdict |
|---|---|---|---|
| `AS-01` | UTF-8 (no BOM), POSIX LF (`\n`), NFC normalization | Independent Python binary scan of 33 text files (`index.html`, `DESIGN.md`, `PLAN_DETAIL.md`, `assets/icons/sprite.svg`, `assets/manifests/resources-verified.json`, `reports/QA_AUDIT_LOG.md`, `styles/*.css`, `scripts/*.js`, `blender/*.py`, `blender/diorama_pins.json`, `qa/*.py`, `qa/*.json`, `vendor/fonts/fonts.css`, `vendor/gsap.min.js`, `vendor/lucide.min.js`): `33/33` valid UTF-8, `0` BOM, `0` CRLF, `100%` NFC. | **PASS** |
| `AS-02` | Zero Unicode emojis and dingbats | Regex scan across non-minified text files (`U+1F300-1FAFF`, `U+2600-27BF`, `U+FE0F`, `U+200D`, `U+1F000-1F2FF`) returned `0` hits, matching `qa/playwright_audit_results.json:12` (`emoji_unicode_count: 0`). | **PASS** |
| `AS-03` | Zero `Inter` font and self-hosted font stack | `styles/tokens.css:33-36` defines `Bricolage Grotesque`, `Be Vietnam Pro`, `Fraunces`, and `Geist Mono`. `0` `Inter` uses in CSS/HTML (`DESIGN.md:30,56` only document the ban). `vendor/fonts/fonts.css` references `40` `.woff2` files; `40/40` exist on disk. | **PASS** |
| `AS-04` | Zero pure black (`#000000`) and `#F6F4EE` palette | `0` pure black hex/rgb uses in app code (`DESIGN.md:9,57` and `qa/qa_playwright_capture.py:115` only record the ban). `styles/tokens.css:3` sets `--bg-paper: #F6F4EE` and `styles/tokens.css:9` sets `--ink: #171C22`. | **PASS** |
| `AS-05` | WCAG AA contrast ratios | Computed relative-luminance ratios from `styles/tokens.css`: `--ink` on `--bg-paper` = `15.58:1`; `--ink` on `--bg-plate` = `17.13:1`; `--ink-slate` on `--bg-paper` = `6.70:1`; `#FFFFFF` on `--accent-pine` = `6.46:1`; `--accent-pine-dark` on `--accent-pine-soft` = `8.09:1`; `--accent-vermilion` on `--bg-plate` (`.cover-subtitle`) = `4.66:1`. All text token pairs exceed `4.5:1`. | **PASS** |
| `AS-06` | Anti-slop prose and layout structure (`unslop/SKILL.md`) | `0` em-dashes, `0` en-dashes, `0` curly quotes, and `0` banned AI vocabulary words in `index.html`, `DESIGN.md`, `PLAN_DETAIL.md`, `styles/*`, and `scripts/*`. Layouts use asymmetric two-column plates, a 5x2 specimen grid (Slide 4), a 2x3 + 3x2 + 2x2 chart (Slide 9), and a 5-column contribution table (Slide 10) with zero 3-card SaaS templates, neon gradients, or `backdrop-filter` glassmorphism. | **PASS** |
| `AS-07` | Offline `vendor/` and 48/48 SHA-256 manifest integrity | `0` external `http://` or `https://` runtime asset loads (only XML namespace `http://www.w3.org/2000/svg`). Independent Python hashing of `assets/manifests/resources-verified.json` matched `48/48` files on disk (`missing=0`, `mismatches=0`). | **PASS** |
| `AS-08` | SVG icon and sprite parity (`30/30` keys across `37` symbols) | All `30` distinct icon names referenced across `index.html`, `scripts/map-data.js`, and `scripts/deck.js` resolve in `scripts/icons.js` and `assets/icons/sprite.svg` (37 `<symbol>` definitions). | **PASS** |
| `AS-09` | QA JSON consistency | `qa/playwright_audit_results.json`, `qa/geometry_proof_results.json`, `qa/blender_asset_metrics.json`, and `qa/license_audit_results.json` all record `"status": "PASS"` and `"failure_count": 0` (`console_errors: 0`, `page_errors: 0`, `broken_images: 0`, `horizontal_overflow_count: 0`, `dock_overlap_count: 0`). | **PASS** |
| `AS-10` | Visual screenshot inspection (`qa/screenshots/`) | All 21 Playwright screenshots (`slide_01.png`..`slide_12.png` at `1440x900`, `1280x720/slide_04.png`, `1280x720/slide_10.png`, 5 interactive states, and 2 mobile `390x844` views; spot-checked directly on `slide_01.png` and `slide_06.png`) render crisp typography, clean alpha-masked Blender PNGs, accurate diorama pins, unobstructed SVG labels, and clean Vietnamese NFC diacritics. | **PASS** |

---

## Section 4: Consolidated defect and remediation register

### 4.1 Major defects (must fix before final submission)

| Defect ID | Severity | File and line(s) | Observed issue (verbatim) | Recommended fix | Verification check |
|---|---|---|---|---|---|
| `IPA-02` | **Major** | `scripts/map-data.js:164` and `scripts/map-data.js:310` | Line 164: `ipa: "/ˈbʊk.stɔːr/"`<br>Line 310: `ipa: "/nɪər/"` (rhotic trailing `r` conflicts with the deck's non-rhotic BrE IPA convention). | Line 164: change to `"/ˈbʊk.stɔː/"`.<br>Line 310: change to `"/nɪə/"`. | Inspect `scripts/map-data.js:164,310` and verify Slide 4 lightbox + Slide 9 vocabulary list show non-rhotic BrE forms. |
| `IPA-03` | **Major** | `scripts/map-data.js:479` | `ipa: "/ɒn jɔːr left / raɪt/"` (linking `/r/` is invalid before consonant `/l/` in BrE, and `/` splits the slash delimiters). | Change to `"/ɒn jɔː ˈleft/"` and `"/ɒn jɔː ˈraɪt/"` (for example `"/ɒn jɔː left \| raɪt/"` or separate `/ɒn jɔː ˈleft/ / /ɒn jɔː ˈraɪt/`). | Inspect `scripts/map-data.js:479` for valid BrE phonology and clean slash delimiters. |

### 4.2 Minor defects (recommended polish)

| Defect ID | Severity | File and line(s) | Observed issue (verbatim) | Recommended fix | Verification check |
|---|---|---|---|---|---|
| `EN-02` | **Minor** | `scripts/map-data.js:157, 174, 281, 292` | Line 157: `"A cozy family bistro..."`<br>Line 281: `"Centered at x = -9.2m..."`<br>Line 174: `"Corner timber-framed bookshop..."` (entry name at 163 is `"Bookstore"`)<br>Line 292: `"Maple Street sidewalk"` (mixed AmE spelling/lexis in a BrE deck). | Change `"cozy"` to `"cosy"` (line 157) and `"Centered"` to `"Centred"` (line 281). Optionally align `"bookshop"` to `"bookstore"` (line 174) and `"sidewalk"` to `"pavement"` (line 292). | Inspect `scripts/map-data.js:157,174,281,292` for BrE consistency. |
| `EN-03` | **Minor** | `index.html:331, 381`; `scripts/map-data.js:507, 527, 546` | `index.html:331`: `"on your right opposite Supermarket."`<br>`index.html:381`: `"North up Pine Street, turn right onto Oak Street past School. On your left."`<br>`map-data.js:507`: `"asked way to Hospital"`<br>`map-data.js:527`: `"asked way to the Park"`<br>`map-data.js:546`: `"Good morning teacher and classmates!"` | Add missing `"the"` (`"opposite the supermarket"`, `"and walk past the school"`, `"asked the way to the Hospital"`, `"asked the way to the Park"`), resolve the comma splice in `index.html:381` (`"Walk north up Pine Street, turn right onto Oak Street, and walk past the school. The park is on your left."`), and add a comma in `map-data.js:546` (`"Good morning, everyone!"` or `"Good morning, teacher and classmates!"`). | Inspect Slides 7, 8, 10, and Presenter Notes Slide 1 in rendered HTML and `scripts/map-data.js`. |
| `EN-04` | **Minor** | `scripts/map-data.js:460, 588` | `"Go straight ahead onto Oak Street, then turn right."` (Walking north on Pine Street, you walk **to** Oak Street first, then turn right **onto** Oak Street). | Change to `"Go straight ahead to Oak Street, then turn right."` (matching `steps[1]` at `scripts/map-data.js:447`). | Inspect Slide 8 dialogue card and Presenter Notes Slide 8. |
| `EN-05` (`D-R1`) | **Minor** | `scripts/map-data.js:518` vs `563` | Line 563 sets `presenterNotes[4].speakers` to `"Phước & Anh Thi"`, whereas line 518 sets Anh Thi's `speakingSlides` to `"Slides 5, 7, 9"` (omitting Slide 4). Also `index.html:217-220` shows `"Click any plate to inspect in 3D"` instead of speaker names. | Either update `scripts/map-data.js:518` to `"Slides 4, 5, 7, 9"` or set `presenterNotes[4].speakers` (line 563) to `"Phước"`. Optionally note speakers in Slide 4 chip. | Cross-check Slide 10 ledger row for Anh Thi against Slide 4 presenter notes. |
| `VI-03` | **Minor** | `scripts/map-data.js:559` | `"để lớp thấy hình 3D xoay góc và câu mô tả."` (Slide 3 shows static Blender PNG renders, not a rotatable 3D viewport). | Change `"hình 3D xoay góc"` to `"hình 3D và câu mô tả"` (or `"vị trí trên mô hình 3D và câu mô tả"`). | Inspect Slide 3 Vietnamese tip in Presenter Notes popover. |

### 4.3 Informational and rubric-wording notes (no remediation required)

| Note ID | Category | File and line(s) | Observation | Impact / optional action |
|---|---|---|---|---|
| `D-R2` | Rubric title wording | `index.html:57-58` | Printed Slide 1 subtitle reads `"Let's Find the Way! (Greenleaf Neighbourhood)"`, omitting `"Map"` from the teacher sample title (`MY NEIGHBOURHOOD MAP`), though spoken in `scripts/map-data.js:546`. | Optional: add `"Map"` to `index.html:58` if exact printed parity is desired. |
| `D-R3` | Deadline time & Slide 9 chip | `index.html:455`, `scripts/map-data.js:475-480` | Slide 10 tag shows `"Submission Deadline: 29/11/2026"` without `"before 24:00 Sunday"` (`PLAN_DETAIL.md:5`). Slide 9 `directionsVocab` lists 4 chips and omits a dedicated chip for `"take the first / second turning..."` (taught on Slides 6 and 7). | Informational only; Slide 7 teaches `"take the second turning on the left"` in full. |
| `D-R4` | Timing cue & unused fields | `scripts/map-data.js:255-316, 542-615` | Total spoken script is ~405 English words (~3.5 to 5 min live), matching the teacher's 3 to 5 minute guideline, though no minute target is printed in `presenterNotes`. Also `prepositions[*].qaTab` and `qaAnswer` (`255-316`) are unused by `scripts/deck.js`. | Optional: add a 3 to 5 minute pacing hint in Presenter Notes. |
| `IPA-01` (note) | Optional stress marks | `scripts/map-data.js:79, 250, 286, 477, 478` | Multi-word phrases `/maɪ haʊs/`, `/nekst tuː/`, `/ɪn frʌnt əv/`, `/tɜːn left/`, `/tɜːn raɪt/` lack primary stress marks (`ˈ`). | Optional polish: `/maɪ ˈhaʊs/`, `/ˈnekst tuː/`, `/ɪn ˈfrʌnt əv/`, `/tɜːn ˈleft/`, `/tɜːn ˈraɪt/`. |
| `SP-05` (note) | Curbside bus-bay geometry | `scripts/map-data.js:183-185`, `qa/geometry_proof_results.json:56` | `bus-stop` (`y in [-4.85, -3.75]`) extends `0.15 m` south of the `-4.70` curb edge as a curbside bus bay while remaining `1.15 m` clear of the Maple Street centerline (`y = -6.0`). | Matches `assets/blender/overview-diorama.png` visually; no change needed. |

---

## Section 5: Independent verification commands and scope declaration

### 5.1 Read-only verification commands

Run from `c:\Users\LENOVO\Desktop\test 4 agron\my-neighbourhood-slides\`:

1. Verify offline licenses, 48/48 SHA-256 manifest hashes, 37 sprite symbols, 40 `.woff2` fonts, 0 BOM, and 0 CRLF:
   ```powershell
   python qa/verify_licenses.py
   ```
2. Verify 10-landmark / 4-street geometry parity, 45 AABB clearances, 6 prepositions, and 3 route cross-products:
   ```powershell
   python qa/verify_geometry.py
   ```
3. Verify all 11 Blender PNG dimensions, alpha margins, and brightness metrics:
   ```powershell
   python qa/verify_blender_assets.py
   ```
4. Verify UTF-8 (no BOM), POSIX LF, and NFC normalization across all 33 workspace text files:
   ```powershell
   python -c "import pathlib, unicodedata; root = pathlib.Path('.'); files = [root/'index.html', root/'DESIGN.md', root/'PLAN_DETAIL.md', root/'assets/icons/sprite.svg', root/'assets/manifests/resources-verified.json', root/'reports/QA_AUDIT_LOG.md', *sorted((root/'styles').glob('*.css')), *sorted((root/'scripts').glob('*.js')), *sorted((root/'blender').glob('*.py')), root/'blender/diorama_pins.json', *sorted((root/'qa').glob('*.py')), *sorted((root/'qa').glob('*.json')), root/'vendor/fonts/fonts.css', root/'vendor/gsap.min.js', root/'vendor/lucide.min.js']; bad = [(f.name, f.read_bytes().startswith(b'\xef\xbb\xbf'), f.read_bytes().count(b'\r\n'), unicodedata.normalize('NFC', f.read_text('utf-8')) == f.read_text('utf-8')) for f in files]; print('checked:', len(files), 'issues:', [x for x in bad if x[1] or x[2] or not x[3]])"
   ```

### 5.2 Scope declaration

This audit was executed strictly read-only on all project source, style, script, Blender, asset, QA, and documentation files (`index.html`, `styles/`, `scripts/`, `blender/`, `assets/`, `qa/`, `vendor/`, `DESIGN.md`, `PLAN_DETAIL.md`, and `reports/QA_AUDIT_LOG.md`). Zero source files were modified; only `reports/TEAMWORK_RUBRIC_AUDIT.md` was created by this report pass.
