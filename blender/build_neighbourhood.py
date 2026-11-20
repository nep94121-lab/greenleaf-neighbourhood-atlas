"""Scene builder, studio lighting, Blender 5.2 compositor, and renderer for Greenleaf Neighbourhood."""

import argparse
import math
import sys
import time
from pathlib import Path

import bpy
from mathutils import Vector

BLENDER_DIR = Path(__file__).resolve().parent
if str(BLENDER_DIR) not in sys.path:
    sys.path.insert(0, str(BLENDER_DIR))

from buildings import BUILDERS  # noqa: E402
from materials import build_material_palette  # noqa: E402
from overview import build_overview_diorama  # noqa: E402
from spec import CC0_HDRI_PATH, LANDMARK_BY_ID, LANDMARKS, OUTPUT_DIR  # noqa: E402


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup_render_settings(engine="CYCLES", samples=48, transparent=True, width=1024, height=1024):
    scene = bpy.context.scene
    scene.render.engine = engine
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = transparent
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    scene.render.image_settings.color_depth = "8"

    if engine == "CYCLES":
        scene.cycles.device = "CPU"
        scene.cycles.samples = samples
        scene.cycles.use_adaptive_sampling = True
        scene.cycles.adaptive_threshold = 0.03
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
        scene.cycles.max_bounces = 4
        scene.cycles.diffuse_bounces = 2
        scene.cycles.glossy_bounces = 2
        scene.cycles.transmission_bounces = 2
        scene.cycles.transparent_max_bounces = 3
    else:
        scene.eevee.taa_render_samples = max(32, samples)
        scene.eevee.use_raytracing = True
        scene.eevee.use_shadows = True
        scene.eevee.shadow_ray_count = 3
        scene.eevee.shadow_step_count = 8
        scene.eevee.shadow_resolution_scale = 1.0

    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.view_settings.exposure = -0.10


def _add_gobo_canopy(collection):
    """Overhead procedural cloud/foliage gobo breaking up flat directional sunlight on the diorama."""
    import bmesh

    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=24.0)
    mesh = bpy.data.meshes.new("Light_Gobo_Canopy")
    bm.to_mesh(mesh)
    bm.free()

    gobo = bpy.data.objects.new("Light_Gobo_Canopy", mesh)
    gobo.location = (-8.0, -6.0, 26.0)
    gobo.visible_camera = False
    gobo.visible_glossy = False
    gobo.visible_diffuse = False
    collection.objects.link(gobo)

    mat = bpy.data.materials.new("Gobo_Canopy_Mat")
    tree = mat.node_tree
    tree.nodes.clear()
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    mix = tree.nodes.new("ShaderNodeMixShader")
    trans = tree.nodes.new("ShaderNodeBsdfTransparent")
    diff = tree.nodes.new("ShaderNodeBsdfDiffuse")
    diff.inputs["Color"].default_value = (0.15, 0.15, 0.15, 1.0)

    tc = tree.nodes.new("ShaderNodeTexCoord")
    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 0.22
    noise.inputs["Detail"].default_value = 3.0
    ramp = tree.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.56
    ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    ramp.color_ramp.elements[1].position = 0.78
    ramp.color_ramp.elements[1].color = (0.28, 0.28, 0.28, 1.0)

    tree.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    tree.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    tree.links.new(ramp.outputs["Color"], mix.inputs["Fac"])
    tree.links.new(trans.outputs["BSDF"], mix.inputs[1])
    tree.links.new(diff.outputs["BSDF"], mix.inputs[2])
    tree.links.new(mix.outputs["Shader"], out.inputs["Surface"])
    gobo.data.materials.append(mat)


def setup_lighting(collection, is_overview=False):
    scene = bpy.context.scene
    world = bpy.data.worlds.new("GreenleafWorld")
    scene.world = world
    wtree = world.node_tree
    wtree.nodes.clear()

    w_out = wtree.nodes.new("ShaderNodeOutputWorld")
    bg_lit = wtree.nodes.new("ShaderNodeBackground")

    if CC0_HDRI_PATH.exists():
        env = wtree.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(str(CC0_HDRI_PATH))
        tc = wtree.nodes.new("ShaderNodeTexCoord")
        mp = wtree.nodes.new("ShaderNodeMapping")
        mp.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(-35.0))
        wtree.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
        wtree.links.new(mp.outputs["Vector"], env.inputs["Vector"])
        wtree.links.new(env.outputs["Color"], bg_lit.inputs["Color"])
        bg_lit.inputs["Strength"].default_value = 0.62 if is_overview else 0.54
    else:
        sky = wtree.nodes.new("ShaderNodeTexSky")
        sky.sky_type = "MULTIPLE_SCATTERING"
        sky.sun_disc = False
        sky.sun_elevation = math.radians(38.0)
        sky.sun_rotation = math.radians(-40.0)
        sky.air_density = 1.15
        sky.aerosol_density = 0.9
        sky.ground_albedo = 0.30
        wtree.links.new(sky.outputs["Color"], bg_lit.inputs["Color"])
        bg_lit.inputs["Strength"].default_value = 0.36

    if is_overview:
        # Keep physical HDRI lighting/reflections while showing a warm sunlit daylight-ivory backdrop behind the diorama.
        lp = wtree.nodes.new("ShaderNodeLightPath")
        bg_cam = wtree.nodes.new("ShaderNodeBackground")
        bg_cam.inputs["Color"].default_value = (0.86, 0.89, 0.83, 1.0)
        bg_cam.inputs["Strength"].default_value = 1.10
        mix_s = wtree.nodes.new("ShaderNodeMixShader")
        wtree.links.new(lp.outputs["Is Camera Ray"], mix_s.inputs["Fac"])
        wtree.links.new(bg_lit.outputs["Background"], mix_s.inputs[1])
        wtree.links.new(bg_cam.outputs["Background"], mix_s.inputs[2])
        wtree.links.new(mix_s.outputs["Shader"], w_out.inputs["Surface"])
    else:
        wtree.links.new(bg_lit.outputs["Background"], w_out.inputs["Surface"])

    sun_data = bpy.data.lights.new("Key_Sun", type="SUN")
    sun_data.energy = 2.6 if not is_overview else 2.8
    sun_data.color = (1.0, 0.92, 0.80)
    sun_data.angle = math.radians(1.6)
    sun = bpy.data.objects.new("Key_Sun", sun_data)
    sun.rotation_euler = (math.radians(46.0), math.radians(15.0), math.radians(-132.0))
    collection.objects.link(sun)

    scale = 3.2 if is_overview else 1.0
    fill_data = bpy.data.lights.new("Sky_Fill", type="AREA")
    fill_data.energy = 34.0 * scale
    fill_data.color = (0.74, 0.87, 1.0)
    fill_data.size = 9.0 * scale
    fill = bpy.data.objects.new("Sky_Fill", fill_data)
    fill.location = (-8.5 * scale, 6.5 * scale, 7.5 * scale)
    target = Vector((1.5, 0.5, 0.5)) if is_overview else Vector((0.0, 0.0, 1.0))
    fill.rotation_euler = (target - fill.location).to_track_quat("-Z", "Y").to_euler()
    collection.objects.link(fill)

    rim_data = bpy.data.lights.new("Warm_Rim", type="AREA")
    rim_data.energy = 20.0 * scale
    rim_data.color = (1.0, 0.89, 0.74)
    rim_data.size = 7.0 * scale
    rim = bpy.data.objects.new("Warm_Rim", rim_data)
    rim.location = (6.5 * scale, 8.0 * scale, 6.5 * scale)
    rim.rotation_euler = (target - rim.location).to_track_quat("-Z", "Y").to_euler()
    collection.objects.link(rim)

    if is_overview and bpy.context.scene.render.engine == "CYCLES":
        _add_gobo_canopy(collection)


def setup_compositor(transparent=True):
    """Configure Blender 5.2 CompositorNodeTree with Fog Glow bloom & lens dispersion on opaque diorama."""
    scene = bpy.context.scene
    ng = bpy.data.node_groups.new("GreenleafComp", "CompositorNodeTree")
    scene.compositing_node_group = ng
    ng.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    rl = ng.nodes.new("CompositorNodeRLayers")
    out = ng.nodes.new("NodeGroupOutput")

    if transparent:
        ng.links.new(rl.outputs["Image"], out.inputs["Image"])
        return

    glare = ng.nodes.new("CompositorNodeGlare")
    glare.inputs["Type"].default_value = "Fog Glow"
    glare.inputs["Threshold"].default_value = 1.25
    glare.inputs["Strength"].default_value = 0.20
    glare.inputs["Size"].default_value = 7

    lens = ng.nodes.new("CompositorNodeLensdist")
    lens.inputs["Dispersion"].default_value = 0.0035

    ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
    ng.links.new(glare.outputs["Image"], lens.inputs["Image"])
    ng.links.new(lens.outputs["Image"], out.inputs["Image"])


def setup_fitted_camera(
    collection,
    lens_mm=52.0,
    azimuth_deg=-35.0,
    elev_deg=26.0,
    fill_ratio=0.84,
    fstop=5.0,
    use_bounds_of=None,
):
    """Place a 35mm full-frame camera optically centered on actual projected mesh vertices."""
    cam_data = bpy.data.cameras.new("ArchCam")
    cam_data.lens = lens_mm
    cam_data.sensor_fit = "HORIZONTAL"
    cam_data.sensor_width = 36.0
    cam_data.clip_start = 0.1
    cam_data.clip_end = 300.0

    cam_obj = bpy.data.objects.new("ArchCam", cam_data)
    collection.objects.link(cam_obj)
    bpy.context.scene.camera = cam_obj

    depsgraph = bpy.context.evaluated_depsgraph_get()
    world_pts = []
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or obj.name == "Light_Gobo_Canopy":
            continue
        if use_bounds_of is not None and not use_bounds_of(obj):
            continue
        eval_obj = obj.evaluated_get(depsgraph)
        mw = eval_obj.matrix_world
        for v in eval_obj.data.vertices:
            world_pts.append(mw @ v.co)

    mins = Vector((min(p.x for p in world_pts), min(p.y for p in world_pts), min(p.z for p in world_pts)))
    maxs = Vector((max(p.x for p in world_pts), max(p.y for p in world_pts), max(p.z for p in world_pts)))
    center = (mins + maxs) * 0.5

    az = math.radians(azimuth_deg)
    el = math.radians(elev_deg)
    view_dir = Vector((
        math.sin(-az) * math.cos(el),
        -math.cos(az) * math.cos(el),
        math.sin(el),
    )).normalized()

    rot_quat = (-view_dir).to_track_quat("-Z", "Y")
    inv_rot = rot_quat.to_matrix().to_4x4().inverted()

    half_fov = math.atan((cam_data.sensor_width * 0.5) / lens_mm)
    aspect = bpy.context.scene.render.resolution_y / bpy.context.scene.render.resolution_x
    tan_h = math.tan(half_fov)
    tan_v = tan_h * aspect

    cam_right = (rot_quat @ Vector((1.0, 0.0, 0.0))).normalized()
    cam_up = (rot_quat @ Vector((0.0, 1.0, 0.0))).normalized()
    proj_pts = [inv_rot @ (p - center) for p in world_pts]
    mid_x = 0.5 * (min(q.x for q in proj_pts) + max(q.x for q in proj_pts))
    mid_y = 0.5 * (min(q.y for q in proj_pts) + max(q.y for q in proj_pts))
    optical_target = center + cam_right * mid_x + cam_up * mid_y

    req_dist = 4.0
    for p in world_pts:
        lc = inv_rot @ (p - optical_target)
        d_x = abs(lc.x) / (fill_ratio * tan_h) + lc.z
        d_y = abs(lc.y) / (fill_ratio * tan_v) + lc.z
        req_dist = max(req_dist, d_x, d_y)

    focus_empty = bpy.data.objects.new("Camera_Focus_Target", None)
    focus_empty.location = optical_target
    collection.objects.link(focus_empty)

    cam_obj.location = optical_target + view_dir * req_dist
    cam_obj.rotation_euler = rot_quat.to_euler()

    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = focus_empty
    cam_data.dof.aperture_fstop = fstop
    return cam_obj


def render_single_landmark(lm_id, engine="CYCLES", samples=48):
    lm = LANDMARK_BY_ID[lm_id]
    clear_scene()
    col = bpy.context.scene.collection
    setup_render_settings(engine=engine, samples=samples, transparent=True, width=1024, height=1024)
    setup_lighting(col, is_overview=False)
    setup_compositor(transparent=True)
    mats = build_material_palette()
    BUILDERS[lm_id](lm, mats, col, include_plinth=True)
    setup_fitted_camera(col, lens_mm=52.0, azimuth_deg=-35.0, elev_deg=26.0, fill_ratio=0.84, fstop=5.0)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{lm_id}.png"
    bpy.context.scene.render.filepath = str(out_path)
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t0
    print(f"[RENDER] {lm_id}.png rendered in {dt:.2f}s via {engine} ({samples} samples)", flush=True)
    return out_path, dt


def render_overview(engine="CYCLES", samples=48):
    clear_scene()
    col = bpy.context.scene.collection
    setup_render_settings(engine=engine, samples=samples, transparent=False, width=1920, height=1080)
    setup_lighting(col, is_overview=True)
    setup_compositor(transparent=False)
    mats = build_material_palette()
    build_overview_diorama(mats, col)
    setup_fitted_camera(col, lens_mm=44.0, azimuth_deg=24.0, elev_deg=32.0, fill_ratio=0.90, fstop=7.1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "overview-diorama.png"
    bpy.context.scene.render.filepath = str(out_path)
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t0
    print(f"[RENDER] overview-diorama.png rendered in {dt:.2f}s via {engine} ({samples} samples)", flush=True)

    # Export exact screen-space percentages (x_pct, y_pct from top-left) for Slide 3 diorama pins.
    from bpy_extras.object_utils import world_to_camera_view
    scene = bpy.context.scene
    cam = scene.camera
    pin_map = {}
    for lm in LANDMARKS:
        co = Vector((lm.cx, lm.cy, 0.9))
        uvz = world_to_camera_view(scene, cam, co)
        pin_map[lm.id] = {
            "x_pct": round(uvz.x * 100.0, 2),
            "y_pct": round((1.0 - uvz.y) * 100.0, 2),
        }
    import json
    (BLENDER_DIR / "diorama_pins.json").write_text(json.dumps(pin_map, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("[PINS] Exported exact overview-diorama camera coordinates to blender/diorama_pins.json", flush=True)
    return out_path, dt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", type=str, default=None, help="Comma-separated landmark IDs or 'overview'")
    parser.add_argument("--overview", action="store_true", help="Render overview-diorama.png")
    parser.add_argument("--all", action="store_true", help="Render all 10 landmarks + overview")
    parser.add_argument("--engine", type=str, default="BLENDER_EEVEE", choices=["CYCLES", "BLENDER_EEVEE"])
    parser.add_argument("--samples", type=int, default=48)
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    args = parser.parse_args(argv)

    if args.only:
        for item in args.only.split(","):
            item = item.strip()
            if item == "overview":
                render_overview(engine=args.engine, samples=args.samples)
            else:
                render_single_landmark(item, engine=args.engine, samples=args.samples)
    elif args.overview:
        render_overview(engine=args.engine, samples=args.samples)
    else:
        for lm in LANDMARKS:
            render_single_landmark(lm.id, engine=args.engine, samples=args.samples)
        render_overview(engine=args.engine, samples=args.samples)


if __name__ == "__main__":
    main()
