import functools
import http.server
import json
import re
import socketserver
import threading
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

QA_DIR = Path(__file__).resolve().parent
PROJECT_DIR = QA_DIR.parent
SCREENSHOT_DIR = QA_DIR / "screenshots"
SCREENSHOT_1280_DIR = SCREENSHOT_DIR / "1280x720"
REPORT_JSON = QA_DIR / "playwright_audit_results.json"

TEXT_EXTENSIONS = {".html", ".css", ".js", ".mjs", ".json", ".svg", ".py", ".md"}

# Strict Unicode Emoji ranges (pictographs, dingbats, transport/map symbols, supplemental symbols, flags)
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\U0001F1E6-\U0001F1FF"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "\uFE0F"
    "]"
)

SLOP_WORDS_RE = re.compile(
    r"\b(delve|delves|delving|tapestry|testament|underscore|underscores|underscoring|"
    r"pivotal|vibrant|fostering|intricate|interplay|garner|enduring|"
    r"serves as|stands as|boasts)\b",
    re.IGNORECASE,
)


class QuietThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    request_queue_size = 64


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        pass


def start_ephemeral_server(root_dir: Path) -> tuple[QuietThreadingHTTPServer, int, threading.Thread]:
    handler = functools.partial(QuietHandler, directory=str(root_dir))
    httpd = QuietThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, name="qa-http-server", daemon=True)
    thread.start()
    return httpd, port, thread


def launch_browser(pw):
    for channel in ("chrome", "msedge", None):
        try:
            if channel:
                return pw.chromium.launch(channel=channel, headless=True), channel
            return pw.chromium.launch(headless=True), "chromium"
        except Exception:
            continue
    raise RuntimeError("Unable to launch any headless Chromium/Chrome/Edge browser.")


def audit_project_files() -> dict:
    crlf_files = []
    bom_files = []
    emoji_hits = []
    slop_hits = []
    pure_black_hits = []
    bad_split_hits = []

    for path in sorted(PROJECT_DIR.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or ".git" in path.parts:
            continue
        ext = path.suffix.lower()
        if ext not in TEXT_EXTENSIONS:
            continue
        rel = str(path.relative_to(PROJECT_DIR)).replace("\\", "/")
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            bom_files.append(rel)
        if b"\r\n" in raw:
            crlf_files.append(rel)

        # Skip vendor minified bundles and QA regex scripts for prose/emoji checks
        if rel.startswith("vendor/") or rel.startswith("qa/") or rel.startswith("reports/") or rel.startswith("assets/cc0-sources/"):
            continue

        text = raw.decode("utf-8", errors="replace")
        for m in EMOJI_RE.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            emoji_hits.append(f"{rel}:{line_no} U+{ord(m.group(0)):04X}")

        if ext in {".html", ".js"}:
            for m in SLOP_WORDS_RE.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                slop_hits.append(f"{rel}:{line_no} '{m.group(0)}'")

        if ext == ".css":
            for m in re.finditer(r"#000000\b|#000\b", text, re.IGNORECASE):
                line_no = text.count("\n", 0, m.start()) + 1
                pure_black_hits.append(f"{rel}:{line_no} '{m.group(0)}'")

        if ext == ".js":
            for m in re.finditer(r"\.split\(\s*['\"]['\"]\s*\)", text):
                line_no = text.count("\n", 0, m.start()) + 1
                bad_split_hits.append(f"{rel}:{line_no} str.split('')")

    remediation_26_hits = []
    map_js_path = PROJECT_DIR / "scripts" / "map-data.js"
    if map_js_path.exists():
        mjs = map_js_path.read_text(encoding="utf-8")
        for forbidden_sub in (
            "/ˈbʊk.stɔːr/",
            "/nɪər/",
            "jɔːr left",
            "cozy",
            "Centered",
            "bookshop",
            "hình 3D xoay góc",
            "straight ahead onto Oak Street",
        ):
            if forbidden_sub in mjs:
                remediation_26_hits.append(f"scripts/map-data.js still contains '{forbidden_sub}'")
        if "Slides 4, 5, 7, 9" not in mjs:
            remediation_26_hits.append("scripts/map-data.js missing Anh Thi 'Slides 4, 5, 7, 9'")

    return {
        "crlf_count": len(crlf_files),
        "crlf_files": crlf_files,
        "bom_count": len(bom_files),
        "bom_files": bom_files,
        "emoji_file_count": len(emoji_hits),
        "emoji_file_hits": emoji_hits[:30],
        "slop_word_hits": slop_hits,
        "pure_black_css_hits": pure_black_hits,
        "bad_js_split_hits": bad_split_hits,
        "remediation_26_hits": remediation_26_hits,
    }


def inspect_slide_dom(page, slide_num: int, viewport_label: str) -> dict:
    return page.evaluate(
        """({ slideNum, viewportLabel }) => {
            const docEl = document.documentElement;
            const horizOverflowPx = Math.max(0, docEl.scrollWidth - window.innerWidth);
            const vertOverflowPx = Math.max(0, docEl.scrollHeight - window.innerHeight);

            const activeSlide = document.querySelector(`.slide[data-slide="${slideNum}"]`);
            const slideRect = activeSlide ? activeSlide.getBoundingClientRect() : null;

            // Broken images inside active slide or chrome
            const brokenImages = [];
            const allVisibleImgs = Array.from(document.querySelectorAll('img')).filter(img => {
                const sec = img.closest('.slide[hidden], [hidden], dialog:not([open]):not(:popover-open)');
                return !sec;
            });
            for (const img of allVisibleImgs) {
                if (!img.complete || img.naturalWidth === 0 || img.naturalHeight === 0) {
                    brokenImages.push(img.getAttribute('src') || img.id || 'unknown-img');
                }
            }

            // Unhydrated icon placeholders & zero-sized SVG icons
            const unhydratedIcons = document.querySelectorAll('[data-icon]').length;
            const brokenSvgIcons = [];
            const visibleSvgs = Array.from(document.querySelectorAll('svg.icon')).filter(svg => {
                const hiddenParent = svg.closest('.slide[hidden], [hidden], dialog:not([open]):not(:popover-open)');
                return !hiddenParent;
            });
            for (const svg of visibleSvgs) {
                const r = svg.getBoundingClientRect();
                if (r.width < 4 || r.height < 4) {
                    brokenSvgIcons.push(svg.outerHTML.slice(0, 80));
                }
            }

            // Check clipped text inside overflow:hidden containers on active slide
            const clippedElements = [];
            if (activeSlide) {
                const elems = activeSlide.querySelectorAll('h1, h2, h3, p, span, strong, td, th, button, blockquote');
                for (const el of elems) {
                    const st = window.getComputedStyle(el);
                    if (st.display === 'none' || st.visibility === 'hidden') continue;
                    if (st.overflowX === 'hidden' || st.textOverflow === 'ellipsis') {
                        if (el.scrollWidth > el.clientWidth + 2) {
                            clippedElements.push({
                                tag: el.tagName.toLowerCase(),
                                text: (el.textContent || '').trim().slice(0, 50),
                                scrollW: el.scrollWidth,
                                clientW: el.clientWidth
                            });
                        }
                    }
                }
            }

            // Check active slide fits vertically inside desktop viewport without footer collision
            const dock = document.querySelector('.deck-dock');
            const dockRect = dock ? dock.getBoundingClientRect() : null;
            let dockOverlapPx = 0;
            if (slideRect && dockRect && window.innerWidth >= 1024) {
                dockOverlapPx = Math.max(0, Math.round(slideRect.bottom - dockRect.top));
            }

            return {
                slide: slideNum,
                viewport: viewportLabel,
                horizOverflowPx,
                vertOverflowPx,
                dockOverlapPx,
                visibleImages: allVisibleImgs.length,
                brokenImages,
                unhydratedIcons,
                visibleSvgIcons: visibleSvgs.length,
                brokenSvgIcons,
                clippedElements
            };
        }""",
        {"slideNum": slide_num, "viewportLabel": viewport_label},
    )


def wait_slide_ready(page, slide_num: int) -> None:
    page.evaluate(
        """(n) => {
            if (window.__ATLAS_DECK && typeof window.__ATLAS_DECK.goToSlide === 'function') {
                window.__ATLAS_DECK.goToSlide(n, true);
            }
        }""",
        slide_num,
    )
    page.wait_for_selector(f'.slide[data-slide="{slide_num}"]:not([hidden])', timeout=5000)
    page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
    if slide_num in (6, 7, 8):
        # Allow GSAP 3-segment route tracer animation (~3.9s on Slide 7) to settle to completion
        time.sleep(4.3)
    else:
        time.sleep(0.25)


def main() -> int:
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOT_1280_DIR.mkdir(parents=True, exist_ok=True)

    file_audit = audit_project_files()
    console_errors: list[str] = []
    page_errors: list[str] = []
    failed_requests: list[str] = []
    slide_metrics_1440: list[dict] = []
    slide_metrics_1280: list[dict] = []
    mobile_metrics: list[dict] = []
    interactive_checks: dict = {}
    dom_emoji_hits: list[str] = []

    httpd, port, _ = start_ephemeral_server(PROJECT_DIR)
    base_url = f"http://127.0.0.1:{port}/index.html"

    try:
        with sync_playwright() as pw:
            browser, channel_used = launch_browser(pw)
            try:
                # --- PASS 1: 1440x900 Full 12 Slides + Interactive State Suite ---
                context = browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
                page = context.new_page()

                page.on(
                    "console",
                    lambda msg: console_errors.append(f"[console.{msg.type}] {msg.text}")
                    if msg.type == "error"
                    else None,
                )
                page.on("pageerror", lambda err: page_errors.append(str(err)))
                page.on(
                    "requestfailed",
                    lambda req: failed_requests.append(f"[FAILED] {req.method} {req.url} ({req.failure})"),
                )
                page.on(
                    "response",
                    lambda resp: failed_requests.append(f"[HTTP {resp.status}] {resp.url}")
                    if resp.status >= 400
                    else None,
                )

                page.goto(base_url, wait_until="networkidle", timeout=20000)
                page.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
                time.sleep(0.4)

                # Check all <img> across entire document (including hidden slides) load cleanly
                all_imgs_status = page.evaluate(
                    """async () => {
                        const imgs = Array.from(document.querySelectorAll('img'));
                        await Promise.all(imgs.map(img => {
                            if (img.complete) return Promise.resolve();
                            return new Promise(res => {
                                img.addEventListener('load', res, { once: true });
                                img.addEventListener('error', res, { once: true });
                            });
                        }));
                        return imgs.map(img => ({
                            src: img.getAttribute('src'),
                            complete: img.complete,
                            naturalWidth: img.naturalWidth,
                            naturalHeight: img.naturalHeight
                        }));
                    }"""
                )
                broken_global_imgs = [i["src"] for i in all_imgs_status if i["naturalWidth"] == 0]

                # Step through all 12 slides at 1440x900
                for s in range(1, 13):
                    wait_slide_ready(page, s)
                    metrics = inspect_slide_dom(page, s, "1440x900")
                    slide_metrics_1440.append(metrics)
                    out_png = SCREENSHOT_DIR / f"slide_{s:02d}.png"
                    page.screenshot(path=str(out_png), full_page=False)

                    txt = page.evaluate("() => document.body.innerText")
                    for m in EMOJI_RE.finditer(txt):
                        dom_emoji_hits.append(f"slide_{s:02d}: U+{ord(m.group(0)):04X}")

                # --- INTERACTIVE CHECKS AT 1440x900 ---
                # 1. Slide 3 Diorama mode + landmark pin click
                wait_slide_ready(page, 3)
                page.click("#mode-diorama-btn")
                time.sleep(0.25)
                page.click('#diorama-pin-layer [data-atlas-pin="hospital"]')
                time.sleep(0.25)
                insp_title = page.text_content("#atlas-inspector-name") or ""
                diorama_visible = page.is_visible("#atlas-diorama-container")
                pin_positions = page.evaluate(
                    """() => {
                        const wrap = document.getElementById('atlas-diorama-container').getBoundingClientRect();
                        return Array.from(document.querySelectorAll('#diorama-pin-layer .diorama-pin')).map(b => {
                            const r = b.getBoundingClientRect();
                            return {
                                id: b.getAttribute('data-atlas-pin'),
                                text: b.textContent.trim(),
                                centerPctX: Math.round(((r.left + r.width / 2 - wrap.left) / wrap.width) * 1000) / 10,
                                centerPctY: Math.round(((r.top + r.height / 2 - wrap.top) / wrap.height) * 1000) / 10
                            };
                        });
                    }"""
                )
                page.screenshot(path=str(SCREENSHOT_DIR / "interactive_slide03_diorama_popup.png"))
                page.click("#mode-svg-btn")
                interactive_checks["slide3_diorama"] = {
                    "diorama_visible": diorama_visible,
                    "inspector_title_after_click": insp_title.strip(),
                    "passed": diorama_visible and "Hospital" in insp_title,
                    "pins": pin_positions,
                }

                # 2. Slide 4 native <dialog closedby="any"> lightbox open + immediate opacity check + close
                wait_slide_ready(page, 4)
                slide4_header_text = (page.text_content('.slide[data-slide="4"] .slide-header') or "").strip()
                cards = page.locator("#places-specimen-grid .specimen-card")
                card_count = cards.count()
                cards.nth(5).click()  # #6 Bookstore (also verifies BrE IPA /ˈbʊk.stɔː/)
                immediate_dialog_style = page.evaluate(
                    """() => {
                        const dlg = document.getElementById('place-lightbox');
                        const st = window.getComputedStyle(dlg);
                        return { open: dlg.open, opacity: st.opacity, bg: st.backgroundColor };
                    }"""
                )
                time.sleep(0.35)
                lb_open = page.evaluate("() => document.getElementById('place-lightbox').open === true")
                lb_title = (page.text_content("#lightbox-title") or "").strip()
                lb_ipa = (page.text_content("#lightbox-ipa") or "").strip()
                page.screenshot(path=str(SCREENSHOT_DIR / "interactive_slide04_lightbox_open.png"))
                page.click("#lightbox-close-btn")
                time.sleep(0.35)
                lb_closed = page.evaluate("() => document.getElementById('place-lightbox').open === false")
                interactive_checks["slide4_lightbox"] = {
                    "specimen_card_count": card_count,
                    "slide4_header_speakers": "Phước" in slide4_header_text and "Anh Thi" in slide4_header_text,
                    "immediate_opacity": immediate_dialog_style["opacity"],
                    "immediate_bg": immediate_dialog_style["bg"],
                    "opened": lb_open,
                    "title": lb_title,
                    "ipa": lb_ipa,
                    "closed_cleanly": lb_closed,
                    "passed": (
                        card_count == 10
                        and lb_open
                        and lb_closed
                        and "Bookstore" in lb_title
                        and lb_ipa == "/ˈbʊk.stɔː/"
                        and float(immediate_dialog_style["opacity"]) >= 0.99
                        and immediate_dialog_style["bg"] == "rgb(255, 255, 255)"
                        and "Phước" in slide4_header_text
                        and "Anh Thi" in slide4_header_text
                    ),
                }

                # 3. Slide 5 preposition highlight + Q&A tabs (capture all key orientations)
                wait_slide_ready(page, 5)
                page.click('#prep-pill-grid [data-prep-id="opposite"]')
                time.sleep(0.2)
                page.screenshot(path=str(SCREENSHOT_DIR / "interactive_slide05_preposition_opposite.png"))
                page.click('#prep-pill-grid [data-prep-id="in-front-of"]')
                time.sleep(0.2)
                page.screenshot(path=str(SCREENSHOT_DIR / "interactive_slide05_preposition_infront.png"))
                page.click('#prep-pill-grid [data-prep-id="between"]')
                page.click('#qa-tab-row [data-qa-id="qa-near-far"]')
                time.sleep(0.25)
                prep_sent = (page.text_content("#prep-sentence-text") or "").strip()
                selected_svg_nodes = page.evaluate(
                    "() => Array.from(document.querySelectorAll('#prep-svg-container .atlas-building.is-selected')).map(n => n.getAttribute('data-place-id'))"
                )
                page.screenshot(path=str(SCREENSHOT_DIR / "interactive_slide05_preposition_active.png"))
                interactive_checks["slide5_prepositions"] = {
                    "sentence": prep_sent,
                    "selected_svg_nodes": selected_svg_nodes,
                    "passed": set(selected_svg_nodes) == {"restaurant", "post-office", "bookstore"},
                }

                # 4. Slide 6/7/8 animated route paused + WCAG button check + Next Step
                wait_slide_ready(page, 6)
                wcag_no_aria_pressed = page.evaluate(
                    "() => !document.getElementById('route-play-6').hasAttribute('aria-pressed')"
                )
                page.click("#route-replay-6")
                time.sleep(0.55)
                label_while_playing = (page.text_content("#route-play-6 .route-play-label") or "").strip()
                page.click("#route-play-6")  # Pause mid-route
                time.sleep(0.15)
                label_when_paused = (page.text_content("#route-play-6 .route-play-label") or "").strip()
                page.screenshot(path=str(SCREENSHOT_DIR / "interactive_slide06_route_paused.png"))
                page.click("#route-next-step-6")
                time.sleep(0.45)
                interactive_checks["slide6_route_controls"] = {
                    "wcag_no_aria_pressed": wcag_no_aria_pressed,
                    "label_while_playing": label_while_playing,
                    "label_when_paused": label_when_paused,
                    "passed": wcag_no_aria_pressed
                    and label_while_playing == "Pause route"
                    and label_when_paused == "Play route",
                }

                # 5. Presenter Notes popover drawer open (check Vietnamese diacritics on Slide 5/8)
                wait_slide_ready(page, 8)
                page.click("#notes-toggle-btn")
                time.sleep(0.3)
                notes_open = page.evaluate(
                    """() => {
                        const d = document.getElementById('presenter-notes');
                        return d.matches(':popover-open') || d.classList.contains(':popover-open');
                    }"""
                )
                notes_vi = (page.text_content("#notes-vietnamese-tips") or "").strip()
                page.screenshot(path=str(SCREENSHOT_DIR / "interactive_presenter_notes_open.png"))
                page.click("#notes-close-btn")
                time.sleep(0.25)
                notes_closed = page.evaluate(
                    """() => {
                        const d = document.getElementById('presenter-notes');
                        return !(d.matches(':popover-open') || d.classList.contains(':popover-open'));
                    }"""
                )
                interactive_checks["presenter_notes_popover"] = {
                    "opened": notes_open,
                    "vi_sample": notes_vi,
                    "closed_cleanly": notes_closed,
                    "passed": notes_open and notes_closed and len(notes_vi) > 20,
                }

                # 6. Global Slide Overview Grid modal + Slide 12 Jump to Map button
                page.click("#slide-grid-btn")
                time.sleep(0.3)
                overview_open = page.evaluate("() => document.getElementById('slide-overview-dialog').open === true")
                page.screenshot(path=str(SCREENSHOT_DIR / "interactive_slide_overview_modal.png"))
                page.click('#overview-grid [data-overview-slide="12"]')
                time.sleep(0.45)
                on_slide_12 = page.evaluate("() => window.__ATLAS_DECK.getCurrentSlide() === 12")
                page.click("#jump-to-map-btn")
                time.sleep(0.45)
                jumped_to_3 = page.evaluate("() => window.__ATLAS_DECK.getCurrentSlide() === 3")
                interactive_checks["overview_and_qna_jump"] = {
                    "overview_opened": overview_open,
                    "jumped_to_12": on_slide_12,
                    "qna_jumped_to_3": jumped_to_3,
                    "passed": overview_open and on_slide_12 and jumped_to_3,
                }
                context.close()

                # --- PASS 2: 1280x720 Full 12-Slide Audit ---
                ctx_1280 = browser.new_context(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
                p1280 = ctx_1280.new_page()
                p1280.goto(base_url, wait_until="networkidle", timeout=20000)
                p1280.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
                for s in range(1, 13):
                    wait_slide_ready(p1280, s)
                    m1280 = inspect_slide_dom(p1280, s, "1280x720")
                    slide_metrics_1280.append(m1280)
                    p1280.screenshot(path=str(SCREENSHOT_1280_DIR / f"slide_{s:02d}.png"))
                ctx_1280.close()

                # --- PASS 3: Mobile 390x844 Check on Slide 3 & Slide 4 ---
                ctx_mob = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
                pmob = ctx_mob.new_page()
                pmob.goto(base_url, wait_until="networkidle", timeout=20000)
                pmob.evaluate("() => document.fonts ? document.fonts.ready : Promise.resolve()")
                for s in (3, 4):
                    wait_slide_ready(pmob, s)
                    mmob = inspect_slide_dom(pmob, s, "390x844")
                    mobile_metrics.append(mmob)
                    pmob.screenshot(path=str(SCREENSHOT_DIR / f"mobile_390x844_slide_{s:02d}.png"), full_page=False)
                ctx_mob.close()
            finally:
                browser.close()
    finally:
        httpd.shutdown()
        httpd.server_close()

    # Aggregate all programmatic assertions
    failures: list[str] = []
    if console_errors:
        failures.append(f"console_errors={len(console_errors)}: {console_errors[:5]}")
    if page_errors:
        failures.append(f"page_errors={len(page_errors)}: {page_errors[:5]}")
    if failed_requests:
        failures.append(f"failed_network_requests={len(failed_requests)}: {failed_requests[:10]}")
    if broken_global_imgs:
        failures.append(f"broken_images={len(broken_global_imgs)}: {broken_global_imgs}")
    if file_audit["crlf_count"] > 0:
        failures.append(f"crlf_files={file_audit['crlf_count']}: {file_audit['crlf_files']}")
    if file_audit["bom_count"] > 0:
        failures.append(f"bom_files={file_audit['bom_count']}: {file_audit['bom_files']}")
    if file_audit["emoji_file_count"] > 0 or dom_emoji_hits:
        failures.append(
            f"emoji_violations: files={file_audit['emoji_file_hits'][:10]}, dom={dom_emoji_hits[:10]}"
        )
    if file_audit["slop_word_hits"]:
        failures.append(f"slop_word_hits: {file_audit['slop_word_hits']}")
    if file_audit["pure_black_css_hits"]:
        failures.append(f"pure_black_css_hits: {file_audit['pure_black_css_hits']}")
    if file_audit["bad_js_split_hits"]:
        failures.append(f"bad_js_split_hits: {file_audit['bad_js_split_hits']}")
    if file_audit.get("remediation_26_hits"):
        failures.append(f"remediation_26_hits: {file_audit['remediation_26_hits']}")

    for m in slide_metrics_1440 + slide_metrics_1280 + mobile_metrics:
        if m["horizOverflowPx"] > 0:
            failures.append(f"{m['viewport']} slide {m['slide']}: horizontal overflow {m['horizOverflowPx']}px")
        if m["dockOverlapPx"] > 2:
            failures.append(
                f"{m['viewport']} slide {m['slide']}: slide content overlaps bottom dock by {m['dockOverlapPx']}px"
            )
        if m["brokenImages"]:
            failures.append(f"{m['viewport']} slide {m['slide']}: broken images {m['brokenImages']}")
        if m["unhydratedIcons"] > 0 or m["brokenSvgIcons"]:
            failures.append(
                f"{m['viewport']} slide {m['slide']}: icon issue (unhydrated={m['unhydratedIcons']}, broken={len(m['brokenSvgIcons'])})"
            )
        if m["clippedElements"]:
            failures.append(f"{m['viewport']} slide {m['slide']}: clipped text {m['clippedElements']}")

    for check_name, check_res in interactive_checks.items():
        if not check_res.get("passed"):
            failures.append(f"Interactive check '{check_name}' failed: {check_res}")

    report = {
        "stage": "Stage D - Playwright Multi-Viewport & Interactive Audit",
        "browser_channel": channel_used,
        "status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
        "assertions": {
            "console_errors": len(console_errors),
            "page_errors": len(page_errors),
            "failed_network_requests": len(failed_requests),
            "broken_images": len(broken_global_imgs),
            "emoji_unicode_count": file_audit["emoji_file_count"] + len(dom_emoji_hits),
            "crlf_count": file_audit["crlf_count"],
            "bom_count": file_audit["bom_count"],
            "horizontal_overflow_count": sum(
                1 for m in (slide_metrics_1440 + slide_metrics_1280 + mobile_metrics) if m["horizOverflowPx"] > 0
            ),
            "dock_overlap_count": sum(
                1 for m in (slide_metrics_1440 + slide_metrics_1280) if m["dockOverlapPx"] > 2
            ),
        },
        "file_audit": file_audit,
        "interactive_checks": interactive_checks,
        "metrics_1440x900": slide_metrics_1440,
        "metrics_1280x720": slide_metrics_1280,
        "metrics_mobile_390x844": mobile_metrics,
    }
    REPORT_JSON.write_bytes((json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

    print(f"[Stage D] Status: {report['status']} (failures={len(failures)}, browser={channel_used})")
    print(f"  - Assertions: {json.dumps(report['assertions'])}")
    if failures:
        for f in failures:
            print(f"  [DEFECT] {f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
