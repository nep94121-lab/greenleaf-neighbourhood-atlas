"""Bespoke 3D architectural builders for all 10 Greenleaf Neighbourhood landmarks."""

import math
import bpy
from arch_kit import (
    add_awning,
    add_box,
    add_cylinder,
    add_diorama_plinth,
    add_door_assembly,
    add_hedge_bush,
    add_mini_vehicle,
    add_multi_branch_tree,
    add_pitched_roof,
    add_recessed_window,
    add_streetlamp,
    add_wooden_bench,
    make_empty,
)
from spec import FACING_ROT_Z


def _local_dims(lm):
    if lm.facing in ("E", "W"):
        return lm.depth, lm.width
    return lm.width, lm.depth


def _place_root(root, lm, include_plinth):
    if not include_plinth:
        root.location = (lm.cx, lm.cy, 0.0)
        root.rotation_euler = (0.0, 0.0, FACING_ROT_Z[lm.facing])
    return root


def _add_picket_span(prefix, x_start, x_end, y_pos, count, mat, collection, parent):
    """Non-overlapping white picket fence segment with rail offset behind pickets."""
    span = x_end - x_start
    cx = (x_start + x_end) * 0.5
    add_box(f"{prefix}_RailTop", (span + 0.04, 0.03, 0.04), (cx, y_pos + 0.032, 0.27), mat, collection, parent)
    add_box(f"{prefix}_RailBot", (span + 0.04, 0.03, 0.04), (cx, y_pos + 0.032, 0.11), mat, collection, parent)
    for i in range(count):
        px = x_start + (span * i) / max(1, count - 1)
        add_box(f"{prefix}_Picket_{i}", (0.055, 0.03, 0.36), (px, y_pos, 0.18), mat, collection, parent, bevel=0.008)


def _add_planter_box(prefix, center, size, box_mat, foliage_mat, bloom_mat, collection, parent):
    sx, sy, sz = size
    add_box(f"{prefix}_Box", (sx, sy, sz), (center[0], center[1], center[2] + sz * 0.5), box_mat, collection, parent, bevel=0.01)
    add_hedge_bush(f"{prefix}_Leaves", (center[0], center[1], center[2] + sz), (sx * 0.9, sy * 0.9, 0.18), foliage_mat, collection, parent, seed=5)
    for k in (-1, 0, 1):
        add_box(f"{prefix}_Bloom_{k}", (0.08, 0.08, 0.07), (center[0] + k * sx * 0.28, center[1], center[2] + sz + 0.14), bloom_mat, collection, parent, bevel=0.02)


def build_my_house(lm, mats, collection, include_plinth=True):
    """Cozy two-story suburban house with dormer, porch, chimney, flower boxes, and garden tree."""
    lw, ld = _local_dims(lm)
    root = make_empty(f"LM_{lm.id}", collection)
    if include_plinth:
        add_diorama_plinth(f"{lm.id}_Plinth", lw, ld, lm.plinth_style, mats, collection, root)

    add_box(f"{lm.id}_Lawn", (lw - 0.08, ld - 0.08, 0.03), (0.0, 0.0, 0.015), mats["grass_lush"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_Walkway", (0.76, 1.05, 0.04), (-0.49, -ld * 0.5 + 0.54, 0.025), mats["sidewalk_stone"], collection, root, bevel=0.01)

    bw, bd, bh = 2.42, 2.04, 1.98
    bx, by = -0.38, 0.26
    add_box(f"{lm.id}_Foundation", (bw + 0.10, bd + 0.10, 0.22), (bx, by, 0.11), mats["brick_warm"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_Body", (bw, bd, bh), (bx, by, 0.22 + bh * 0.5), mats["stucco_butter"], collection, root, bevel=0.02)

    for sx in (-1, 1):
        for sy in (-1, 1):
            add_box(
                f"{lm.id}_Corner_{sx}_{sy}",
                (0.11, 0.11, bh),
                (bx + sx * (bw * 0.5 - 0.02), by + sy * (bd * 0.5 - 0.02), 0.22 + bh * 0.5),
                mats["wood_white"],
                collection,
                root,
                bevel=0.01,
            )
    add_box(f"{lm.id}_BeltCourse", (bw + 0.06, bd + 0.06, 0.07), (bx, by, 1.24), mats["wood_white"], collection, root, bevel=0.01)

    z_eave = 0.22 + bh
    add_pitched_roof(
        f"{lm.id}_Roof",
        bw,
        bd,
        0.92,
        z_eave,
        mats["stucco_butter"],
        mats["roof_terracotta"],
        mats["wood_white"],
        collection,
        root,
        axis="X",
        overhang=0.18,
        offset_xy=(bx, by),
    )

    # Front attic dormer window.
    dx, dy, dz = bx + 0.55, by - 0.55, z_eave + 0.42
    add_box(f"{lm.id}_DormerBody", (0.60, 0.60, 0.50), (dx, dy, dz), mats["stucco_butter"], collection, root, bevel=0.01)
    add_pitched_roof(
        f"{lm.id}_DormerRoof",
        0.62,
        0.66,
        0.25,
        dz + 0.23,
        mats["stucco_butter"],
        mats["roof_terracotta"],
        mats["wood_white"],
        collection,
        root,
        axis="Y",
        overhang=0.06,
        offset_xy=(dx, dy),
        add_ribs=False,
    )
    add_recessed_window(
        f"{lm.id}_DormerWin",
        (dx, dy - 0.30, dz + 0.02),
        0.34,
        0.34,
        "-Y",
        mats["wood_white"],
        mats["glass"],
        mats["interior_warm"],
        collection,
        root,
        mullions=(1, 1),
    )

    # Brick chimney with terracotta flue.
    cx_ch, cy_ch = bx + 0.72, by + 0.42
    add_box(f"{lm.id}_Chimney", (0.36, 0.36, 1.22), (cx_ch, cy_ch, z_eave + 0.54), mats["brick_red"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_ChimneyCap", (0.44, 0.44, 0.08), (cx_ch, cy_ch, z_eave + 1.18), mats["curb_granite"], collection, root, bevel=0.015)
    add_cylinder(f"{lm.id}_Flue", 0.085, 0.075, 0.22, (cx_ch, cy_ch, z_eave + 1.30), mats["roof_terracotta"], collection, root, segments=12)

    # Front porch + steps + lantern.
    px, py = bx - 0.14, by - bd * 0.5 - 0.32
    pw, pd = 1.44, 0.64
    add_box(f"{lm.id}_PorchDeck", (pw, pd, 0.18), (px, py, 0.09), mats["wood_warm"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_PorchStep", (0.72, 0.22, 0.09), (px, py - pd * 0.5 - 0.11, 0.045), mats["wood_warm"], collection, root, bevel=0.01)
    for sx in (-1, 1):
        add_box(f"{lm.id}_PorchPost_{sx}", (0.08, 0.08, 1.10), (px + sx * (pw * 0.5 - 0.08), py - pd * 0.5 + 0.07, 0.18 + 0.55), mats["wood_white"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_PorchRoof", (pw + 0.16, pd + 0.18, 0.07), (px, py - 0.04, 1.34), mats["roof_terracotta"], collection, root, bevel=0.015, rotation=(-0.22, 0.0, 0.0))

    add_door_assembly(
        f"{lm.id}_FrontDoor",
        (px - 0.18, by - bd * 0.5),
        0.18,
        0.54,
        1.02,
        "-Y",
        mats["accent_teal"],
        mats["wood_white"],
        mats["glass"],
        mats["metal_brass"],
        collection,
        root,
        step_depth=0.0,
    )
    add_box(f"{lm.id}_PorchLamp", (0.10, 0.10, 0.16), (px + 0.22, by - bd * 0.5 - 0.07, 1.06), mats["lamp_glow"], collection, root, bevel=0.01)

    add_recessed_window(
        f"{lm.id}_WinFrontR",
        (bx + 0.66, by - bd * 0.5, 0.78),
        0.50,
        0.62,
        "-Y",
        mats["wood_white"],
        mats["glass"],
        mats["interior_warm"],
        collection,
        root,
        mullions=(1, 1),
        shutter_mat=mats["accent_teal"],
    )
    _add_planter_box(f"{lm.id}_WinBox", (bx + 0.66, by - bd * 0.5 - 0.10, 0.31), (0.56, 0.16, 0.12), mats["wood_warm"], mats["foliage_lime"], mats["flower_coral"], collection, root)

    for idx, wx in enumerate((bx - 0.60, bx + 0.60)):
        add_recessed_window(
            f"{lm.id}_WinUp_{idx}",
            (wx, by - bd * 0.5, 1.72),
            0.46,
            0.54,
            "-Y",
            mats["wood_white"],
            mats["glass"],
            mats["interior_warm"],
            collection,
            root,
            mullions=(1, 1),
            shutter_mat=mats["accent_teal"],
        )

    for side, fdir in ((-1, "-X"), (1, "+X")):
        add_recessed_window(f"{lm.id}_WinSide_{side}_L", (bx + side * bw * 0.5, by, 0.78), 0.54, 0.62, fdir, mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root)
        add_recessed_window(f"{lm.id}_WinSide_{side}_U", (bx + side * bw * 0.5, by, 1.72), 0.48, 0.54, fdir, mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root)
    add_recessed_window(f"{lm.id}_WinBack", (bx, by + bd * 0.5, 0.82), 0.62, 0.62, "+Y", mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root)

    # Clean non-overlapping picket fences flanking the front walkway.
    _add_picket_span(f"{lm.id}_FenceL", -1.68, -0.96, -ld * 0.5 + 0.14, 6, mats["wood_white"], collection, root)
    _add_picket_span(f"{lm.id}_FenceR", -0.04, 1.15, -ld * 0.5 + 0.14, 8, mats["wood_white"], collection, root)

    add_box(f"{lm.id}_MailboxPost", (0.07, 0.07, 0.52), (-0.92, -ld * 0.5 + 0.30, 0.26), mats["wood_white"], collection, root, bevel=0.008)
    add_box(f"{lm.id}_Mailbox", (0.14, 0.22, 0.14), (-0.92, -ld * 0.5 + 0.30, 0.56), mats["accent_red"], collection, root, bevel=0.02)

    add_multi_branch_tree(f"{lm.id}_Tree", (1.50, -0.78, 0.0), 2.25, mats["bark"], mats["foliage_emerald"], collection, root, seed=3, crown_radius=0.46)
    add_hedge_bush(f"{lm.id}_Hedge", (1.28, -ld * 0.5 + 0.44, 0.0), (0.76, 0.32, 0.34), mats["foliage_lime"], collection, root, seed=2)
    return _place_root(root, lm, include_plinth)


def build_school(lm, mats, collection, include_plinth=True):
    """Civic two-story red-brick school with central clock tower, bell cupola, flagpole, and bike rack."""
    lw, ld = _local_dims(lm)
    root = make_empty(f"LM_{lm.id}", collection)
    if include_plinth:
        add_diorama_plinth(f"{lm.id}_Plinth", lw, ld, lm.plinth_style, mats, collection, root)

    # Courtyard paving & lawn border.
    add_box(f"{lm.id}_Courtyard", (lw - 0.12, ld - 0.12, 0.03), (0.0, 0.0, 0.015), mats["sidewalk_stone"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_LawnStripL", (0.72, 0.62, 0.04), (-1.48, -ld * 0.5 + 0.44, 0.025), mats["grass_lush"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_LawnStripR", (0.72, 0.62, 0.04), (1.48, -ld * 0.5 + 0.44, 0.025), mats["grass_lush"], collection, root, bevel=0.01)

    # Main brick academic wing.
    bw, bd, bh = 3.16, 2.15, 2.35
    bx, by = 0.0, 0.42
    add_box(f"{lm.id}_PlinthStone", (bw + 0.12, bd + 0.12, 0.24), (bx, by, 0.12), mats["curb_granite"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_MainBrick", (bw, bd, bh), (bx, by, 0.24 + bh * 0.5), mats["brick_red"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_Cornice", (bw + 0.16, bd + 0.16, 0.12), (bx, by, 0.24 + bh + 0.03), mats["wood_white"], collection, root, bevel=0.015)

    # Main hipped/pitched slate roof.
    z_eave = 0.24 + bh + 0.08
    add_pitched_roof(
        f"{lm.id}_MainRoof",
        bw,
        bd,
        0.88,
        z_eave,
        mats["brick_red"],
        mats["roof_slate"],
        mats["wood_white"],
        collection,
        root,
        axis="X",
        overhang=0.18,
        offset_xy=(bx, by),
    )

    # Central projecting clock-tower pavilion.
    tw, td, th = 1.24, 0.58, 2.85
    ty = by - bd * 0.5 - 0.08
    add_box(f"{lm.id}_TowerBase", (tw + 0.08, td + 0.08, 0.24), (bx, ty, 0.12), mats["curb_granite"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_TowerBody", (tw, td, th), (bx, ty, 0.24 + th * 0.5), mats["brick_warm"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_TowerTrim", (tw + 0.10, td + 0.10, 0.10), (bx, ty, 0.24 + th), mats["wood_white"], collection, root, bevel=0.015)

    # Upper clock belfry cube + crisp pyramidal teal cupola + brass spire.
    cb_w = 0.92
    cb_z = 0.24 + th + 0.42
    add_box(f"{lm.id}_Belfry", (cb_w, cb_w, 0.84), (bx, ty + 0.06, cb_z), mats["stucco_cream"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_BelfryCap", (cb_w + 0.12, cb_w + 0.12, 0.09), (bx, ty + 0.06, cb_z + 0.44), mats["wood_white"], collection, root, bevel=0.015)
    add_cylinder(f"{lm.id}_CupolaRoof", 0.66, 0.04, 0.68, (bx, ty + 0.06, cb_z + 0.82), mats["roof_teal"], collection, root, segments=4, rotation=(0.0, 0.0, math.pi * 0.25), smooth=False)
    add_cylinder(f"{lm.id}_Spire", 0.025, 0.015, 0.40, (bx, ty + 0.06, cb_z + 1.32), mats["metal_brass"], collection, root, segments=10)

    # 3D Circular Clock face on front of belfry.
    clk_y = ty + 0.06 - cb_w * 0.5 - 0.03
    add_cylinder(f"{lm.id}_ClockRim", 0.29, 0.29, 0.05, (bx, clk_y, cb_z + 0.02), mats["metal_brass"], collection, root, segments=24, rotation=(math.pi * 0.5, 0.0, 0.0))
    add_cylinder(f"{lm.id}_ClockDial", 0.24, 0.24, 0.06, (bx, clk_y - 0.01, cb_z + 0.02), mats["wood_white"], collection, root, segments=24, rotation=(math.pi * 0.5, 0.0, 0.0))
    add_box(f"{lm.id}_ClockHandH", (0.03, 0.04, 0.13), (bx, clk_y - 0.035, cb_z + 0.07), mats["metal_dark"], collection, root)
    add_box(f"{lm.id}_ClockHandM", (0.15, 0.04, 0.025), (bx + 0.06, clk_y - 0.035, cb_z + 0.02), mats["metal_dark"], collection, root)

    # School sign plaque with brass crest bars & arched double entrance doors.
    add_box(f"{lm.id}_SignBoard", (1.06, 0.08, 0.26), (bx, ty - td * 0.5 - 0.03, 1.82), mats["accent_teal"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_SignBorder", (1.12, 0.05, 0.32), (bx, ty - td * 0.5 - 0.01, 1.82), mats["metal_brass"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_SignCrestL", (0.28, 0.03, 0.06), (bx - 0.28, ty - td * 0.5 - 0.06, 1.82), mats["accent_amber"], collection, root, bevel=0.005)
    add_box(f"{lm.id}_SignCrestR", (0.28, 0.03, 0.06), (bx + 0.28, ty - td * 0.5 - 0.06, 1.82), mats["accent_amber"], collection, root, bevel=0.005)
    add_cylinder(f"{lm.id}_SignMed", 0.08, 0.08, 0.04, (bx, ty - td * 0.5 - 0.06, 1.82), mats["metal_brass"], collection, root, segments=16, rotation=(math.pi * 0.5, 0.0, 0.0))
    add_door_assembly(
        f"{lm.id}_Doors",
        (bx, ty - td * 0.5),
        0.24,
        0.86,
        1.22,
        "-Y",
        mats["wood_dark"],
        mats["wood_white"],
        mats["glass"],
        mats["metal_brass"],
        collection,
        root,
        double=True,
        step_depth=0.30,
    )

    # Symmetric classroom windows (left & right wings, 2 floors).
    for wx in (-1.08, 1.08):
        add_recessed_window(f"{lm.id}_Win1_{wx:.1f}", (wx, by - bd * 0.5, 0.92), 0.66, 0.78, "-Y", mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root, mullions=(2, 1), sill_mat=mats["curb_granite"])
        add_recessed_window(f"{lm.id}_Win2_{wx:.1f}", (wx, by - bd * 0.5, 1.98), 0.66, 0.78, "-Y", mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root, mullions=(2, 1), sill_mat=mats["curb_granite"])
    add_recessed_window(f"{lm.id}_WinCtr2", (bx, ty - td * 0.5, 2.38), 0.60, 0.62, "-Y", mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root, mullions=(1, 1), sill_mat=mats["curb_granite"])

    for side, fdir in ((-1, "-X"), (1, "+X")):
        for wz in (0.92, 1.98):
            add_recessed_window(f"{lm.id}_WinSide_{side}_{wz:.1f}", (bx + side * bw * 0.5, by, wz), 0.72, 0.72, fdir, mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root, mullions=(2, 1))

    # Flagpole with fluttering green/amber school pennant in front left plaza.
    fx, fy = -1.48, -ld * 0.5 + 0.44
    add_cylinder(f"{lm.id}_FlagBase", 0.16, 0.14, 0.18, (fx, fy, 0.09), mats["curb_granite"], collection, root, segments=12)
    add_cylinder(f"{lm.id}_FlagMast", 0.032, 0.022, 2.45, (fx, fy, 0.18 + 1.225), mats["metal_silver"], collection, root, segments=10)
    add_box(f"{lm.id}_FlagMain", (0.52, 0.03, 0.30), (fx + 0.27, fy, 2.45), mats["accent_teal"], collection, root, bevel=0.005, rotation=(0.0, 0.0, 0.12))
    add_box(f"{lm.id}_FlagStripe", (0.50, 0.035, 0.08), (fx + 0.27, fy, 2.45), mats["accent_amber"], collection, root, rotation=(0.0, 0.0, 0.12))

    # Bike rack & clear courtyard tree in front right corner (completely clear of walls!).
    rx, ry = 1.05, -ld * 0.5 + 0.50
    add_box(f"{lm.id}_RackBar", (0.72, 0.04, 0.04), (rx, ry, 0.06), mats["metal_silver"], collection, root)
    for bi in (-0.22, 0.0, 0.22):
        add_box(f"{lm.id}_RackLoop_{bi:.2f}", (0.03, 0.26, 0.24), (rx + bi, ry, 0.18), mats["metal_silver"], collection, root, bevel=0.005)
    add_multi_branch_tree(f"{lm.id}_Tree", (1.82, -1.16, 0.0), 2.10, mats["bark"], mats["foliage_lime"], collection, root, seed=7, crown_radius=0.38)
    return _place_root(root, lm, include_plinth)


def build_park(lm, mats, collection, include_plinth=True):
    """Lush neighbourhood park with stone fountain, wooden benches, pergola arbor, and multi-branch trees."""
    lw, ld = _local_dims(lm)
    root = make_empty(f"LM_{lm.id}", collection)
    if include_plinth:
        add_diorama_plinth(f"{lm.id}_Plinth", lw, ld, lm.plinth_style, mats, collection, root)

    add_box(f"{lm.id}_Grass", (lw - 0.08, ld - 0.08, 0.03), (0.0, 0.0, 0.015), mats["grass_park"], collection, root, bevel=0.01)

    # Cross stone pathways + circular central fountain plaza.
    add_box(f"{lm.id}_PathNS", (0.78, ld - 0.12, 0.04), (0.0, 0.0, 0.025), mats["sidewalk_stone"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_PathEW", (lw - 0.18, 0.68, 0.04), (0.0, -0.05, 0.025), mats["sidewalk_stone"], collection, root, bevel=0.01)
    add_cylinder(f"{lm.id}_Plaza", 1.18, 1.18, 0.05, (0.0, -0.05, 0.03), mats["sidewalk_stone"], collection, root, segments=24)

    # Low stone perimeter curb with South gateway pillars & warm iron lanterns.
    for side in (-1, 1):
        add_box(f"{lm.id}_WallFront_{side}", (1.62, 0.14, 0.24), (side * 1.46, -ld * 0.5 + 0.14, 0.12), mats["curb_granite"], collection, root, bevel=0.015)
        px = side * 0.56
        py = -ld * 0.5 + 0.16
        add_box(f"{lm.id}_GatePillar_{side}", (0.24, 0.24, 0.58), (px, py, 0.29), mats["brick_warm"], collection, root, bevel=0.02)
        add_box(f"{lm.id}_GateCap_{side}", (0.30, 0.30, 0.08), (px, py, 0.61), mats["curb_granite"], collection, root, bevel=0.015)
        add_box(f"{lm.id}_GateLamp_{side}", (0.12, 0.12, 0.18), (px, py, 0.74), mats["lamp_glow"], collection, root, bevel=0.01)

    # Tiered 3D octagonal stone fountain with visible turquoise water pool.
    fcx, fcy = 0.0, -0.05
    add_cylinder(f"{lm.id}_FountainBase", 0.84, 0.86, 0.14, (fcx, fcy, 0.09), mats["curb_granite"], collection, root, segments=12, smooth=False)
    add_cylinder(f"{lm.id}_FountainRim", 0.80, 0.82, 0.14, (fcx, fcy, 0.21), mats["sidewalk_stone"], collection, root, segments=12, smooth=False)
    add_cylinder(f"{lm.id}_FountainWater", 0.72, 0.72, 0.06, (fcx, fcy, 0.275), mats["water"], collection, root, segments=16, smooth=False)
    add_cylinder(f"{lm.id}_FountainPed", 0.16, 0.13, 0.42, (fcx, fcy, 0.42), mats["curb_granite"], collection, root, segments=12, smooth=False)
    add_cylinder(f"{lm.id}_FountainBowl", 0.36, 0.42, 0.11, (fcx, fcy, 0.62), mats["sidewalk_stone"], collection, root, segments=12, smooth=False)
    add_cylinder(f"{lm.id}_FountainTopWater", 0.34, 0.34, 0.05, (fcx, fcy, 0.675), mats["water"], collection, root, segments=14, smooth=False)
    add_cylinder(f"{lm.id}_FountainSpout", 0.045, 0.02, 0.28, (fcx, fcy, 0.82), mats["water"], collection, root, segments=10, smooth=False)

    # 3 wooden & iron benches facing the fountain.
    add_wooden_bench(f"{lm.id}_BenchW", (-1.15, -0.05, 0.04), -math.pi * 0.5, mats["wood_warm"], mats["metal_dark"], collection, root)
    add_wooden_bench(f"{lm.id}_BenchE", (1.15, -0.05, 0.04), math.pi * 0.5, mats["wood_warm"], mats["metal_dark"], collection, root)
    add_wooden_bench(f"{lm.id}_BenchN", (0.0, 1.18, 0.04), math.pi, mats["wood_warm"], mats["metal_dark"], collection, root)

    # Timber garden pergola arbor on North-West terrace with climbing vine canopy.
    gx, gy = -1.45, 0.92
    for px_off in (-0.52, 0.52):
        for py_off in (-0.42, 0.42):
            add_box(f"{lm.id}_PergolaPost_{px_off:.1f}_{py_off:.1f}", (0.09, 0.09, 1.38), (gx + px_off, gy + py_off, 0.69), mats["wood_warm"], collection, root, bevel=0.01)
    for r in range(5):
        ry = gy - 0.44 + r * 0.22
        add_box(f"{lm.id}_PergolaRafter_{r}", (1.28, 0.06, 0.09), (gx, ry, 1.42), mats["wood_dark"], collection, root, bevel=0.008)
    add_hedge_bush(f"{lm.id}_PergolaVineA", (gx - 0.15, gy + 0.18, 1.43), (0.86, 0.46, 0.24), mats["foliage_emerald"], collection, root, seed=9)
    add_hedge_bush(f"{lm.id}_PergolaVineB", (gx + 0.36, gy - 0.12, 1.43), (0.58, 0.58, 0.22), mats["foliage_lime"], collection, root, seed=12)
    for bi, (vx, vy) in enumerate(((-0.22, 0.20), (0.10, 0.14), (0.35, -0.05))):
        add_box(f"{lm.id}_PergolaBloom_{bi}", (0.09, 0.09, 0.08), (gx + vx, gy + vy, 1.56), mats["flower_coral"], collection, root, bevel=0.025)

    # Four multi-branch trees of varied silhouettes & foliage tones + flowering shrubs.
    add_multi_branch_tree(f"{lm.id}_TreeNE", (1.58, 1.05, 0.0), 2.35, mats["bark"], mats["foliage_emerald"], collection, root, seed=11, crown_radius=0.56)
    add_multi_branch_tree(f"{lm.id}_TreeNW", (-1.75, -1.05, 0.0), 1.95, mats["bark"], mats["foliage_autumn"], collection, root, seed=14, crown_radius=0.45)
    add_multi_branch_tree(f"{lm.id}_TreeSE", (1.68, -0.95, 0.0), 2.10, mats["bark"], mats["foliage_lime"], collection, root, seed=17, crown_radius=0.48)
    add_multi_branch_tree(f"{lm.id}_TreeN", (0.92, 1.18, 0.0), 1.85, mats["bark"], mats["foliage_emerald"], collection, root, seed=21, crown_radius=0.42)

    add_hedge_bush(f"{lm.id}_FlowerBed1", (-0.95, -1.10, 0.0), (0.68, 0.38, 0.30), mats["foliage_lime"], collection, root, seed=4)
    add_hedge_bush(f"{lm.id}_FlowerBed2", (0.95, -1.10, 0.0), (0.68, 0.38, 0.30), mats["foliage_emerald"], collection, root, seed=6)
    for k, fx_b in enumerate((-1.10, -0.95, -0.80, 0.80, 0.95, 1.10)):
        add_box(f"{lm.id}_Bloom_{k}", (0.11, 0.11, 0.09), (fx_b, -1.10, 0.26), mats["flower_coral"] if k % 2 == 0 else mats["flower_gold"], collection, root, bevel=0.025)
    return _place_root(root, lm, include_plinth)


def build_post_office(lm, mats, collection, include_plinth=True):
    """Heritage brick & cream Post Office with stepped gable, golden post emblem, parcel awning, and red letterbox."""
    lw, ld = _local_dims(lm)
    root = make_empty(f"LM_{lm.id}", collection)
    if include_plinth:
        add_diorama_plinth(f"{lm.id}_Plinth", lw, ld, lm.plinth_style, mats, collection, root)

    add_box(f"{lm.id}_Paving", (lw - 0.08, ld - 0.08, 0.03), (0.0, 0.0, 0.015), mats["sidewalk_stone"], collection, root, bevel=0.01)

    bw, bd, bh = 2.58, 2.02, 2.05
    bx, by = 0.0, 0.28
    add_box(f"{lm.id}_Base", (bw + 0.08, bd + 0.08, 0.22), (bx, by, 0.11), mats["curb_granite"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_LowerBrick", (bw, bd, 1.15), (bx, by, 0.22 + 0.575), mats["brick_red"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_UpperStucco", (bw - 0.04, bd - 0.04, 0.90), (bx, by, 1.37 + 0.45), mats["stucco_cream"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_Band", (bw + 0.08, bd + 0.08, 0.08), (bx, by, 1.37), mats["wood_white"], collection, root, bevel=0.01)

    z_eave = 0.22 + bh
    add_pitched_roof(f"{lm.id}_Roof", bw, bd, 0.72, z_eave, mats["stucco_cream"], mats["roof_slate"], mats["wood_white"], collection, root, axis="X", overhang=0.14, offset_xy=(bx, by))

    # Front stepped civic parapet pediment + golden envelope emblem.
    add_box(f"{lm.id}_Parapet", (1.62, 0.16, 0.62), (bx, by - bd * 0.5 + 0.04, z_eave + 0.28), mats["brick_red"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_ParapetCap", (1.72, 0.22, 0.08), (bx, by - bd * 0.5 + 0.04, z_eave + 0.60), mats["wood_white"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_PostSign", (1.28, 0.08, 0.30), (bx, by - bd * 0.5 - 0.04, z_eave + 0.26), mats["accent_blue"], collection, root, bevel=0.015)
    # 3D Golden envelope icon mounted on the civic signboard.
    add_box(f"{lm.id}_EnvBody", (0.38, 0.05, 0.22), (bx, by - bd * 0.5 - 0.09, z_eave + 0.26), mats["metal_brass"], collection, root, bevel=0.008)
    add_box(f"{lm.id}_EnvFlap", (0.24, 0.06, 0.14), (bx, by - bd * 0.5 - 0.10, z_eave + 0.30), mats["accent_amber"], collection, root, bevel=0.006, rotation=(0.0, math.pi * 0.25, 0.0))

    # Left entrance double doors + right parcel window & striped awning.
    add_door_assembly(
        f"{lm.id}_Doors",
        (bx - 0.56, by - bd * 0.5),
        0.22,
        0.74,
        1.04,
        "-Y",
        mats["accent_blue"],
        mats["wood_white"],
        mats["glass"],
        mats["metal_brass"],
        collection,
        root,
        double=True,
        step_depth=0.28,
    )
    add_recessed_window(f"{lm.id}_ParcelWin", (bx + 0.58, by - bd * 0.5, 0.88), 0.72, 0.62, "-Y", mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root, mullions=(1, 1))
    add_awning(f"{lm.id}_ParcelAwning", (bx + 0.58, by - bd * 0.5 - 0.02, 1.36), 0.88, 0.44, 0.20, "-Y", mats["awning_red"], mats["metal_dark"], collection, root)

    for wx in (-0.65, 0.65):
        add_recessed_window(f"{lm.id}_WinUp_{wx:.1f}", (bx + wx, by - bd * 0.5, 1.80), 0.48, 0.52, "-Y", mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root)
    for side, fdir in ((-1, "-X"), (1, "+X")):
        add_recessed_window(f"{lm.id}_WinSide_{side}", (bx + side * bw * 0.5, by, 1.12), 0.56, 0.56, fdir, mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root)

    # Iconic bright-red cylindrical pillar letterbox outside on front stoop + stacked parcel boxes.
    lbx, lby = -1.06, -ld * 0.5 + 0.36
    add_cylinder(f"{lm.id}_LetterboxPed", 0.14, 0.13, 0.14, (lbx, lby, 0.07), mats["metal_dark"], collection, root, segments=16)
    add_cylinder(f"{lm.id}_LetterboxBody", 0.12, 0.12, 0.48, (lbx, lby, 0.38), mats["accent_red"], collection, root, segments=16, bevel=0.01)
    add_cylinder(f"{lm.id}_LetterboxCap", 0.145, 0.08, 0.10, (lbx, lby, 0.65), mats["accent_red"], collection, root, segments=16)
    add_box(f"{lm.id}_LetterboxSlot", (0.14, 0.04, 0.05), (lbx, lby - 0.11, 0.50), mats["metal_brass"], collection, root)

    add_box(f"{lm.id}_Parcel1", (0.30, 0.28, 0.24), (0.94, -ld * 0.5 + 0.46, 0.12), mats["wood_warm"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_Parcel2", (0.22, 0.22, 0.18), (0.92, -ld * 0.5 + 0.46, 0.33), mats["stucco_cream"], collection, root, bevel=0.01, rotation=(0.0, 0.0, 0.24))
    _add_planter_box(f"{lm.id}_Planter", (1.38, -ld * 0.5 + 0.46, 0.0), (0.36, 0.32, 0.22), mats["brick_warm"], mats["foliage_emerald"], mats["flower_gold"], collection, root)
    return _place_root(root, lm, include_plinth)


def build_restaurant(lm, mats, collection, include_plinth=True):
    """Warm bistro restaurant with red/cream striped awning, patio tables & cups, hanging sign, and copper hood."""
    lw, ld = _local_dims(lm)
    root = make_empty(f"LM_{lm.id}", collection)
    if include_plinth:
        add_diorama_plinth(f"{lm.id}_Plinth", lw, ld, lm.plinth_style, mats, collection, root)

    add_box(f"{lm.id}_PatioStone", (lw - 0.08, ld - 0.08, 0.03), (0.0, 0.0, 0.015), mats["sidewalk_stone"], collection, root, bevel=0.01)

    bw, bd, bh = 2.86, 1.88, 2.02
    bx, by = 0.0, 0.44
    add_box(f"{lm.id}_Foundation", (bw + 0.08, bd + 0.08, 0.16), (bx, by, 0.08), mats["curb_granite"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_GroundWall", (bw, bd, 1.10), (bx, by, 0.16 + 0.55), mats["brick_warm"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_UpperWall", (bw - 0.04, bd - 0.04, 0.92), (bx, by, 1.26 + 0.46), mats["stucco_cream"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_Frieze", (bw + 0.10, bd + 0.10, 0.10), (bx, by, 1.26), mats["wood_dark"], collection, root, bevel=0.01)

    z_eave = 0.16 + bh
    add_pitched_roof(f"{lm.id}_Roof", bw, bd, 0.68, z_eave, mats["stucco_cream"], mats["roof_terracotta"], mats["wood_dark"], collection, root, axis="X", overhang=0.14, offset_xy=(bx, by))
    # Copper kitchen exhaust pipe.
    add_cylinder(f"{lm.id}_VentPipe", 0.10, 0.10, 0.85, (bx + 0.88, by + 0.36, z_eave + 0.44), mats["metal_brass"], collection, root, segments=12)
    add_cylinder(f"{lm.id}_VentCap", 0.18, 0.06, 0.14, (bx + 0.88, by + 0.36, z_eave + 0.90), mats["metal_brass"], collection, root, segments=12)

    # Large glazed bistro storefront + door + full-width striped awning.
    add_door_assembly(f"{lm.id}_Door", (bx - 0.82, by - bd * 0.5), 0.16, 0.64, 1.02, "-Y", mats["wood_dark"], mats["wood_dark"], mats["glass"], mats["metal_brass"], collection, root, step_depth=0.18)
    add_recessed_window(f"{lm.id}_ShopWin", (bx + 0.48, by - bd * 0.5, 0.72), 1.38, 0.78, "-Y", mats["wood_dark"], mats["glass"], mats["interior_warm"], collection, root, mullions=(2, 0))
    add_awning(f"{lm.id}_Awning", (bx, by - bd * 0.5 - 0.02, 1.25), 2.74, 0.64, 0.24, "-Y", mats["awning_red"], mats["metal_dark"], collection, root)

    for wx in (-0.82, 0.0, 0.82):
        add_recessed_window(f"{lm.id}_WinUp_{wx:.1f}", (bx + wx, by - bd * 0.5, 1.72), 0.46, 0.50, "-Y", mats["wood_dark"], mats["glass"], mats["interior_warm"], collection, root)
    for side, fdir in ((-1, "-X"), (1, "+X")):
        add_recessed_window(f"{lm.id}_WinSide_{side}", (bx + side * bw * 0.5, by, 1.66), 0.52, 0.48, fdir, mats["wood_dark"], mats["glass"], mats["interior_warm"], collection, root)

    # 3D Round chef-plate signboard mounted above awning + wall bracket arm (non-floating).
    add_box(f"{lm.id}_SignBack", (1.24, 0.08, 0.26), (bx, by - bd * 0.5 - 0.05, 1.38), mats["wood_dark"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_SignArm", (0.05, 0.44, 0.05), (bx + 1.24, by - bd * 0.5 - 0.22, 1.76), mats["metal_dark"], collection, root, bevel=0.008)
    add_cylinder(f"{lm.id}_SignMedallion", 0.18, 0.18, 0.05, (bx + 1.24, by - bd * 0.5 - 0.34, 1.56), mats["accent_red"], collection, root, segments=18, rotation=(0.0, math.pi * 0.5, 0.0))

    # Two outdoor sidewalk bistro tables + chairs + espresso cups + menu easel.
    for tx in (0.15, 1.05):
        ty = -ld * 0.5 + 0.56
        add_cylinder(f"{lm.id}_TableBase_{tx:.2f}", 0.18, 0.04, 0.04, (tx, ty, 0.04), mats["metal_dark"], collection, root, segments=12)
        add_cylinder(f"{lm.id}_TableStem_{tx:.2f}", 0.03, 0.03, 0.36, (tx, ty, 0.22), mats["metal_dark"], collection, root, segments=10)
        add_cylinder(f"{lm.id}_TableTop_{tx:.2f}", 0.26, 0.26, 0.035, (tx, ty, 0.41), mats["wood_warm"], collection, root, segments=16, bevel=0.006)
        add_cylinder(f"{lm.id}_Cup_{tx:.2f}", 0.04, 0.05, 0.06, (tx + 0.05, ty - 0.04, 0.46), mats["wood_white"], collection, root, segments=10)
        for cs in (-1, 1):
            cx_c = tx + cs * 0.32
            add_box(f"{lm.id}_ChairSeat_{tx:.2f}_{cs}", (0.18, 0.18, 0.03), (cx_c, ty, 0.22), mats["wood_warm"], collection, root, bevel=0.005)
            add_box(f"{lm.id}_ChairBack_{tx:.2f}_{cs}", (0.03, 0.18, 0.22), (cx_c + cs * 0.08, ty, 0.33), mats["metal_dark"], collection, root, bevel=0.004)
            add_box(f"{lm.id}_ChairLegs_{tx:.2f}_{cs}", (0.14, 0.14, 0.20), (cx_c, ty, 0.10), mats["metal_dark"], collection, root)

    add_box(f"{lm.id}_MenuBoard", (0.28, 0.08, 0.46), (-1.22, -ld * 0.5 + 0.44, 0.23), mats["wood_dark"], collection, root, bevel=0.008, rotation=(0.14, 0.0, 0.25))
    _add_planter_box(f"{lm.id}_Planter", (-1.34, -ld * 0.5 + 0.80, 0.0), (0.34, 0.28, 0.22), mats["wood_warm"], mats["foliage_emerald"], mats["flower_coral"], collection, root)
    return _place_root(root, lm, include_plinth)


def build_bookstore(lm, mats, collection, include_plinth=True):
    """Heritage forest-green bookshop with display window packed with 3D books, awning, dormer, and open-book roof sign."""
    lw, ld = _local_dims(lm)
    root = make_empty(f"LM_{lm.id}", collection)
    if include_plinth:
        add_diorama_plinth(f"{lm.id}_Plinth", lw, ld, lm.plinth_style, mats, collection, root)

    add_box(f"{lm.id}_Paving", (lw - 0.08, ld - 0.08, 0.03), (0.0, 0.0, 0.015), mats["sidewalk_stone"], collection, root, bevel=0.01)

    bw, bd, bh = 2.34, 2.08, 2.02
    bx, by = 0.0, 0.28
    add_box(f"{lm.id}_PlinthBase", (bw + 0.08, bd + 0.08, 0.18), (bx, by, 0.09), mats["curb_granite"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_Shopfront", (bw, bd, 1.15), (bx, by, 0.18 + 0.575), mats["wood_green"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_UpperStory", (bw - 0.04, bd - 0.04, 0.87), (bx, by, 1.33 + 0.435), mats["stucco_cream"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_Cornice", (bw + 0.10, bd + 0.10, 0.09), (bx, by, 1.33), mats["wood_green"], collection, root, bevel=0.01)

    z_eave = 0.18 + bh
    add_pitched_roof(f"{lm.id}_Roof", bw, bd, 0.80, z_eave, mats["stucco_cream"], mats["roof_slate"], mats["wood_white"], collection, root, axis="X", overhang=0.14, offset_xy=(bx, by))

    # Open-book 3D roof crest emblem on front ridge.
    add_box(f"{lm.id}_BookStand", (0.72, 0.14, 0.10), (bx, by - 0.42, z_eave + 0.48), mats["wood_dark"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_BookCoverL", (0.34, 0.04, 0.34), (bx - 0.16, by - 0.44, z_eave + 0.66), mats["accent_amber"], collection, root, bevel=0.008, rotation=(0.0, 0.0, 0.32))
    add_box(f"{lm.id}_BookCoverR", (0.34, 0.04, 0.34), (bx + 0.16, by - 0.44, z_eave + 0.66), mats["accent_amber"], collection, root, bevel=0.008, rotation=(0.0, 0.0, -0.32))
    add_box(f"{lm.id}_PagesL", (0.30, 0.05, 0.30), (bx - 0.15, by - 0.46, z_eave + 0.66), mats["wood_white"], collection, root, bevel=0.005, rotation=(0.0, 0.0, 0.32))
    add_box(f"{lm.id}_PagesR", (0.30, 0.05, 0.30), (bx + 0.15, by - 0.46, z_eave + 0.66), mats["wood_white"], collection, root, bevel=0.005, rotation=(0.0, 0.0, -0.32))

    # Shop door + large display window with exterior shelf & colorful 3D books.
    add_door_assembly(f"{lm.id}_Door", (bx - 0.68, by - bd * 0.5), 0.18, 0.56, 1.00, "-Y", mats["wood_warm"], mats["wood_white"], mats["glass"], mats["metal_brass"], collection, root, step_depth=0.22)
    add_recessed_window(f"{lm.id}_DisplayWin", (bx + 0.36, by - bd * 0.5, 0.74), 1.04, 0.78, "-Y", mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root, mullions=(1, 0))
    add_box(f"{lm.id}_DisplayShelf", (0.98, 0.18, 0.06), (bx + 0.34, by - bd * 0.5 - 0.09, 0.31), mats["wood_green"], collection, root, bevel=0.01)
    book_mats = (mats["accent_red"], mats["accent_amber"], mats["accent_blue"], mats["accent_teal"], mats["brick_warm"])
    for bi in range(5):
        add_box(f"{lm.id}_DispBook_{bi}", (0.10, 0.12, 0.22 + (bi % 2) * 0.04), (bx + 0.02 + bi * 0.16, by - bd * 0.5 - 0.10, 0.45), book_mats[bi], collection, root, bevel=0.006, rotation=(0.0, 0.0, (bi - 2) * 0.08))

    add_awning(f"{lm.id}_Awning", (bx, by - bd * 0.5 - 0.02, 1.32), 2.18, 0.48, 0.20, "-Y", mats["awning_green"], mats["metal_dark"], collection, root)

    for wx in (-0.54, 0.54):
        add_recessed_window(f"{lm.id}_WinUp_{wx:.1f}", (bx + wx, by - bd * 0.5, 1.76), 0.48, 0.52, "-Y", mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root)
    for side, fdir in ((-1, "-X"), (1, "+X")):
        add_recessed_window(f"{lm.id}_WinSide_{side}", (bx + side * bw * 0.5, by, 1.74), 0.52, 0.50, fdir, mats["wood_white"], mats["glass"], mats["interior_warm"], collection, root)

    # Outdoor wooden book-browse stall cart in front right.
    add_box(f"{lm.id}_CartBase", (0.70, 0.36, 0.36), (0.58, -ld * 0.5 + 0.36, 0.18), mats["wood_warm"], collection, root, bevel=0.01)
    for bi in range(4):
        add_box(f"{lm.id}_CartBook_{bi}", (0.12, 0.16, 0.14), (0.34 + bi * 0.15, -ld * 0.5 + 0.36, 0.41), book_mats[bi], collection, root, bevel=0.005, rotation=(0.22, 0.0, 0.0))
    return _place_root(root, lm, include_plinth)


def build_bus_stop(lm, mats, collection, include_plinth=True):
    """Teal-steel & glass bus shelter, timber bench, route map box, tall bus sign, and parked mini shuttle."""
    lw, ld = _local_dims(lm)
    root = make_empty(f"LM_{lm.id}", collection)
    if include_plinth:
        # Showcase plinth slightly deeper in front so both sidewalk shelter & curb mini shuttle bus fit cleanly.
        add_diorama_plinth(f"{lm.id}_Plinth", lw + 0.45, ld + 0.95, "paving", mats, collection, root, margin=0.32)
        add_box(f"{lm.id}_AsphaltApron", (lw + 1.0, 0.96, 0.02), (0.0, -0.78, 0.01), mats["asphalt"], collection, root)
        add_box(f"{lm.id}_CurbStrip", (lw + 1.0, 0.12, 0.04), (0.0, -0.28, 0.02), mats["road_paint_yellow"], collection, root, bevel=0.008)

    # Shelter structure positioned neatly along North sidewalk edge (elevated 0.048m in overview onto raised sidewalk).
    sz_base = 0.0 if include_plinth else 0.048
    sy = 0.08
    sw = 1.48
    for px in (-sw * 0.5, 0.0, sw * 0.5):
        add_cylinder(f"{lm.id}_Post_{px:.2f}", 0.036, 0.036, 1.38, (px, sy + 0.24, sz_base + 0.69), mats["accent_teal"], collection, root, segments=10)
    add_box(f"{lm.id}_BackGlass", (sw, 0.03, 1.10), (0.0, sy + 0.24, sz_base + 0.72), mats["glass"], collection, root)
    add_box(f"{lm.id}_BackRail", (sw + 0.08, 0.06, 0.06), (0.0, sy + 0.24, sz_base + 1.30), mats["accent_teal"], collection, root, bevel=0.008)
    # Side ad/route-map light box on left end.
    add_box(f"{lm.id}_MapBox", (0.09, 0.52, 1.18), (-sw * 0.5 - 0.04, sy + 0.0, sz_base + 0.66), mats["accent_teal"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_MapGlow", (0.11, 0.38, 0.78), (-sw * 0.5 - 0.04, sy + 0.0, sz_base + 0.70), mats["interior_warm"], collection, root)

    # Cantilevered curved-style canopy roof with structural ribs.
    add_box(f"{lm.id}_Canopy", (sw + 0.24, 0.78, 0.06), (0.0, sy - 0.04, sz_base + 1.40), mats["accent_teal"], collection, root, bevel=0.015, rotation=(-0.08, 0.0, 0.0))
    for rx in (-0.55, 0.0, 0.55):
        add_box(f"{lm.id}_Rib_{rx:.2f}", (0.04, 0.70, 0.04), (rx, sy - 0.04, sz_base + 1.35), mats["metal_silver"], collection, root, rotation=(-0.08, 0.0, 0.0))

    # Timber waiting bench inside shelter.
    add_wooden_bench(f"{lm.id}_Bench", (0.10, sy + 0.04, sz_base), 0.0, mats["wood_warm"], mats["metal_dark"], collection, root)

    # Tall Bus Stop pole & circular emblem sign at right end.
    add_cylinder(f"{lm.id}_SignPole", 0.03, 0.03, 1.85, (0.96, sy - 0.16, sz_base + 0.925), mats["metal_silver"], collection, root, segments=10)
    add_cylinder(f"{lm.id}_SignDisc", 0.20, 0.20, 0.05, (0.96, sy - 0.16, sz_base + 1.82), mats["accent_teal"], collection, root, segments=20, rotation=(math.pi * 0.5, 0.0, 0.0))
    add_cylinder(f"{lm.id}_SignInner", 0.14, 0.14, 0.06, (0.96, sy - 0.16, sz_base + 1.82), mats["accent_amber"], collection, root, segments=20, rotation=(math.pi * 0.5, 0.0, 0.0))
    add_box(f"{lm.id}_Timetable", (0.12, 0.05, 0.28), (0.96, sy - 0.16, sz_base + 1.15), mats["wood_white"], collection, root, bevel=0.008)

    # Cute miniature 3D shuttle bus parked right along the curb.
    bus_y = -0.80 if include_plinth else -0.95
    bus_z = 0.0 if include_plinth else 0.016
    add_mini_vehicle(
        f"{lm.id}_Shuttle",
        (0.05, bus_y, bus_z),
        0.0,
        mats["stucco_cream"],
        mats["accent_teal"],
        mats["glass"],
        mats["tire_rubber"],
        mats["metal_silver"],
        mats["lamp_glow"],
        collection,
        root,
        kind="bus",
    )
    return _place_root(root, lm, include_plinth)


def build_market(lm, mats, collection, include_plinth=True):
    """Bustling open-air covered market hall with clerestory roof, striped stalls, and produce/bread crates."""
    lw, ld = _local_dims(lm)
    root = make_empty(f"LM_{lm.id}", collection)
    if include_plinth:
        add_diorama_plinth(f"{lm.id}_Plinth", lw, ld, lm.plinth_style, mats, collection, root)

    add_box(f"{lm.id}_Floor", (lw - 0.08, ld - 0.08, 0.04), (0.0, 0.0, 0.02), mats["sidewalk_stone"], collection, root, bevel=0.01)

    # Market hall structure recessed behind front plaza stalls.
    bw, bd, bh = 3.65, 2.35, 2.05
    bx, by = 0.0, 0.56
    add_box(f"{lm.id}_HallPlinth", (bw + 0.10, bd + 0.10, 0.16), (bx, by, 0.08), mats["curb_granite"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_HallBody", (bw, bd, bh), (bx, by, 0.16 + bh * 0.5), mats["stucco_cream"], collection, root, bevel=0.02)
    # Brick corner piers.
    for sx in (-1, 1):
        for sy in (-1, 1):
            add_box(f"{lm.id}_Pier_{sx}_{sy}", (0.28, 0.28, bh + 0.06), (bx + sx * (bw * 0.5 - 0.06), by + sy * (bd * 0.5 - 0.06), 0.16 + bh * 0.5), mats["brick_warm"], collection, root, bevel=0.015)

    z_eave = 0.16 + bh
    add_pitched_roof(f"{lm.id}_HallRoof", bw, bd, 0.86, z_eave, mats["stucco_cream"], mats["roof_terracotta"], mats["wood_dark"], collection, root, axis="X", overhang=0.18, offset_xy=(bx, by))
    # Raised clerestory monitor lantern atop roof ridge.
    add_box(f"{lm.id}_Clerestory", (1.95, 0.72, 0.42), (bx, by, z_eave + 0.92), mats["wood_white"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_ClerestoryGlass", (1.76, 0.75, 0.22), (bx, by, z_eave + 0.92), mats["interior_warm"], collection, root)
    add_pitched_roof(f"{lm.id}_ClerestoryRoof", 1.98, 0.74, 0.26, z_eave + 1.12, mats["wood_white"], mats["roof_green"], mats["wood_dark"], collection, root, axis="X", overhang=0.10, offset_xy=(bx, by), add_ribs=False)

    # Arched central market entrance, framed market sign & side windows.
    add_door_assembly(f"{lm.id}_Entry", (bx, by - bd * 0.5), 0.16, 1.05, 1.32, "-Y", mats["wood_warm"], mats["wood_dark"], mats["glass"], mats["metal_brass"], collection, root, double=True, step_depth=0.20)
    add_box(f"{lm.id}_MarketSign", (1.45, 0.08, 0.30), (bx, by - bd * 0.5 - 0.04, 1.82), mats["wood_green"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_MarketSignFrame", (1.51, 0.05, 0.36), (bx, by - bd * 0.5 - 0.02, 1.82), mats["metal_brass"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_MarketSignBarL", (0.36, 0.03, 0.06), (bx - 0.38, by - bd * 0.5 - 0.07, 1.82), mats["accent_amber"], collection, root, bevel=0.005)
    add_box(f"{lm.id}_MarketSignBarR", (0.36, 0.03, 0.06), (bx + 0.38, by - bd * 0.5 - 0.07, 1.82), mats["accent_amber"], collection, root, bevel=0.005)
    add_cylinder(f"{lm.id}_MarketSignSeal", 0.09, 0.09, 0.04, (bx, by - bd * 0.5 - 0.07, 1.82), mats["accent_red"], collection, root, segments=16, rotation=(math.pi * 0.5, 0.0, 0.0))
    for side, fdir in ((-1, "-X"), (1, "+X")):
        add_recessed_window(f"{lm.id}_WinSide_{side}", (bx + side * bw * 0.5, by, 1.15), 0.96, 0.74, fdir, mats["wood_dark"], mats["glass"], mats["interior_warm"], collection, root, mullions=(2, 1))

    # Three outdoor produce/bakery/flower stalls under alternating striped awnings on front plaza!
    stall_specs = [
        (-1.35, "awning_red", (mats["accent_red"], mats["accent_amber"], mats["foliage_lime"])),
        (0.0, "awning_amber", (mats["wood_warm"], mats["accent_amber"], mats["stucco_butter"])),
        (1.35, "awning_green", (mats["flower_coral"], mats["flower_gold"], mats["foliage_emerald"])),
    ]
    for idx, (sx, awn_key, crate_mats) in enumerate(stall_specs):
        sy = -1.28
        for px in (-0.42, 0.42):
            add_box(f"{lm.id}_StallPost_{idx}_{px:.2f}", (0.06, 0.06, 1.24), (sx + px, sy + 0.14, 0.62), mats["wood_dark"], collection, root)
        add_box(f"{lm.id}_StallHeader_{idx}", (0.94, 0.06, 0.06), (sx, sy + 0.14, 1.26), mats["wood_dark"], collection, root)
        add_box(f"{lm.id}_StallCounter_{idx}", (1.02, 0.56, 0.42), (sx, sy - 0.04, 0.21), mats["wood_warm"], collection, root, bevel=0.012)
        add_awning(f"{lm.id}_StallAwning_{idx}", (sx, sy + 0.18, 1.28), 1.08, 0.64, 0.22, "-Y", mats[awn_key], mats["metal_dark"], collection, root)
        for ci, c_mat in enumerate(crate_mats):
            cx_c = sx - 0.28 + ci * 0.28
            add_box(f"{lm.id}_Crate_{idx}_{ci}", (0.23, 0.26, 0.14), (cx_c, sy - 0.08, 0.48), mats["wood_dark"], collection, root, bevel=0.008, rotation=(0.18, 0.0, 0.0))
            for g in range(3):
                add_box(f"{lm.id}_Goods_{idx}_{ci}_{g}", (0.08, 0.08, 0.08), (cx_c - 0.05 + g * 0.05, sy - 0.09, 0.56), c_mat, collection, root, bevel=0.02)

    return _place_root(root, lm, include_plinth)


def build_supermarket(lm, mats, collection, include_plinth=True):
    """Bright modern supermarket with cedar slat accent, teal/amber canopy, sliding doors, and shopping carts."""
    lw, ld = _local_dims(lm)
    root = make_empty(f"LM_{lm.id}", collection)
    if include_plinth:
        add_diorama_plinth(f"{lm.id}_Plinth", lw, ld, lm.plinth_style, mats, collection, root)

    add_box(f"{lm.id}_Plaza", (lw - 0.08, ld - 0.08, 0.03), (0.0, 0.0, 0.015), mats["sidewalk_stone"], collection, root, bevel=0.01)

    bw, bd, bh = 3.85, 2.75, 2.25
    bx, by = 0.0, 0.36
    add_box(f"{lm.id}_Base", (bw + 0.08, bd + 0.08, 0.16), (bx, by, 0.08), mats["curb_granite"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_MainBox", (bw, bd, bh), (bx, by, 0.16 + bh * 0.5), mats["stucco_white"], collection, root, bevel=0.02)
    # Modern teal parapet cap & recessed flat roof deck with skylights.
    add_box(f"{lm.id}_Parapet", (bw + 0.12, bd + 0.12, 0.18), (bx, by, 0.16 + bh + 0.08), mats["accent_teal"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_RoofDeck", (bw - 0.14, bd - 0.14, 0.06), (bx, by, 0.16 + bh + 0.04), mats["roof_slate"], collection, root)
    for sx in (-0.95, 0.95):
        add_box(f"{lm.id}_Skylight_{sx:.2f}", (1.15, 0.85, 0.18), (bx + sx, by, 0.16 + bh + 0.14), mats["glass"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_HVAC", (0.72, 0.56, 0.34), (bx, by + 0.58, 0.16 + bh + 0.22), mats["metal_silver"], collection, root, bevel=0.02)

    # Cedar wood vertical slat fascia along upper front facade.
    for i in range(15):
        slat_x = bx - 1.68 + i * 0.24
        add_box(f"{lm.id}_Slat_{i}", (0.10, 0.06, 0.56), (slat_x, by - bd * 0.5 - 0.03, 1.98), mats["wood_warm"], collection, root, bevel=0.008)

    # Bold cantilevered entrance canopy with framed amber/white sign plaque.
    add_box(f"{lm.id}_Canopy", (2.68, 0.86, 0.16), (bx - 0.30, by - bd * 0.5 - 0.42, 1.56), mats["accent_teal"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_CanopyAmber", (2.72, 0.90, 0.05), (bx - 0.30, by - bd * 0.5 - 0.42, 1.64), mats["accent_amber"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_SignBlock", (1.62, 0.10, 0.34), (bx - 0.30, by - bd * 0.5 - 0.82, 1.82), mats["accent_teal"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_SignFrame", (1.68, 0.07, 0.40), (bx - 0.30, by - bd * 0.5 - 0.80, 1.82), mats["accent_amber"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_SignBarL", (0.42, 0.03, 0.07), (bx - 0.72, by - bd * 0.5 - 0.87, 1.82), mats["wood_white"], collection, root, bevel=0.005)
    add_box(f"{lm.id}_SignBarR", (0.42, 0.03, 0.07), (bx + 0.12, by - bd * 0.5 - 0.87, 1.82), mats["wood_white"], collection, root, bevel=0.005)
    add_cylinder(f"{lm.id}_SignLeaf", 0.10, 0.10, 0.04, (bx - 0.30, by - bd * 0.5 - 0.87, 1.82), mats["foliage_lime"], collection, root, segments=16, rotation=(math.pi * 0.5, 0.0, 0.0))

    # Wide glazed automatic sliding doors + curtain wall bays.
    add_door_assembly(f"{lm.id}_SlidingDoors", (bx - 0.30, by - bd * 0.5), 0.16, 1.18, 1.24, "-Y", mats["glass"], mats["metal_silver"], mats["glass"], mats["metal_silver"], collection, root, double=True, step_depth=0.14)
    add_recessed_window(f"{lm.id}_FrontGlassL", (bx - 1.38, by - bd * 0.5, 0.82), 0.68, 1.05, "-Y", mats["metal_dark"], mats["glass"], mats["interior_warm"], collection, root)
    add_recessed_window(f"{lm.id}_FrontGlassR", (bx + 1.05, by - bd * 0.5, 0.82), 1.25, 1.05, "-Y", mats["metal_dark"], mats["glass"], mats["interior_warm"], collection, root, mullions=(2, 0))
    for side, fdir in ((-1, "-X"), (1, "+X")):
        add_recessed_window(f"{lm.id}_SideWin_{side}", (bx + side * bw * 0.5, by, 1.22), 1.35, 0.65, fdir, mats["metal_dark"], mats["glass"], mats["interior_warm"], collection, root, mullions=(2, 0))

    # Shopping cart corral with vertical posts + 3 nested 3D metallic shopping carts in front right plaza.
    cx_cor, cy_cor = 1.15, -ld * 0.5 + 0.56
    add_box(f"{lm.id}_CorralRailL", (0.04, 0.68, 0.04), (cx_cor - 0.36, cy_cor, 0.34), mats["accent_teal"], collection, root)
    add_box(f"{lm.id}_CorralRailR", (0.04, 0.68, 0.04), (cx_cor + 0.36, cy_cor, 0.34), mats["accent_teal"], collection, root)
    add_box(f"{lm.id}_CorralRailB", (0.76, 0.04, 0.04), (cx_cor, cy_cor + 0.32, 0.34), mats["accent_teal"], collection, root)
    for sx_c in (-0.36, 0.36):
        for sy_c in (-0.32, 0.32):
            add_cylinder(f"{lm.id}_CorralPost_{sx_c:.2f}_{sy_c:.2f}", 0.025, 0.025, 0.36, (cx_cor + sx_c, cy_cor + sy_c, 0.18), mats["accent_teal"], collection, root, segments=8)
    for ci in range(3):
        cy_c = cy_cor - 0.14 + ci * 0.15
        add_box(f"{lm.id}_CartBasket_{ci}", (0.34, 0.24, 0.22), (cx_cor, cy_c, 0.24), mats["metal_silver"], collection, root, bevel=0.01)
        add_box(f"{lm.id}_CartHandle_{ci}", (0.36, 0.04, 0.04), (cx_cor, cy_c + 0.12, 0.38), mats["accent_red"], collection, root, bevel=0.008)
        for wx in (-0.12, 0.12):
            add_cylinder(f"{lm.id}_CartWheel_{ci}_{wx:.2f}", 0.035, 0.035, 0.03, (cx_cor + wx, cy_c, 0.04), mats["tire_rubber"], collection, root, segments=10, rotation=(0.0, math.pi * 0.5, 0.0))

    _add_planter_box(f"{lm.id}_PlanterL", (-1.45, -ld * 0.5 + 0.42, 0.0), (0.64, 0.34, 0.24), mats["curb_granite"], mats["foliage_emerald"], mats["flower_gold"], collection, root)
    return _place_root(root, lm, include_plinth)


def build_hospital(lm, mats, collection, include_plinth=True):
    """Clean civic medical clinic/hospital with red 3D Cross emblems, ambulance portico, and mini ambulance."""
    lw, ld = _local_dims(lm)
    root = make_empty(f"LM_{lm.id}", collection)
    if include_plinth:
        add_diorama_plinth(f"{lm.id}_Plinth", lw, ld, lm.plinth_style, mats, collection, root)

    add_box(f"{lm.id}_Ground", (lw - 0.08, ld - 0.08, 0.03), (0.0, 0.0, 0.015), mats["sidewalk_stone"], collection, root, bevel=0.01)
    # Ambulance drop-off lane paving on front left inside footprint.
    add_box(f"{lm.id}_DriveBay", (1.68, 1.35, 0.035), (-1.15, -ld * 0.5 + 0.72, 0.02), mats["asphalt"], collection, root)

    bw, bd, bh = 3.95, 2.55, 2.38
    bx, by = 0.05, 0.48
    add_box(f"{lm.id}_Base", (bw + 0.08, bd + 0.08, 0.18), (bx, by, 0.09), mats["curb_granite"], collection, root, bevel=0.015)
    add_box(f"{lm.id}_MainWing", (bw, bd, bh), (bx, by, 0.18 + bh * 0.5), mats["stucco_white"], collection, root, bevel=0.025)
    add_box(f"{lm.id}_TealBand", (bw + 0.06, bd + 0.06, 0.14), (bx, by, 1.38), mats["accent_teal"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_Parapet", (bw + 0.10, bd + 0.10, 0.14), (bx, by, 0.18 + bh + 0.06), mats["curb_granite"], collection, root, bevel=0.015)

    # Recessed upper penthouse + rooftop red Cross helipad cleanly clear of penthouse wall.
    add_box(f"{lm.id}_Penthouse", (2.10, 1.55, 0.78), (bx + 0.42, by + 0.12, 0.18 + bh + 0.39), mats["stucco_white"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_PentCap", (2.20, 1.65, 0.10), (bx + 0.42, by + 0.12, 0.18 + bh + 0.82), mats["accent_teal"], collection, root, bevel=0.015)
    add_cylinder(f"{lm.id}_HelipadDisc", 0.52, 0.52, 0.05, (bx - 1.26, by + 0.05, 0.18 + bh + 0.12), mats["curb_granite"], collection, root, segments=24)
    add_box(f"{lm.id}_HeliCrossV", (0.16, 0.58, 0.06), (bx - 1.26, by + 0.05, 0.18 + bh + 0.15), mats["accent_red"], collection, root)
    add_box(f"{lm.id}_HeliCrossH", (0.58, 0.16, 0.06), (bx - 1.26, by + 0.05, 0.18 + bh + 0.15), mats["accent_red"], collection, root)

    # Prominent 3D Red Cross emblem on front West facade!
    cross_x, cross_y, cross_z = bx + 0.65, by - bd * 0.5 - 0.05, 2.02
    add_box(f"{lm.id}_CrossPlaque", (0.76, 0.06, 0.76), (cross_x, cross_y + 0.02, cross_z), mats["wood_white"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_CrossV", (0.20, 0.08, 0.54), (cross_x, cross_y - 0.02, cross_z), mats["accent_red"], collection, root, bevel=0.01)
    add_box(f"{lm.id}_CrossH", (0.54, 0.08, 0.20), (cross_x, cross_y - 0.02, cross_z), mats["accent_red"], collection, root, bevel=0.01)

    # Covered ambulance portico extending forward on left side (columns clear ambulance bumper completely).
    add_box(f"{lm.id}_PorticoRoof", (1.92, 1.12, 0.12), (-1.15, by - bd * 0.5 - 0.55, 1.38), mats["stucco_white"], collection, root, bevel=0.02)
    add_box(f"{lm.id}_PorticoTrim", (1.96, 1.16, 0.06), (-1.15, by - bd * 0.5 - 0.55, 1.46), mats["accent_red"], collection, root, bevel=0.01)
    for px in (-2.02, -0.28):
        add_cylinder(f"{lm.id}_PorticoCol_{px:.2f}", 0.065, 0.065, 1.34, (px, by - bd * 0.5 - 1.02, 0.67), mats["metal_silver"], collection, root, segments=12)

    # Hospital double glass entrance doors & ribbon windows.
    add_door_assembly(f"{lm.id}_Doors", (bx + 0.65, by - bd * 0.5), 0.18, 0.96, 1.12, "-Y", mats["glass"], mats["metal_silver"], mats["glass"], mats["metal_silver"], collection, root, double=True, step_depth=0.24)
    add_recessed_window(f"{lm.id}_Win1L", (bx - 0.95, by - bd * 0.5, 0.82), 1.10, 0.68, "-Y", mats["metal_silver"], mats["glass"], mats["interior_warm"], collection, root, mullions=(2, 0))
    add_recessed_window(f"{lm.id}_Win2L", (bx - 0.95, by - bd * 0.5, 1.98), 1.35, 0.64, "-Y", mats["metal_silver"], mats["glass"], mats["interior_warm"], collection, root, mullions=(2, 0))
    add_recessed_window(f"{lm.id}_Win2R", (bx + 1.52, by - bd * 0.5, 1.98), 0.65, 0.64, "-Y", mats["metal_silver"], mats["glass"], mats["interior_warm"], collection, root)
    for side, fdir in ((-1, "-X"), (1, "+X")):
        add_recessed_window(f"{lm.id}_SideWin_{side}", (bx + side * bw * 0.5, by, 1.98), 1.35, 0.64, fdir, mats["metal_silver"], mats["glass"], mats["interior_warm"], collection, root, mullions=(2, 0))

    # Cute miniature 3D ambulance parked at portico drive bay.
    add_mini_vehicle(
        f"{lm.id}_Ambulance",
        (-1.15, -ld * 0.5 + 0.66, 0.0),
        0.0,
        mats["wood_white"],
        mats["accent_red"],
        mats["glass"],
        mats["tire_rubber"],
        mats["metal_silver"],
        mats["lamp_glow"],
        collection,
        root,
        kind="ambulance",
    )
    _add_planter_box(f"{lm.id}_PlanterR", (1.62, -ld * 0.5 + 0.45, 0.0), (0.64, 0.34, 0.24), mats["curb_granite"], mats["foliage_emerald"], mats["flower_coral"], collection, root)
    return _place_root(root, lm, include_plinth)


BUILDERS = {
    "my-house": build_my_house,
    "school": build_school,
    "park": build_park,
    "post-office": build_post_office,
    "restaurant": build_restaurant,
    "bookstore": build_bookstore,
    "bus-stop": build_bus_stop,
    "market": build_market,
    "supermarket": build_supermarket,
    "hospital": build_hospital,
}
