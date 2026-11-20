import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

QA_DIR = Path(__file__).resolve().parent
PROJECT_DIR = QA_DIR.parent
MANIFEST_PATH = PROJECT_DIR / "assets" / "manifests" / "resources-verified.json"
SPRITE_PATH = PROJECT_DIR / "assets" / "icons" / "sprite.svg"
FONTS_CSS_PATH = PROJECT_DIR / "vendor" / "fonts" / "fonts.css"
REPORT_JSON = QA_DIR / "license_audit_results.json"

REQUIRED_FIELDS = {
    "name",
    "category",
    "url",
    "http_status",
    "license",
    "license_url",
    "license_quote",
    "local_path",
    "sha256",
}

ALLOWED_LICENSE_PATTERNS = [
    r"\bcc0\b",
    r"\bpublic\s+domain\b",
    r"\bmit\b",
    r"\bisc\b",
    r"\bofl\b",
    r"\bsil\s+open\s+font\b",
    r"\bgsap\b",
    r"\bwebflow\b",
    r"\bgreensock\b",
    r"\bapache[- ]2\.0\b",
    r"\bbsd\b",
]

FORBIDDEN_LICENSE_PATTERNS = [
    r"by-nc",
    r"non-commercial",
    r"noncommercial",
    r"personal\s+use\s+only",
    r"envato",
    r"shutterstock",
]

REQUIRED_LOCAL_FILES = [
    "vendor/gsap.min.js",
    "vendor/lucide.min.js",
    "assets/icons/sprite.svg",
    "vendor/fonts/fonts.css",
]

REQUIRED_FONT_FAMILIES = [
    "Bricolage Grotesque",
    "Be Vietnam Pro",
    "Fraunces",
    "Geist Mono",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def word_count(text: str) -> int:
    tokens = [w for w in re.split(r"\s+", text.strip()) if w]
    return len(tokens)


def license_is_allowed(lic: str) -> bool:
    low = lic.lower()
    if any(re.search(pat, low) for pat in FORBIDDEN_LICENSE_PATTERNS):
        return False
    return any(re.search(pat, low) for pat in ALLOWED_LICENSE_PATTERNS)


def check_text_encoding(path: Path, failures: list[str]) -> None:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        failures.append(f"UTF-8 BOM found in {path.relative_to(PROJECT_DIR)}")
    if b"\r\n" in raw:
        failures.append(f"CRLF line endings found in {path.relative_to(PROJECT_DIR)}")


def main() -> int:
    failures: list[str] = []
    if not MANIFEST_PATH.exists():
        print(f"[Stage B] Waiting/FAIL: Manifest missing at {MANIFEST_PATH}")
        return 2

    check_text_encoding(MANIFEST_PATH, failures)
    try:
        entries = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"[Stage B] FAIL: Invalid JSON in {MANIFEST_PATH}: {exc}")
        return 1

    if not isinstance(entries, list) or len(entries) == 0:
        failures.append("Manifest must be a non-empty JSON array of resource objects.")
        entries = []

    manifest_paths = set()
    verified_records = []

    for idx, item in enumerate(entries):
        label = item.get("name", f"entry[{idx}]") if isinstance(item, dict) else f"entry[{idx}]"
        if not isinstance(item, dict):
            failures.append(f"{label}: entry is not a JSON object")
            continue

        missing = REQUIRED_FIELDS - set(item.keys())
        if missing:
            failures.append(f"{label}: missing fields {sorted(missing)}")

        lic = str(item.get("license") or "").strip()
        quote = str(item.get("license_quote") or "").strip()
        local_rel = item.get("local_path")
        expected_sha = str(item.get("sha256") or "").strip().lower()
        http_status = item.get("http_status")

        # Allow documented unreachable optional CC0 3D texture/HDRI fallback ONLY if local_path is empty/null
        is_documented_fallback = (not local_rel) and (http_status in (None, 0, "unreachable", "fallback") or int(http_status or 0) >= 400)

        if not is_documented_fallback:
            if not license_is_allowed(lic):
                failures.append(f"{label}: disallowed or unrecognized license '{lic}'")

            wc = word_count(quote)
            if wc == 0:
                failures.append(f"{label}: empty license_quote")
            elif wc > 20:
                failures.append(f"{label}: license_quote exceeds 20 words ({wc} words): '{quote}'")
            elif quote.lower() in {"todo", "tbd", "n/a", "none", "unknown"}:
                failures.append(f"{label}: placeholder license_quote '{quote}'")

            if not local_rel:
                failures.append(f"{label}: missing local_path")
            else:
                norm_rel = str(local_rel).replace("\\", "/").lstrip("./")
                if norm_rel.startswith("my-neighbourhood-slides/"):
                    norm_rel = norm_rel[len("my-neighbourhood-slides/") :]
                manifest_paths.add(norm_rel)
                abs_path = (PROJECT_DIR / norm_rel).resolve()
                if not abs_path.exists():
                    failures.append(f"{label}: local file missing on disk: {norm_rel}")
                elif abs_path.stat().st_size == 0:
                    failures.append(f"{label}: local file is 0 bytes: {norm_rel}")
                else:
                    actual_sha = sha256_file(abs_path)
                    if actual_sha != expected_sha:
                        failures.append(
                            f"{label}: SHA-256 mismatch for {norm_rel} (manifest={expected_sha}, disk={actual_sha})"
                        )
                    verified_records.append(
                        {
                            "name": label,
                            "local_path": norm_rel,
                            "size_bytes": abs_path.stat().st_size,
                            "sha256_match": actual_sha == expected_sha,
                            "license": lic,
                            "quote_words": wc,
                        }
                    )

    for req_rel in REQUIRED_LOCAL_FILES:
        req_abs = PROJECT_DIR / req_rel
        if not req_abs.exists():
            failures.append(f"Required offline asset missing on disk: {req_rel}")
        elif req_rel not in manifest_paths:
            failures.append(f"Required offline asset not listed in resources-verified.json: {req_rel}")

    sprite_symbols = []
    if SPRITE_PATH.exists():
        check_text_encoding(SPRITE_PATH, failures)
        try:
            root = ET.fromstring(SPRITE_PATH.read_text(encoding="utf-8"))
            for elem in root.iter():
                if elem.tag.endswith("symbol") and elem.attrib.get("id"):
                    sprite_symbols.append(elem.attrib["id"])
            if len(sprite_symbols) < 20:
                failures.append(f"sprite.svg has too few <symbol> icons ({len(sprite_symbols)} found)")
        except Exception as exc:
            failures.append(f"sprite.svg XML parse error: {exc}")

    referenced_font_files = []
    if FONTS_CSS_PATH.exists():
        check_text_encoding(FONTS_CSS_PATH, failures)
        css_text = FONTS_CSS_PATH.read_text(encoding="utf-8")
        for fam in REQUIRED_FONT_FAMILIES:
            if fam.lower() not in css_text.lower():
                failures.append(f"fonts.css missing @font-face family '{fam}'")
        if "http://" in css_text or "https://" in css_text:
            failures.append("fonts.css contains remote http(s) URLs instead of 100% offline local font files")
        for m in re.finditer(r"url\(['\"]?([^'\")]+)['\"]?\)", css_text):
            url_val = m.group(1).split("?")[0].split("#")[0]
            if url_val.startswith("data:"):
                continue
            font_path = (FONTS_CSS_PATH.parent / url_val).resolve()
            referenced_font_files.append(str(font_path.relative_to(PROJECT_DIR)).replace("\\", "/"))
            if not font_path.exists() or font_path.stat().st_size == 0:
                failures.append(f"fonts.css references missing/empty font file: {url_val}")

    summary = {
        "stage": "Stage B - Resource & License Audit",
        "status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
        "manifest_entries": len(entries),
        "verified_local_files": len(verified_records),
        "sprite_symbol_count": len(sprite_symbols),
        "sprite_symbols": sprite_symbols,
        "referenced_font_files_count": len(referenced_font_files),
        "records": verified_records,
    }
    REPORT_JSON.write_bytes((json.dumps(summary, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

    print(f"[Stage B] Status: {summary['status']} (failures={len(failures)}, entries={len(entries)})")
    print(f"  - Verified local files: {len(verified_records)}, sprite symbols: {len(sprite_symbols)}, font files: {len(referenced_font_files)}")
    if failures:
        for f in failures:
            print(f"  [DEFECT] {f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
