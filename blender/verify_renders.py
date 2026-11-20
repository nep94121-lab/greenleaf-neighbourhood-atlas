"""Deterministic verification for Greenleaf Neighbourhood Blender PNG outputs and scripts."""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

BLENDER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BLENDER_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "assets" / "blender"

EXPECTED_LANDMARKS = [
    "my-house",
    "school",
    "park",
    "post-office",
    "restaurant",
    "bookstore",
    "bus-stop",
    "market",
    "supermarket",
    "hospital",
]


def check_text_encoding():
    """Assert all Python files under blender/ are UTF-8 (no BOM) with 0 CRLF."""
    issues = []
    for p in sorted(BLENDER_DIR.glob("*.py")):
        raw = p.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            issues.append(f"{p.name}: contains UTF-8 BOM")
        if b"\r\n" in raw:
            issues.append(f"{p.name}: contains CRLF")
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            issues.append(f"{p.name}: invalid UTF-8 ({exc})")
    return issues


def inspect_png(path, expected_w, expected_h, expect_transparent):
    """Validate image dimensions, alpha bounds, zero border clipping, and contrast."""
    if not path.exists():
        return {"ok": False, "error": "missing"}
    if path.stat().st_size < 4096:
        return {"ok": False, "error": f"file too small ({path.stat().st_size} bytes)"}

    img = Image.open(path)
    w, h = img.size
    if (w, h) != (expected_w, expected_h):
        return {"ok": False, "error": f"wrong size {w}x{h}, expected {expected_w}x{expected_h}"}

    arr = np.asarray(img.convert("RGBA"))
    rgb = arr[:, :, :3].astype(np.float32)
    alpha = arr[:, :, 3]

    lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]

    if expect_transparent:
        mask = alpha > 16
        coverage = float(mask.mean())
        if coverage < 0.08 or coverage > 0.85:
            return {"ok": False, "error": f"bad alpha coverage {coverage:.3f}"}

        ys, xs = np.where(mask)
        min_x, max_x = int(xs.min()), int(xs.max())
        min_y, max_y = int(ys.min()), int(ys.max())
        # Zero border clipping check on outer 2px rim.
        border_clip = int(
            (alpha[:2, :] > 20).sum()
            + (alpha[-2:, :] > 20).sum()
            + (alpha[:, :2] > 20).sum()
            + (alpha[:, -2:] > 20).sum()
        )
        if border_clip > 0:
            return {"ok": False, "error": f"border clipping: {border_clip} opaque border pixels"}

        fg_lum = lum[mask]
        mean_l, std_l = float(fg_lum.mean()), float(fg_lum.std())
        if mean_l < 35.0 or mean_l > 235.0 or std_l < 18.0:
            return {"ok": False, "error": f"poor tonal contrast mean={mean_l:.1f}, std={std_l:.1f}"}

        return {
            "ok": True,
            "size": f"{w}x{h}",
            "bytes": path.stat().st_size,
            "coverage": round(coverage, 3),
            "bbox": [min_x, min_y, max_x, max_y],
            "mean_lum": round(mean_l, 1),
            "std_lum": round(std_l, 1),
        }
    else:
        mean_l, std_l = float(lum.mean()), float(lum.std())
        if mean_l < 35.0 or mean_l > 235.0 or std_l < 20.0:
            return {"ok": False, "error": f"poor overview contrast mean={mean_l:.1f}, std={std_l:.1f}"}
        return {
            "ok": True,
            "size": f"{w}x{h}",
            "bytes": path.stat().st_size,
            "mean_lum": round(mean_l, 1),
            "std_lum": round(std_l, 1),
        }


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    enc_issues = check_text_encoding()
    if enc_issues:
        print("ENCODING ERRORS:", enc_issues)
        sys.exit(1)

    targets = [only] if only else EXPECTED_LANDMARKS + ["overview-diorama"]
    results = {}
    failed = []
    for name in targets:
        is_overview = name == "overview-diorama"
        w, h = (1920, 1080) if is_overview else (1024, 1024)
        res = inspect_png(OUTPUT_DIR / f"{name}.png", w, h, expect_transparent=not is_overview)
        results[name] = res
        if not res["ok"]:
            failed.append((name, res["error"]))

    print(json.dumps(results, indent=2))
    if failed:
        print("FAILED:", failed)
        sys.exit(1)
    print(f"ALL {len(targets)} RENDERS VERIFIED OK (UTF-8 no BOM, 0 CRLF).")


if __name__ == "__main__":
    main()
