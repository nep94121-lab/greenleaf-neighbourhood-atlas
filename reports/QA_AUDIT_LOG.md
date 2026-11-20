# QA audit log for Greenleaf Neighbourhood

## Goal

Prove that the 12-slide presentation and 11 Blender 5.2 renders for "My Neighbourhood: Let's Find the Way!" have valid street and route math, verified offline licenses, clean 3D geometry, and zero live browser, visual, or typography defects.

## Stage A. Mathematical and route geometry proof

- Script: `qa/verify_geometry.py`
- Output artifact: `qa/geometry_proof_results.json`
- Status: PASS (0 failures across Round 1 and Round 2)
- Cross-source parity: `scripts/map-data.js` and `blender/spec.py` match the canonical specification across all 4 streets and 10 landmarks within 1e-6 meters.
- Building-to-building AABB clearance: all 45 landmark pairs exceed the 0.40m threshold. Minimum clearance is 0.50m between `post-office` and `restaurant`, and 0.50m between `restaurant` and `bookstore`.
- Street corridor clearance: all 9 buildings have 0.00m overlap with all 4 street corridors (`Oak Street`, `Maple Street`, `Pine Street`, `River Road`). The sidewalk transit shelter `bus-stop` sits on the north sidewalk of `Maple Street` at `(-5.6, -4.3)` (`1.15m` clear of the `y = -6.0m` road centerline).
- Spatial prepositions verified:
  - `next to` (`school`, `park`): 0.80m gap on the same north block of Oak Street, zero intervening landmarks.
  - `opposite` (`hospital`, `supermarket`): separated by `River Road` (`x` in `[10.2, 13.8]`), anti-parallel facings (`dot = -1.0`), 4.60m Y-axis overlap.
  - `between` (`restaurant` flanked by `post-office` and `bookstore`): collinear (`cross = 0.0`), 0.50m west gap and 0.50m east gap on the same block.
  - `in front of` (`bus-stop` relative to `bookstore`): forward projection `+2.80m`, lateral offset `0.00m`, 0.75m clearance.
  - `behind` (`bookstore` relative to `bus-stop`): forward projection `-2.80m`, lateral offset `0.00m`, 0.75m clearance.
  - `near` (`my-house`, `school`): same Oak Street north frontage, 7.60m edge-to-edge distance (`11.70m` center distance vs `14.80m` neighbourhood median).
- Direction routes verified by 2D vector cross-products and English text matching:
  - `route-market` (Slide 6): East on Maple Street to 1st cross street (`Pine Street`, ordinal 1), turn LEFT (`cross_z = +1.0`), arrive at `(-2.0, 0.0)` with `market` (`+2.5, 0.0`) ON YOUR RIGHT (`cross_z = -4.5`).
  - `route-hospital` (Slide 7): East on Maple Street past `Pine Street` to 2nd cross street (`River Road`, ordinal 2), turn LEFT (`cross_z = +1.0`), arrive at `(+12.0, 0.0)` with `hospital` (`+16.2, 0.0`) ON YOUR RIGHT (`cross_z = -4.2`).
  - `route-park` (Slide 8): North on Pine Street to `Oak Street` (ordinal 1), turn RIGHT (`cross_z = -1.0`), pass `school` (`x = +2.2`), arrive at `(+7.5, +6.0)` with `park` (`+7.5, +10.5`) ON YOUR LEFT (`cross_z = +4.5`).

## Stage B. Resource and license audit

- Script: `qa/verify_licenses.py`
- Output artifact: `qa/license_audit_results.json`
- Status: PASS (0 failures across 48 manifest entries)
- Verified local files: 48/48 exist on disk, non-empty, with exact byte-for-byte SHA-256 hash match against `assets/manifests/resources-verified.json`.
- Offline bundles verified: `vendor/gsap.min.js` (`Webflow-GSAP`), `vendor/lucide.min.js` (`ISC / MIT`), `assets/icons/sprite.svg` (37 valid XML `<symbol>` icons), `vendor/fonts/fonts.css` + 40 `.woff2` files covering `Bricolage Grotesque`, `Be Vietnam Pro`, `Fraunces`, and `Geist Mono` (`OFL-1.1`), plus Poly Haven 1K HDRI and 3 ambientCG 1K PBR packs (`CC0-1.0`).
- Verbatim license quotes: 48/48 non-empty and within the 20-word ceiling. Zero BOM and zero CRLF across manifest, sprite, and font stylesheet.

## Stage C. Human-eye 3D render audit

- Script: `qa/verify_blender_assets.py` + direct `read_file` visual inspection of all 11 PNGs in `assets/blender/`
- Output artifact: `qa/blender_asset_metrics.json`
- Status: PASS (11/11 verified, 0 visual or alpha defects)
- Pre-final preview catch: early `my-house.png` preview showed black coplanar Z-fighting on 2 front fence pickets; `@blender-studio` resolved the geometry before final batch delivery.
- Final 10 isolated landmarks (`1024x1024` RGBA, 0 border clipping): `my-house.png`, `school.png`, `park.png`, `post-office.png`, `restaurant.png`, `bookstore.png`, `bus-stop.png`, `market.png`, `supermarket.png`, `hospital.png` all show grounded 3D micro-joinery, clean plinths, warm readable shadows, and zero floating parts or clipping.
- Final overview diorama (`1920x1080` RGB): `overview-diorama.png` places all 10 landmarks at exact Single-Source-of-Truth coordinates and street facings across the 4-street grid with crosswalks, raised brick sidewalks, streetlamps, and perimeter trees.

## Stage D. Playwright multi-viewport and interactive visual audit

### Round 1 (2026-11-20 16:40)

- Programmatic assertions: PASS (`console_errors=0`, `page_errors=0`, `failed_network_requests=0`, `broken_images=0`, `emoji_unicode_count=0`, `crlf_count=0`, `bom_count=0`, `horizontal_overflow_count=0`, `dock_overlap_count=0`).
- Human-eye visual and prose defects reported in #20 and #21 to `@frontend-engineer`:
  - **D-1**: Slide 5 `highlightPreposition()` anchored dots/lines at building centers `(sx1, sy1)` over centered building names.
  - **D-2**: `Park #3` center decorative ring stroke overlapped `"Park"` and `"#3"` text.
  - **D-3**: `scripts/map-data.js:106` used `"features"` (`unslop` rule 8).
  - **D-4 (#21-1)**: `"Bus Stop"` label hugged the narrow `#7` parcel borders.
  - **D-5 (#21-2)**: Speaker chips and dialogue headers on Slides 2, 3, 5, 6, 7, 8, and 11 lacked NFC Vietnamese accents (`Phước`, `Yến Nhi`, `Tùng Lâm`, `Tuấn Anh`).

### Round 2 Re-Test (2026-11-20 16:52)

- Script: `qa/qa_playwright_capture.py` + human-eye `read_file` inspection of updated `1440x900`, `1280x720`, `390x844`, and interactive screenshots (`qa/screenshots/`)
- Output artifact: `qa/playwright_audit_results.json`
- Status: PASS (0 programmatic defects, 0 visual or prose defects)
- Closure verification:
  - **D-1 CLOSED**: Slide 5 exterior brackets (`next to` top bracket, `between` 3-prong top bracket, `opposite` street-edge connector, `in front of` / `behind` east-side stepped bracket, `near` gap connector) leave 100% of building names clear (`slide_05.png`, `interactive_slide05_preposition_active.png`, `interactive_slide05_preposition_opposite.png`, `interactive_slide05_preposition_infront.png`).
  - **D-2 CLOSED**: Park decorative ring moved to top-right corner; `"Park #3"` is unobstructed on Slides 3, 5, 6, 7, and 8.
  - **D-3 CLOSED**: `"features"` replaced with `"has"` in `scripts/map-data.js:106`; zero banned `unslop` words, zero em-dashes, zero emojis across project files and rendered DOM.
  - **D-4 CLOSED**: Compact `"Bus Stop"` typography fits cleanly with side margins inside `#7`.
  - **D-5 CLOSED**: Full NFC Vietnamese diacritics (`Phước`, `Yến Nhi`, `Tùng Lâm`, `Tuấn Anh`, `Ầ Ẫ Ở Ữ đ`) render cleanly without clipping across all 12 slides, dialogue headers, overview modal, and Presenter Notes popover.
- Final assertion summary:
  - `console_errors`: 0
  - `page_errors`: 0
  - `failed_network_requests`: 0
  - `broken_images`: 0
  - `emoji_unicode_count`: 0
  - `crlf_count`: 0
  - `bom_count`: 0
  - `horizontal_overflow_count` (`1440x900`, `1280x720`, `390x844`): 0
  - `dock_overlap_count` (`1440x900`, `1280x720`): 0

### Round 3 Re-Test After Rubric and Live Browser Remediation (#26 / #27, 2026-11-20 17:19)

- Re-ran `qa/verify_geometry.py` (PASS, 0 failures), `qa/verify_licenses.py` (PASS, 48/48 SHA-256 matched), `qa/verify_blender_assets.py` (PASS, 11/11), and `qa/qa_playwright_capture.py` (PASS, 0 failures) plus human-eye `read_file` inspection of updated `1440x900`, `1280x720`, `390x844`, and lightbox screenshots.
- Verified closure of all `reports/TEAMWORK_RUBRIC_AUDIT.md` and live `/browser` items:
  - **IPA-02, IPA-03, and IPA-01 CLOSED**: Non-rhotic British English IPA verified in `scripts/map-data.js` and rendered DOM (`/ˈbʊk.stɔː/`, `/nɪə/`, `/ɒn jɔː ˈleft/ | /ɒn jɔː ˈraɪt/`, `/maɪ ˈhaʊs/`, `/ˈnekst tuː/`, `/ɪn ˈfrʌnt əv/`, `/tɜːn ˈleft/`, `/tɜːn ˈraɪt/`).
  - **EN-02, EN-03, EN-04, EN-05/D-R1, and VI-03 CLOSED**: British English lexis (`cosy`, `Centred`, `bookstore`, `pavement`), grammar/articles (`opposite the supermarket.`, `Walk north up Pine Street, turn right onto Oak Street, and walk past the school. The park is on your left.`, `Go straight ahead to Oak Street, then turn right.`, `asked the way to the Hospital`, `asked the way to the Park`, `Good morning, teacher and classmates!`), Anh Thi `Slides 4, 5, 7, 9` on Slides 4, 10, and 12, and Slide 3 Vietnamese tip (`hình 3D và câu mô tả`) all verified.
  - **Live `/browser` `<dialog>` opacity CLOSED**: Immediate computed style on `showModal()` verified `opacity: "1"` and `backgroundColor: "rgb(255, 255, 255)"` with zero card bleed-through (`interactive_slide04_lightbox_open.png`).
  - **Encoding & NFC**: 100% UTF-8 (no BOM), POSIX LF (`0` CRLF), and NFC verified across all project files.
