"""Full Greenleaf Neighbourhood 3D street grid and sunlit diorama builder."""

import math
import bpy
from arch_kit import (
    add_box,
    add_hedge_bush,
    add_multi_branch_tree,
    add_streetlamp,
    make_empty,
)
from buildings import BUILDERS
from spec import BOARD_BOUNDS, LANDMARKS, STREETS


def _add_dashed_line(prefix, start, end, axis, mat, collection, parent, z=0.019):
    dash, gap = 0.78, 0.62
    step = dash + gap
    pos = start + gap * 0.5
    idx = 0
    while pos + dash <= end:
        cx = pos + dash * 0.5 if axis == "x" else start  # handled below
        if axis == "x":
            add_box(f"{prefix}_{idx}", (dash, 0.10, 0.006), (cx, end, z), mat, collection, parent)
        idx += 1
        pos += step


def _add_crosswalk(prefix, cx, cy, orientation, mat, collection, parent, z=0.019):
    """Add crisp zebra crossing stripes ('H' across vertical road, 'V' across horizontal road)."""
    for i in range(5):
        off = -0.92 + i * 0.46
        if orientation == "H":
            add_box(f"{prefix}_{i}", (0.24, 0.72, 0.006), (cx + off, cy, z), mat, collection, parent)
        else:
            add_box(f"{prefix}_{i}", (0.72, 0.24, 0.006), (cx, cy + off, z), mat, collection, parent)


def build_overview_diorama(mats, collection):
    """Assemble full Greenleaf Neighbourhood diorama with exact Single-Source-of-Truth street grid and all 10 buildings."""
    root = make_empty("Greenleaf_Overview_Root", collection)

    bx0, bx1 = BOARD_BOUNDS["x_min"], BOARD_BOUNDS["x_max"]
    by0, by1 = BOARD_BOUNDS["y_min"], BOARD_BOUNDS["y_max"]
    bw = bx1 - bx0
    bd = by1 - by0
    bcx = (bx0 + bx1) * 0.5
    bcy = (by0 + by1) * 0.5

    # Thick museum walnut baseboard + granite curb rim + lush grass ground top at Z=0.0.
    add_box("Board_Walnut", (bw + 0.70, bd + 0.70, 0.48), (bcx, bcy, -0.32), mats["plinth_walnut"], collection, root, bevel=0.05)
    add_box("Board_Curb", (bw + 0.24, bd + 0.24, 0.16), (bcx, bcy, -0.09), mats["curb_granite"], collection, root, bevel=0.02)
    add_box("Board_Grass", (bw, bd, 0.10), (bcx, bcy, -0.05), mats["grass_lush"], collection, root, bevel=0.01)

    # Roads: horizontal Oak (y=+6) and Maple (y=-6) run full span; vertical Pine (x=-2) and River (x=+12) fill non-overlapping segments.
    road_w = 2.6
    for key in ("oak", "maple"):
        st = STREETS[key]
        x0, x1 = st["span"]
        add_box(f"Road_{key}", (x1 - x0, road_w, 0.016), ((x0 + x1) * 0.5, st["center"], 0.008), mats["asphalt"], collection, root)

    v_segments = ((-11.0, -7.3), (-4.7, 4.7), (7.3, 14.0))
    for key in ("pine", "river"):
        st = STREETS[key]
        for idx, (ya, yb) in enumerate(v_segments):
            add_box(f"Road_{key}_{idx}", (road_w, yb - ya, 0.016), (st["center"], (ya + yb) * 0.5, 0.008), mats["asphalt"], collection, root)

    # Raised stone sidewalks (0.5m wide, Z=0.048), cleanly split at intersection corridors so zero sidewalk crosses asphalt.
    sw_h_spans = ((-16.0, -3.8), (-0.2, 10.2), (13.8, 19.0))
    for key in ("oak", "maple"):
        cy = STREETS[key]["center"]
        for side in (-1, 1):
            sy = cy + side * 1.55
            for idx, (xa, xb) in enumerate(sw_h_spans):
                add_box(f"SW_{key}_{side}_{idx}", (xb - xa, 0.50, 0.048), ((xa + xb) * 0.5, sy, 0.024), mats["sidewalk_stone"], collection, root, bevel=0.008)

    sw_v_spans = ((-11.0, -7.8), (-4.2, 4.2), (7.8, 14.0))
    for key in ("pine", "river"):
        cx = STREETS[key]["center"]
        for side in (-1, 1):
            sx = cx + side * 1.55
            for idx, (ya, yb) in enumerate(sw_v_spans):
                add_box(f"SW_{key}_{side}_{idx}", (0.50, yb - ya, 0.048), (sx, (ya + yb) * 0.5, 0.024), mats["sidewalk_stone"], collection, root, bevel=0.008)

    # Corner L-pads closing all 16 sidewalk intersections cleanly.
    for vx in (-3.55, -0.45, 10.45, 13.55):
        for hy in (-7.55, -4.45, 4.45, 7.55):
            add_box(f"SW_Corner_{vx:.2f}_{hy:.2f}", (0.50, 0.50, 0.048), (vx, hy, 0.024), mats["sidewalk_stone"], collection, root, bevel=0.008)

    # Dashed white centerlines along clear road blocks.
    dash, gap = 0.78, 0.62
    for key in ("oak", "maple"):
        cy = STREETS[key]["center"]
        for seg_idx, (xa, xb) in enumerate(((-15.5, -4.1), (0.1, 9.9), (14.1, 18.6))):
            pos = xa + 0.3
            k = 0
            while pos + dash <= xb - 0.3:
                add_box(f"DashH_{key}_{seg_idx}_{k}", (dash, 0.09, 0.006), (pos + dash * 0.5, cy, 0.019), mats["road_paint_white"], collection, root)
                pos += dash + gap
                k += 1

    for key in ("pine", "river"):
        cx = STREETS[key]["center"]
        for seg_idx, (ya, yb) in enumerate(((-10.7, -8.1), (-3.9, 3.9), (8.1, 13.7))):
            pos = ya + 0.3
            k = 0
            while pos + dash <= yb - 0.3:
                add_box(f"DashV_{key}_{seg_idx}_{k}", (0.09, dash, 0.006), (cx, pos + dash * 0.5, 0.019), mats["road_paint_white"], collection, root)
                pos += dash + gap
                k += 1

    # Zebra crosswalks on all 4 approaches of all 4 intersections.
    for ix in (-2.0, 12.0):
        for iy in (-6.0, 6.0):
            _add_crosswalk(f"CW_{ix:.0f}_{iy:.0f}_W", ix - 1.90, iy, "V", mats["road_paint_white"], collection, root)
            _add_crosswalk(f"CW_{ix:.0f}_{iy:.0f}_E", ix + 1.90, iy, "V", mats["road_paint_white"], collection, root)
            _add_crosswalk(f"CW_{ix:.0f}_{iy:.0f}_S", ix, iy - 1.90, "H", mats["road_paint_white"], collection, root)
            _add_crosswalk(f"CW_{ix:.0f}_{iy:.0f}_N", ix, iy + 1.90, "H", mats["road_paint_white"], collection, root)

    # All 10 Greenleaf Neighbourhood landmarks placed at exact Single-Source-of-Truth coordinates!
    for lm in LANDMARKS:
        BUILDERS[lm.id](lm, mats, collection, include_plinth=False)

    # Streetlamps along sidewalks (z = 0.048, avoiding intersections & doorways).
    lamp_coords = [
        (-13.8, 7.55), (-7.0, 7.55), (4.8, 7.55), (15.5, 7.55),
        (-14.8, -4.45), (-7.4, -4.45), (5.0, -4.45), (15.8, -4.45),
        (-3.55, 1.5), (-0.45, -2.5), (10.45, 2.5), (13.55, -2.5),
    ]
    for i, (lx, ly) in enumerate(lamp_coords):
        add_streetlamp(f"StreetLamp_{i}", (lx, ly, 0.048), mats["metal_dark"], mats["lamp_glow"], collection, root, height=1.85)

    # Perimeter & pocket trees strictly outside all building AABBs and road corridors!
    tree_specs = [
        (-14.2, 10.6, 2.35, "foliage_emerald", 1, 0.56),
        (-5.6, 10.6, 2.10, "foliage_lime", 2, 0.50),
        (15.6, 10.6, 2.40, "foliage_emerald", 3, 0.58),
        (17.8, 9.6, 1.95, "foliage_autumn", 4, 0.45),
        (-13.6, 1.8, 2.15, "foliage_lime", 5, 0.50),
        (-5.2, 2.1, 2.25, "foliage_emerald", 6, 0.52),
        (-13.2, -9.6, 2.20, "foliage_emerald", 7, 0.52),
        (-7.4, -9.6, 1.95, "foliage_autumn", 8, 0.46),
        (2.4, -9.6, 2.25, "foliage_lime", 9, 0.54),
        (7.8, -9.6, 2.15, "foliage_emerald", 10, 0.50),
        (15.8, -9.6, 2.30, "foliage_lime", 11, 0.54),
        (17.2, 3.3, 1.90, "foliage_emerald", 12, 0.44),
    ]
    for i, (tx, ty, th, mat_key, seed, rad) in enumerate(tree_specs):
        add_multi_branch_tree(f"TownTree_{i}", (tx, ty, 0.0), th, mats["bark"], mats[mat_key], collection, root, seed=seed, crown_radius=rad)

    hedge_specs = [
        (-14.5, 8.6, (1.2, 0.45, 0.36), "foliage_lime"),
        (-6.2, 8.6, (1.0, 0.42, 0.34), "foliage_emerald"),
        (15.4, 8.6, (1.4, 0.46, 0.36), "foliage_lime"),
        (4.8, 2.9, (1.2, 0.45, 0.36), "foliage_emerald"),
        (5.2, -9.2, (1.5, 0.48, 0.38), "foliage_lime"),
    ]
    for i, (hx, hy, hsize, mkey) in enumerate(hedge_specs):
        add_hedge_bush(f"TownHedge_{i}", (hx, hy, 0.0), hsize, mats[mkey], collection, root, seed=i + 3)

    return root
