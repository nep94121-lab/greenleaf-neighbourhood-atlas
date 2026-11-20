import json
from pathlib import Path
from PIL import Image, ImageStat

QA_DIR = Path(__file__).resolve().parent
PROJECT_DIR = QA_DIR.parent
BLENDER_ASSETS_DIR = PROJECT_DIR / "assets" / "blender"
REPORT_JSON = QA_DIR / "blender_asset_metrics.json"

ISOLATED_BUILDINGS = [
    "my-house.png",
    "school.png",
    "park.png",
    "post-office.png",
    "restaurant.png",
    "bookstore.png",
    "bus-stop.png",
    "market.png",
    "supermarket.png",
    "hospital.png",
]
OVERVIEW_FILE = "overview-diorama.png"


def main() -> int:
    failures: list[str] = []
    metrics: dict[str, dict] = {}

    for fname in ISOLATED_BUILDINGS:
        fpath = BLENDER_ASSETS_DIR / fname
        if not fpath.exists():
            failures.append(f"Missing isolated 3D render: {fname}")
            continue
        with Image.open(fpath) as im:
            w, h = im.size
            mode = im.mode
            if (w, h) != (1024, 1024):
                failures.append(f"{fname}: wrong resolution {w}x{h} (expected 1024x1024)")
            if mode != "RGBA":
                failures.append(f"{fname}: mode is {mode} (expected RGBA transparent)")
                rgba = im.convert("RGBA")
            else:
                rgba = im

            alpha = rgba.getchannel("A")
            # Threshold > 16 to ignore ultra-faint shadow-catcher fringe
            hard_alpha = alpha.point(lambda p: 255 if p > 24 else 0)
            bbox = hard_alpha.getbbox()
            if not bbox:
                failures.append(f"{fname}: completely transparent / empty render")
                continue

            left, top, right, bottom = bbox
            margin_px = min(left, top, w - right, h - bottom)
            if margin_px < 4:
                failures.append(
                    f"{fname}: clipped against 1024x1024 border (bbox={bbox}, min_margin={margin_px}px)"
                )

            rgb = rgba.convert("RGB")
            stat = ImageStat.Stat(rgb, mask=hard_alpha)
            luma_mean = 0.2126 * stat.mean[0] + 0.7152 * stat.mean[1] + 0.0722 * stat.mean[2]
            luma_std = 0.2126 * stat.stddev[0] + 0.7152 * stat.stddev[1] + 0.0722 * stat.stddev[2]
            if luma_mean < 45.0:
                failures.append(f"{fname}: render is too dark (mean_luma={luma_mean:.1f})")

            metrics[fname] = {
                "size": [w, h],
                "mode": mode,
                "alpha_bbox": list(bbox),
                "min_border_margin_px": margin_px,
                "fill_width_pct": round((right - left) / w * 100.0, 1),
                "fill_height_pct": round((bottom - top) / h * 100.0, 1),
                "mean_luma": round(luma_mean, 1),
                "luma_stddev": round(luma_std, 1),
                "bytes": fpath.stat().st_size,
            }

    ov_path = BLENDER_ASSETS_DIR / OVERVIEW_FILE
    if not ov_path.exists():
        failures.append(f"Missing overview diorama render: {OVERVIEW_FILE}")
    else:
        with Image.open(ov_path) as im:
            w, h = im.size
            if (w, h) != (1920, 1080):
                failures.append(f"{OVERVIEW_FILE}: wrong resolution {w}x{h} (expected 1920x1080)")
            rgb = im.convert("RGB")
            stat = ImageStat.Stat(rgb)
            luma_mean = 0.2126 * stat.mean[0] + 0.7152 * stat.mean[1] + 0.0722 * stat.mean[2]
            luma_std = 0.2126 * stat.stddev[0] + 0.7152 * stat.stddev[1] + 0.0722 * stat.stddev[2]
            if luma_mean < 45.0:
                failures.append(f"{OVERVIEW_FILE}: render is too dark (mean_luma={luma_mean:.1f})")
            metrics[OVERVIEW_FILE] = {
                "size": [w, h],
                "mode": im.mode,
                "mean_luma": round(luma_mean, 1),
                "luma_stddev": round(luma_std, 1),
                "bytes": ov_path.stat().st_size,
            }

    summary = {
        "stage": "Stage C - Programmatic 3D Asset Pre-Check",
        "status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
        "metrics": metrics,
    }
    REPORT_JSON.write_bytes((json.dumps(summary, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"[Stage C Pre-Check] Status: {summary['status']} (rendered={len(metrics)}/11, failures={len(failures)})")
    for f in failures:
        print(f"  [DEFECT] {f}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
