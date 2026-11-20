"""Reusable 3D micro-joinery, botanical, and prop builders using bmesh."""

import math
import bmesh
import bpy
from mathutils import Euler, Matrix, Vector


def link_obj(obj, collection, parent=None):
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    if parent is not None:
        obj.parent = parent
    return obj


def make_empty(name, collection, parent=None, location=(0.0, 0.0, 0.0), rot_z=0.0):
    empty = bpy.data.objects.new(name, None)
    empty.location = location
    empty.rotation_euler = (0.0, 0.0, rot_z)
    link_obj(empty, collection, parent)
    return empty


def _finish_bmesh(bm, name, mat, collection, parent=None, location=(0.0, 0.0, 0.0), rotation=(0.0, 0.0, 0.0), smooth=False):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    if smooth:
        for poly in mesh.polygons:
            poly.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    if mat is not None:
        obj.data.materials.append(mat)
    link_obj(obj, collection, parent)
    return obj


def add_box(
    name,
    size,
    center,
    mat,
    collection,
    parent=None,
    bevel=0.0,
    bevel_segments=2,
    rotation=(0.0, 0.0, 0.0),
):
    """Create a box with optional crisp chamfer bevel."""
    bm = bmesh.new()
    sx, sy, sz = size
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(sx, sy, sz), verts=bm.verts)
    if bevel > 0.0:
        b = min(bevel, min(sx, sy, sz) * 0.25)
        bmesh.ops.bevel(
            bm,
            geom=list(bm.edges),
            offset=b,
            segments=bevel_segments,
            profile=0.5,
            affect="EDGES",
            clamp_overlap=True,
        )
    return _finish_bmesh(bm, name, mat, collection, parent, location=center, rotation=rotation)


def add_cylinder(
    name,
    radius_bottom,
    radius_top,
    height,
    center,
    mat,
    collection,
    parent=None,
    segments=16,
    bevel=0.0,
    rotation=(0.0, 0.0, 0.0),
    smooth=True,
):
    bm = bmesh.new()
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=segments,
        radius1=radius_bottom,
        radius2=radius_top,
        depth=height,
    )
    if bevel > 0.0:
        cap_edges = [e for e in bm.edges if abs(e.verts[0].co.z - e.verts[1].co.z) < 1e-4]
        bmesh.ops.bevel(
            bm,
            geom=cap_edges,
            offset=min(bevel, min(radius_bottom, radius_top, height) * 0.22),
            segments=2,
            affect="EDGES",
            clamp_overlap=True,
        )
    return _finish_bmesh(bm, name, mat, collection, parent, location=center, rotation=rotation, smooth=smooth)


def add_gable_prism(
    name,
    width,
    depth,
    height,
    z_base,
    mat,
    collection,
    parent=None,
    axis="X",
    offset_xy=(0.0, 0.0),
):
    """Triangular gable prism sitting at z_base; ridge runs along axis ('X' or 'Y')."""
    bm = bmesh.new()
    hw, hd = width * 0.5, depth * 0.5
    ox, oy = offset_xy
    if axis == "X":
        # Ridge runs East-West (X), slopes face South (-Y) and North (+Y).
        verts = [
            bm.verts.new((-hw, -hd, 0.0)),
            bm.verts.new((hw, -hd, 0.0)),
            bm.verts.new((hw, hd, 0.0)),
            bm.verts.new((-hw, hd, 0.0)),
            bm.verts.new((-hw, 0.0, height)),
            bm.verts.new((hw, 0.0, height)),
        ]
    else:
        # Ridge runs North-South (Y), slopes face West (-X) and East (+X).
        verts = [
            bm.verts.new((-hw, -hd, 0.0)),
            bm.verts.new((hw, -hd, 0.0)),
            bm.verts.new((hw, hd, 0.0)),
            bm.verts.new((-hw, hd, 0.0)),
            bm.verts.new((0.0, -hd, height)),
            bm.verts.new((0.0, hd, height)),
        ]
    bm.faces.new((verts[0], verts[1], verts[5], verts[4]))
    bm.faces.new((verts[2], verts[3], verts[4], verts[5]))
    bm.faces.new((verts[0], verts[4], verts[3]))
    bm.faces.new((verts[1], verts[2], verts[5]))
    bm.faces.new((verts[0], verts[3], verts[2], verts[1]))
    return _finish_bmesh(bm, name, mat, collection, parent, location=(ox, oy, z_base))


def add_pitched_roof(
    prefix,
    width,
    depth,
    ridge_height,
    z_eave,
    wall_mat,
    roof_mat,
    trim_mat,
    collection,
    parent=None,
    axis="X",
    overhang=0.14,
    offset_xy=(0.0, 0.0),
    add_ribs=True,
):
    """Build complete pitched roof: gable wall core, sloped roof slabs, fascia, ridge cap, and tile ribs."""
    ox, oy = offset_xy
    add_gable_prism(
        f"{prefix}_GableWall",
        width - 0.02,
        depth - 0.02,
        ridge_height,
        z_eave,
        wall_mat,
        collection,
        parent,
        axis=axis,
        offset_xy=(ox, oy),
    )

    span = depth if axis == "X" else width
    run = width if axis == "X" else depth
    half_span = span * 0.5 + overhang
    slope_angle = math.atan2(ridge_height, span * 0.5)
    slope_len = math.hypot(span * 0.5 + overhang, ridge_height * (1.0 + overhang / max(0.1, span * 0.5)))
    roof_thick = 0.08
    z_ridge = z_eave + ridge_height

    for side in (-1, 1):
        mid_off = side * half_span * 0.5
        mid_z = z_ridge - (half_span * 0.5) * math.tan(slope_angle) + roof_thick * 0.45
        if axis == "X":
            size = (run + overhang * 2.0, slope_len, roof_thick)
            loc = (ox, oy + mid_off, mid_z)
            rot = (-side * slope_angle, 0.0, 0.0)
        else:
            size = (slope_len, run + overhang * 2.0, roof_thick)
            loc = (ox + mid_off, oy, mid_z)
            rot = (0.0, side * slope_angle, 0.0)

        add_box(f"{prefix}_Slope_{side}", size, loc, roof_mat, collection, parent, bevel=0.012, rotation=rot)

        # Raised standing-seam / tile batten ribs across the roof slope.
        if add_ribs:
            rib_count = max(4, int(run / 0.36))
            for i in range(rib_count):
                t = -0.5 * (run + overhang * 1.4) + (i + 0.5) * ((run + overhang * 1.4) / rib_count)
                if axis == "X":
                    rloc = (ox + t, oy + mid_off, mid_z + 0.042)
                    rsize = (0.035, slope_len * 0.98, 0.032)
                else:
                    rloc = (ox + mid_off, oy + t, mid_z + 0.042)
                    rsize = (slope_len * 0.98, 0.035, 0.032)
                add_box(f"{prefix}_Rib_{side}_{i}", rsize, rloc, roof_mat, collection, parent, bevel=0.006, rotation=rot)

    # Ridge cap beam and eave fascia trim.
    if axis == "X":
        add_box(f"{prefix}_RidgeCap", (run + overhang * 2.1, 0.14, 0.10), (ox, oy, z_ridge + 0.05), trim_mat, collection, parent, bevel=0.015)
        for side in (-1, 1):
            add_box(
                f"{prefix}_Fascia_{side}",
                (run + overhang * 2.0, 0.05, 0.10),
                (ox, oy + side * (span * 0.5 + overhang), z_eave - overhang * math.tan(slope_angle)),
                trim_mat,
                collection,
                parent,
                bevel=0.008,
            )
    else:
        add_box(f"{prefix}_RidgeCap", (0.14, run + overhang * 2.1, 0.10), (ox, oy, z_ridge + 0.05), trim_mat, collection, parent, bevel=0.015)
        for side in (-1, 1):
            add_box(
                f"{prefix}_Fascia_{side}",
                (0.05, run + overhang * 2.0, 0.10),
                (ox + side * (span * 0.5 + overhang), oy, z_eave - overhang * math.tan(slope_angle)),
                trim_mat,
                collection,
                parent,
                bevel=0.008,
            )


def add_recessed_window(
    prefix,
    center,
    w,
    h,
    face_dir,
    frame_mat,
    glass_mat,
    backing_mat,
    collection,
    parent=None,
    mullions=(1, 1),
    sill_mat=None,
    shutter_mat=None,
):
    """Build a 3D framed window with recessed glass, sill, lintel, mullions, and optional shutters."""
    # face_dir in ('-Y', '+Y', '-X', '+X')
    rot_map = {"-Y": 0.0, "+X": math.pi * 0.5, "+Y": math.pi, "-X": -math.pi * 0.5}
    rz = rot_map[face_dir]
    win_root = make_empty(prefix, collection, parent, location=center, rot_z=rz)

    frame_t = 0.055
    frame_d = 0.09
    # Outer perimeter frame stiles & rails.
    add_box(f"{prefix}_Top", (w, frame_d, frame_t), (0.0, -0.02, h * 0.5 - frame_t * 0.5), frame_mat, collection, win_root, bevel=0.006)
    add_box(f"{prefix}_Bot", (w, frame_d, frame_t), (0.0, -0.02, -h * 0.5 + frame_t * 0.5), frame_mat, collection, win_root, bevel=0.006)
    add_box(f"{prefix}_Left", (frame_t, frame_d, h), (-w * 0.5 + frame_t * 0.5, -0.02, 0.0), frame_mat, collection, win_root, bevel=0.006)
    add_box(f"{prefix}_Right", (frame_t, frame_d, h), (w * 0.5 - frame_t * 0.5, -0.02, 0.0), frame_mat, collection, win_root, bevel=0.006)

    # Stone/wood projecting sill & header lintel.
    s_mat = sill_mat or frame_mat
    add_box(f"{prefix}_Sill", (w + 0.12, 0.13, 0.06), (0.0, -0.05, -h * 0.5 - 0.015), s_mat, collection, win_root, bevel=0.01)
    add_box(f"{prefix}_Lintel", (w + 0.10, 0.10, 0.07), (0.0, -0.03, h * 0.5 + 0.025), s_mat, collection, win_root, bevel=0.008)

    # Recessed glass pane and warm interior backing plane.
    add_box(f"{prefix}_Glass", (w - frame_t * 1.4, 0.02, h - frame_t * 1.4), (0.0, 0.0, 0.0), glass_mat, collection, win_root)
    add_box(f"{prefix}_Interior", (w - frame_t * 1.6, 0.02, h - frame_t * 1.6), (0.0, 0.035, 0.0), backing_mat, collection, win_root)

    # Mullions (vertical, horizontal).
    nx, nz = mullions
    for i in range(1, nx + 1):
        mx = -w * 0.5 + (w * i) / (nx + 1)
        add_box(f"{prefix}_VMul_{i}", (0.028, 0.04, h - frame_t), (mx, -0.02, 0.0), frame_mat, collection, win_root)
    for j in range(1, nz + 1):
        mz = -h * 0.5 + (h * j) / (nz + 1)
        add_box(f"{prefix}_HMul_{j}", (w - frame_t, 0.04, 0.028), (0.0, -0.02, mz), frame_mat, collection, win_root)

    if shutter_mat is not None:
        sw = min(0.24, w * 0.34)
        for side in (-1, 1):
            add_box(
                f"{prefix}_Shutter_{side}",
                (sw, 0.045, h),
                (side * (w * 0.5 + sw * 0.5 + 0.03), -0.03, 0.0),
                shutter_mat,
                collection,
                win_root,
                bevel=0.006,
            )
    return win_root


def add_door_assembly(
    prefix,
    center_xy,
    z_floor,
    w,
    h,
    face_dir,
    door_mat,
    frame_mat,
    glass_mat,
    metal_mat,
    collection,
    parent=None,
    double=False,
    step_depth=0.28,
):
    """Build a framed entrance door with stone step, glass transom/panes, and brass handle."""
    rot_map = {"-Y": 0.0, "+X": math.pi * 0.5, "+Y": math.pi, "-X": -math.pi * 0.5}
    d_root = make_empty(prefix, collection, parent, location=(center_xy[0], center_xy[1], z_floor), rot_z=rot_map[face_dir])

    # Threshold step(s) staying cleanly compact.
    if step_depth > 0.0:
        add_box(f"{prefix}_Step", (w + 0.32, step_depth, 0.12), (0.0, -step_depth * 0.5, 0.06), frame_mat, collection, d_root, bevel=0.015)

    z0 = 0.12 if step_depth > 0.0 else 0.0
    add_box(f"{prefix}_FrameTop", (w + 0.14, 0.12, 0.08), (0.0, -0.02, z0 + h + 0.02), frame_mat, collection, d_root, bevel=0.008)
    for side in (-1, 1):
        add_box(f"{prefix}_FrameSide_{side}", (0.08, 0.12, h), (side * (w * 0.5 + 0.03), -0.02, z0 + h * 0.5), frame_mat, collection, d_root, bevel=0.008)

    if double:
        leaf_w = w * 0.48
        for side in (-1, 1):
            lx = side * (leaf_w * 0.5 + 0.01)
            add_box(f"{prefix}_Leaf_{side}", (leaf_w, 0.06, h), (lx, 0.0, z0 + h * 0.5), door_mat, collection, d_root, bevel=0.006)
            add_box(f"{prefix}_Glass_{side}", (leaf_w * 0.6, 0.075, h * 0.48), (lx, -0.005, z0 + h * 0.62), glass_mat, collection, d_root)
            add_box(f"{prefix}_Handle_{side}", (0.025, 0.06, 0.18), (side * 0.06, -0.045, z0 + h * 0.46), metal_mat, collection, d_root, bevel=0.004)
    else:
        add_box(f"{prefix}_Leaf", (w, 0.06, h), (0.0, 0.0, z0 + h * 0.5), door_mat, collection, d_root, bevel=0.006)
        add_box(f"{prefix}_Glass", (w * 0.54, 0.075, h * 0.34), (0.0, -0.005, z0 + h * 0.68), glass_mat, collection, d_root)
        add_cylinder(f"{prefix}_Knob", 0.03, 0.03, 0.06, (w * 0.34, -0.05, z0 + h * 0.45), metal_mat, collection, d_root, segments=12, rotation=(math.pi * 0.5, 0.0, 0.0))
    return d_root


def add_awning(
    prefix,
    center,
    width,
    proj,
    drop,
    face_dir,
    cloth_mat,
    metal_mat,
    collection,
    parent=None,
):
    """Build sloped striped cloth shop awning with scalloped valance and metal brackets."""
    rot_map = {"-Y": 0.0, "+X": math.pi * 0.5, "+Y": math.pi, "-X": -math.pi * 0.5}
    a_root = make_empty(prefix, collection, parent, location=center, rot_z=rot_map[face_dir])
    slope_len = math.hypot(proj, drop)
    angle = math.atan2(drop, proj)
    add_box(
        f"{prefix}_Slope",
        (width, slope_len, 0.045),
        (0.0, -proj * 0.5, -drop * 0.5),
        cloth_mat,
        collection,
        a_root,
        bevel=0.008,
        rotation=(angle, 0.0, 0.0),
    )
    add_box(
        f"{prefix}_Valance",
        (width, 0.035, 0.14),
        (0.0, -proj, -drop - 0.06),
        cloth_mat,
        collection,
        a_root,
        bevel=0.006,
    )
    for side in (-1, 1):
        add_box(
            f"{prefix}_Arm_{side}",
            (0.035, proj * 0.92, 0.035),
            (side * (width * 0.46), -proj * 0.46, -drop - 0.02),
            metal_mat,
            collection,
            a_root,
        )
    return a_root


def add_diorama_plinth(prefix, width, depth, style, mats, collection, parent=None, margin=0.38):
    """Crisp architectural display plinth whose top surface sits exactly at Z = 0.0."""
    pw = width + margin * 2.0
    pd = depth + margin * 2.0
    # Dark walnut showcase base slab underneath.
    add_box(f"{prefix}_Base", (pw + 0.18, pd + 0.18, 0.18), (0.0, 0.0, -0.15), mats["plinth_walnut"], collection, parent, bevel=0.025)
    # Stone curb lip.
    add_box(f"{prefix}_Curb", (pw + 0.06, pd + 0.06, 0.08), (0.0, 0.0, -0.05), mats["curb_granite"], collection, parent, bevel=0.015)
    # Ground top surface (z=0.0).
    top_mat = mats["grass_lush"] if style == "lawn" else mats["sidewalk_stone"]
    add_box(f"{prefix}_Top", (pw, pd, 0.06), (0.0, 0.0, -0.03), top_mat, collection, parent, bevel=0.012)


def add_multi_branch_tree(
    prefix,
    base_pos,
    height,
    bark_mat,
    leaf_mat,
    collection,
    parent=None,
    seed=1,
    crown_radius=0.62,
):
    """Build organic multi-branch tree with tapered trunk, flared boughs, and displaced leaf clusters."""
    t_root = make_empty(prefix, collection, parent, location=base_pos)
    trunk_h = height * 0.56
    add_cylinder(f"{prefix}_Trunk", 0.11, 0.055, trunk_h, (0.0, 0.0, trunk_h * 0.5), bark_mat, collection, t_root, segments=10)

    # Flared root buttresses at base.
    for k in range(3):
        ang = seed * 1.3 + k * (2.094)
        add_box(
            f"{prefix}_Root_{k}",
            (0.08, 0.18, 0.14),
            (math.cos(ang) * 0.08, math.sin(ang) * 0.08, 0.05),
            bark_mat,
            collection,
            t_root,
            bevel=0.02,
            rotation=(0.25 * math.sin(ang), -0.25 * math.cos(ang), ang),
        )

    # Secondary branches radiating upward + irregular foliage clusters.
    clusters = []
    for i in range(4):
        ang = seed * 0.9 + i * 1.57 + (i % 2) * 0.28
        tilt = 0.55 + 0.12 * ((i + seed) % 3)
        blen = height * 0.34
        bx = math.cos(ang) * blen * 0.45
        by = math.sin(ang) * blen * 0.45
        bz = trunk_h * 0.85 + blen * 0.40
        add_cylinder(
            f"{prefix}_Branch_{i}",
            0.048,
            0.022,
            blen,
            (bx, by, bz),
            bark_mat,
            collection,
            t_root,
            segments=8,
            rotation=(-math.sin(ang) * tilt, math.cos(ang) * tilt, 0.0),
        )
        clusters.append((
            math.cos(ang) * crown_radius * 0.62,
            math.sin(ang) * crown_radius * 0.62,
            trunk_h + blen * 0.58 + 0.12 * ((i + seed) % 2),
            crown_radius * (0.64 + 0.08 * ((i + seed) % 2)),
        ))

    # Top central crown cluster + lower accent tufts.
    clusters.append((0.0, 0.0, height * 0.88, crown_radius * 0.78))
    clusters.append((0.15 * math.cos(seed), 0.15 * math.sin(seed), height * 0.74, crown_radius * 0.65))

    for idx, (cx, cy, cz, rad) in enumerate(clusters):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=3, radius=rad)
        for v in bm.verts:
            p = v.co
            wobble = (
                1.0
                + 0.18 * math.sin(p.x * 8.3 + seed * 1.7 + idx)
                + 0.15 * math.cos(p.y * 9.1 - seed * 2.1)
                + 0.12 * math.sin(p.z * 7.7 + idx * 1.9)
            )
            v.co.x *= wobble
            v.co.y *= wobble
            v.co.z *= wobble * 0.84
        _finish_bmesh(bm, f"{prefix}_Crown_{idx}", leaf_mat, collection, t_root, location=(cx, cy, cz), smooth=False)
    return t_root


def add_hedge_bush(prefix, center, size, leaf_mat, collection, parent=None, seed=1):
    """Organic multi-puff shrub/hedge (not a flat box or smooth sphere)."""
    bm = bmesh.new()
    sx, sy, sz = size
    steps = max(3, int(max(sx, sy) / 0.25))
    for i in range(steps):
        t = -0.5 + (i + 0.5) / steps
        px = t * (sx * 0.66) if sx >= sy else 0.0
        py = t * (sy * 0.66) if sy > sx else 0.0
        r = min(sx, sy, sz) * (0.48 + 0.08 * ((i + seed) % 2))
        sub = bmesh.new()
        bmesh.ops.create_icosphere(sub, subdivisions=2, radius=r)
        for v in sub.verts:
            p = v.co
            w = 1.0 + 0.20 * math.sin(p.x * 11.0 + i + seed) + 0.16 * math.cos(p.y * 10.5 - seed)
            v.co.x = p.x * w + px
            v.co.y = p.y * w + py
            v.co.z = p.z * w * 0.88 + sz * 0.44
        me = bpy.data.meshes.new("_tmp")
        sub.to_mesh(me)
        sub.free()
        bm.from_mesh(me)
        bpy.data.meshes.remove(me)
    return _finish_bmesh(bm, prefix, leaf_mat, collection, parent, location=center, smooth=False)


def add_wooden_bench(prefix, center, rot_z, wood_mat, iron_mat, collection, parent=None):
    """Slatted wood & cast-iron park/bus bench."""
    b_root = make_empty(prefix, collection, parent, location=center, rot_z=rot_z)
    for side in (-1, 1):
        lx = side * 0.36
        add_box(f"{prefix}_LegF_{side}", (0.04, 0.04, 0.24), (lx, -0.14, 0.12), iron_mat, collection, b_root, bevel=0.005)
        add_box(f"{prefix}_LegB_{side}", (0.04, 0.04, 0.44), (lx, 0.14, 0.22), iron_mat, collection, b_root, bevel=0.005)
        add_box(f"{prefix}_Arm_{side}", (0.045, 0.34, 0.035), (lx, 0.0, 0.32), iron_mat, collection, b_root, bevel=0.005)
    for s in range(3):
        add_box(f"{prefix}_Seat_{s}", (0.86, 0.08, 0.03), (0.0, -0.10 + s * 0.10, 0.23), wood_mat, collection, b_root, bevel=0.005)
    for s in range(2):
        add_box(f"{prefix}_Back_{s}", (0.86, 0.03, 0.09), (0.0, 0.14, 0.32 + s * 0.11), wood_mat, collection, b_root, bevel=0.005)
    return b_root


def add_streetlamp(prefix, base_pos, metal_mat, glow_mat, collection, parent=None, height=2.25):
    """Architectural black-iron streetlamp with warm glowing lantern head."""
    l_root = make_empty(prefix, collection, parent, location=base_pos)
    add_cylinder(f"{prefix}_Base", 0.10, 0.07, 0.32, (0.0, 0.0, 0.16), metal_mat, collection, l_root, segments=10, bevel=0.01)
    add_cylinder(f"{prefix}_Pole", 0.04, 0.03, height - 0.5, (0.0, 0.0, 0.32 + (height - 0.5) * 0.5), metal_mat, collection, l_root, segments=10)
    add_cylinder(f"{prefix}_Lantern", 0.09, 0.12, 0.22, (0.0, 0.0, height - 0.12), glow_mat, collection, l_root, segments=8)
    add_cylinder(f"{prefix}_Cap", 0.15, 0.02, 0.10, (0.0, 0.0, height + 0.04), metal_mat, collection, l_root, segments=8)
    return l_root


def add_mini_vehicle(prefix, center, rot_z, body_mat, stripe_mat, glass_mat, tire_mat, metal_mat, glow_mat, collection, parent=None, kind="bus"):
    """Detailed miniature 3D neighbourhood shuttle bus or ambulance."""
    v_root = make_empty(prefix, collection, parent, location=center, rot_z=rot_z)
    length, width, height = (1.55, 0.66, 0.72) if kind == "bus" else (1.38, 0.64, 0.68)

    # Lower chassis & upper cabin.
    add_box(f"{prefix}_Chassis", (length, width, height * 0.52), (0.0, 0.0, 0.12 + height * 0.26), body_mat, collection, v_root, bevel=0.04)
    add_box(f"{prefix}_Cabin", (length * 0.88, width * 0.96, height * 0.44), (-0.04 if kind == "bus" else -0.06, 0.0, 0.12 + height * 0.72), body_mat, collection, v_root, bevel=0.05)
    add_box(f"{prefix}_Stripe", (length + 0.01, width + 0.01, 0.10), (0.0, 0.0, 0.34), stripe_mat, collection, v_root, bevel=0.01)

    # Windows & windshield.
    add_box(f"{prefix}_Windshield", (0.04, width * 0.82, height * 0.32), (length * 0.42, 0.0, 0.12 + height * 0.68), glass_mat, collection, v_root, bevel=0.01)
    for side in (-1, 1):
        add_box(f"{prefix}_SideGlass_{side}", (length * 0.68, 0.03, height * 0.28), (-0.04, side * (width * 0.48), 0.12 + height * 0.70), glass_mat, collection, v_root)

    # Bumpers, headlights & roof sign/beacon.
    add_box(f"{prefix}_BumperF", (0.06, width * 0.96, 0.07), (length * 0.51, 0.0, 0.15), metal_mat, collection, v_root, bevel=0.015)
    add_box(f"{prefix}_BumperB", (0.06, width * 0.96, 0.07), (-length * 0.51, 0.0, 0.15), metal_mat, collection, v_root, bevel=0.015)
    for side in (-1, 1):
        add_cylinder(f"{prefix}_Headlight_{side}", 0.04, 0.04, 0.03, (length * 0.505, side * width * 0.32, 0.25), glow_mat, collection, v_root, segments=12, rotation=(0.0, math.pi * 0.5, 0.0))

    if kind == "bus":
        add_box(f"{prefix}_RouteBoard", (0.14, width * 0.52, 0.09), (length * 0.26, 0.0, 0.12 + height * 0.98), stripe_mat, collection, v_root, bevel=0.015)
    else:
        add_box(f"{prefix}_Lightbar", (0.12, width * 0.45, 0.08), (length * 0.22, 0.0, 0.12 + height * 0.98), stripe_mat, collection, v_root, bevel=0.015)

    # Four wheels with metallic hubcaps.
    for wx in (-length * 0.32, length * 0.32):
        for wy in (-width * 0.49, width * 0.49):
            add_cylinder(f"{prefix}_Tire_{wx:.2f}_{wy:.2f}", 0.12, 0.12, 0.09, (wx, wy, 0.12), tire_mat, collection, v_root, segments=16, bevel=0.015, rotation=(math.pi * 0.5, 0.0, 0.0))
            add_cylinder(f"{prefix}_Rim_{wx:.2f}_{wy:.2f}", 0.065, 0.065, 0.10, (wx, wy, 0.12), metal_mat, collection, v_root, segments=12, rotation=(math.pi * 0.5, 0.0, 0.0))
    return v_root
