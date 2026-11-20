"""Procedural and CC0-textured PBR material library calibrated for Blender 5.2.2 LTS + AgX."""

from pathlib import Path
import bpy

CC0_DIR = Path(__file__).resolve().parent.parent / "assets" / "cc0-sources"


def _load_image(path, colorspace="sRGB"):
    name = path.name
    if name in bpy.data.images:
        img = bpy.data.images[name]
    else:
        img = bpy.data.images.load(str(path))
    img.colorspace_settings.name = colorspace
    return img


def make_cc0_pbr_mat(name, folder, prefix, tile_scale=0.55, tint=(1.0, 1.0, 1.0), normal_strength=0.45, fallback_fn=None):
    """Build box-mapped CC0 image PBR material (Color, Roughness, NormalGL) with procedural fallback."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    base_dir = CC0_DIR / folder
    col_p = base_dir / f"{prefix}_Color.jpg"
    rgh_p = base_dir / f"{prefix}_Roughness.jpg"
    nrm_p = base_dir / f"{prefix}_NormalGL.jpg"
    if not (col_p.exists() and rgh_p.exists() and nrm_p.exists()):
        return fallback_fn() if fallback_fn else make_pbr_mat(name, (0.3, 0.3, 0.3))

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new("ShaderNodeOutputMaterial")
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = tree.nodes.new("ShaderNodeTexCoord")
    mp = tree.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (tile_scale, tile_scale, tile_scale)
    tree.links.new(tc.outputs["Object"], mp.inputs["Vector"])

    tex_c = tree.nodes.new("ShaderNodeTexImage")
    tex_c.image = _load_image(col_p, "sRGB")
    tex_c.projection = "BOX"
    tex_c.projection_blend = 0.15
    tree.links.new(mp.outputs["Vector"], tex_c.inputs["Vector"])

    # Apply subtle albedo tint multiplier for balanced AgX contrast.
    tint_mix = _mix_rgba(tree, (1, 1, 1, 1), (*tint[:3], 1.0), None, blend_type="MULTIPLY")
    tint_mix.inputs[0].default_value = 1.0
    tree.links.new(tex_c.outputs["Color"], tint_mix.inputs[6])
    tree.links.new(tint_mix.outputs[2], bsdf.inputs["Base Color"])

    tex_r = tree.nodes.new("ShaderNodeTexImage")
    tex_r.image = _load_image(rgh_p, "Non-Color")
    tex_r.projection = "BOX"
    tex_r.projection_blend = 0.15
    tree.links.new(mp.outputs["Vector"], tex_r.inputs["Vector"])
    tree.links.new(tex_r.outputs["Color"], bsdf.inputs["Roughness"])

    tex_n = tree.nodes.new("ShaderNodeTexImage")
    tex_n.image = _load_image(nrm_p, "Non-Color")
    tex_n.projection = "BOX"
    tex_n.projection_blend = 0.15
    tree.links.new(mp.outputs["Vector"], tex_n.inputs["Vector"])
    nrm = tree.nodes.new("ShaderNodeNormalMap")
    nrm.inputs["Strength"].default_value = normal_strength
    tree.links.new(tex_n.outputs["Color"], nrm.inputs["Color"])
    tree.links.new(nrm.outputs["Normal"], bsdf.inputs["Normal"])

    _set_input(bsdf, "Specular IOR Level", 0.42)
    return mat


def _set_input(node, name, value):
    sock = node.inputs.get(name)
    if sock is not None:
        sock.default_value = value


def _mix_float_linear_light(tree, base_rough, noise_out, factor=0.28):
    mix = tree.nodes.new("ShaderNodeMix")
    mix.data_type = "FLOAT"
    mix.blend_type = "LINEAR_LIGHT"
    mix.clamp_result = True
    mix.inputs[0].default_value = factor
    mix.inputs[2].default_value = base_rough
    tree.links.new(noise_out, mix.inputs[3])
    return mix.outputs[0]


def _mix_rgba(tree, col_a, col_b, factor_socket, blend_type="MIX"):
    mix = tree.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = blend_type
    mix.clamp_result = True
    mix.inputs[6].default_value = col_a
    mix.inputs[7].default_value = col_b
    if factor_socket is not None:
        tree.links.new(factor_socket, mix.inputs[0])
    return mix


def make_pbr_mat(
    name,
    base_color,
    roughness=0.55,
    metallic=0.0,
    specular=0.5,
    coat=0.0,
    coat_rough=0.1,
    noise_scale=18.0,
    rough_var=0.24,
    bump_strength=0.06,
    wear_color=None,
    subsurface=0.0,
    emission_color=None,
    emission_strength=0.0,
    transmission=0.0,
    ior=1.45,
):
    """Create a procedural PBR material with micro-roughness noise, macro breakup, and Pointiness edge wear."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (280, 0)
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tex_coord = tree.nodes.new("ShaderNodeTexCoord")
    tex_coord.location = (-800, 0)

    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.location = (-520, -80)
    noise.inputs["Scale"].default_value = noise_scale
    noise.inputs["Detail"].default_value = 5.0
    noise.inputs["Roughness"].default_value = 0.60
    tree.links.new(tex_coord.outputs["Object"], noise.inputs["Vector"])

    # Micro-roughness variation via Linear Light mix.
    rough_ramp = tree.nodes.new("ShaderNodeValToRGB")
    rough_ramp.location = (-280, -140)
    rough_ramp.color_ramp.elements[0].position = 0.25
    rough_ramp.color_ramp.elements[0].color = (0.35, 0.35, 0.35, 1.0)
    rough_ramp.color_ramp.elements[1].position = 0.78
    rough_ramp.color_ramp.elements[1].color = (0.68, 0.68, 0.68, 1.0)
    tree.links.new(noise.outputs["Fac"], rough_ramp.inputs["Fac"])
    rough_sock = _mix_float_linear_light(tree, roughness, rough_ramp.outputs["Color"], factor=rough_var)
    tree.links.new(rough_sock, bsdf.inputs["Roughness"])

    # Macro tonal variation + Pointiness edge wear (lightweight, zero extra AO ray overhead).
    macro_noise = tree.nodes.new("ShaderNodeTexNoise")
    macro_noise.location = (-520, 320)
    macro_noise.inputs["Scale"].default_value = max(2.2, noise_scale * 0.16)
    macro_noise.inputs["Detail"].default_value = 4.0
    tree.links.new(tex_coord.outputs["Object"], macro_noise.inputs["Vector"])

    macro_ramp = tree.nodes.new("ShaderNodeValToRGB")
    macro_ramp.location = (-300, 320)
    macro_ramp.color_ramp.elements[0].position = 0.32
    macro_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    macro_ramp.color_ramp.elements[1].position = 0.72
    macro_ramp.color_ramp.elements[1].color = (0.24, 0.24, 0.24, 1.0)
    tree.links.new(macro_noise.outputs["Fac"], macro_ramp.inputs["Fac"])

    c_dark = (base_color[0] * 0.80, base_color[1] * 0.78, base_color[2] * 0.76, 1.0)
    c_wear = wear_color or (
        min(1.0, base_color[0] * 1.15 + 0.02),
        min(1.0, base_color[1] * 1.15 + 0.02),
        min(1.0, base_color[2] * 1.13 + 0.02),
        1.0,
    )

    base_mix = _mix_rgba(tree, (*base_color[:3], 1.0), c_dark, macro_ramp.outputs["Color"])

    geom = tree.nodes.new("ShaderNodeNewGeometry")
    geom.location = (-520, 80)
    pt_ramp = tree.nodes.new("ShaderNodeValToRGB")
    pt_ramp.location = (-300, 80)
    pt_ramp.color_ramp.elements[0].position = 0.55
    pt_ramp.color_ramp.elements[0].color = (0.0, 0.0, 0.0, 1.0)
    pt_ramp.color_ramp.elements[1].position = 0.76
    pt_ramp.color_ramp.elements[1].color = (0.30, 0.30, 0.30, 1.0)
    tree.links.new(geom.outputs["Pointiness"], pt_ramp.inputs["Fac"])

    edge_mix = _mix_rgba(tree, (0, 0, 0, 1), (*c_wear[:3], 1.0), pt_ramp.outputs["Color"])
    tree.links.new(base_mix.outputs[2], edge_mix.inputs[6])
    tree.links.new(edge_mix.outputs[2], bsdf.inputs["Base Color"])

    if bump_strength > 0.0:
        bump = tree.nodes.new("ShaderNodeBump")
        bump.location = (40, -240)
        bump.inputs["Strength"].default_value = bump_strength
        bump.inputs["Distance"].default_value = 0.012
        tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
        tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])

    _set_input(bsdf, "Metallic", metallic)
    _set_input(bsdf, "Specular IOR Level", specular)
    _set_input(bsdf, "Coat Weight", coat)
    _set_input(bsdf, "Coat Roughness", coat_rough)
    _set_input(bsdf, "Subsurface Weight", subsurface)
    _set_input(bsdf, "Transmission Weight", transmission)
    _set_input(bsdf, "IOR", ior)
    if emission_color is not None and emission_strength > 0.0:
        _set_input(bsdf, "Emission Color", (*emission_color[:3], 1.0))
        _set_input(bsdf, "Emission Strength", emission_strength)

    return mat


def make_brick_mat(name, brick_col1, brick_col2, mortar_col, scale=5.5, bump_strength=0.14):
    """Procedural brick masonry shader with mortar joints and relief bump."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new("ShaderNodeOutputMaterial")
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = tree.nodes.new("ShaderNodeTexCoord")
    brick = tree.nodes.new("ShaderNodeTexBrick")
    brick.inputs["Scale"].default_value = scale
    brick.inputs["Mortar Size"].default_value = 0.032
    brick.inputs["Mortar Smooth"].default_value = 0.15
    brick.inputs["Bias"].default_value = 0.05
    brick.inputs["Brick Width"].default_value = 0.45
    brick.inputs["Row Height"].default_value = 0.22
    brick.inputs["Color1"].default_value = (*brick_col1[:3], 1.0)
    brick.inputs["Color2"].default_value = (*brick_col2[:3], 1.0)
    brick.inputs["Mortar"].default_value = (*mortar_col[:3], 1.0)

    sep = tree.nodes.new("ShaderNodeSeparateXYZ")
    tree.links.new(tc.outputs["Object"], sep.inputs["Vector"])
    add_xy = tree.nodes.new("ShaderNodeMath")
    add_xy.operation = "ADD"
    tree.links.new(sep.outputs["X"], add_xy.inputs[0])
    tree.links.new(sep.outputs["Y"], add_xy.inputs[1])
    comb = tree.nodes.new("ShaderNodeCombineXYZ")
    tree.links.new(add_xy.outputs["Value"], comb.inputs["X"])
    tree.links.new(sep.outputs["Z"], comb.inputs["Y"])
    tree.links.new(comb.outputs["Vector"], brick.inputs["Vector"])

    tree.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])

    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 24.0
    tree.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    rough_sock = _mix_float_linear_light(tree, 0.74, noise.outputs["Fac"], factor=0.22)
    tree.links.new(rough_sock, bsdf.inputs["Roughness"])

    bump = tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = bump_strength
    bump.inputs["Distance"].default_value = 0.018
    tree.links.new(brick.outputs["Fac"], bump.inputs["Height"])
    tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    _set_input(bsdf, "Specular IOR Level", 0.35)
    return mat


def make_striped_awning_mat(name, col_a, col_b, stripe_scale=7.0):
    """Procedural woven striped awning cloth material."""
    if name in bpy.data.materials:
        return bpy.data.materials[name]

    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()

    out = tree.nodes.new("ShaderNodeOutputMaterial")
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    tc = tree.nodes.new("ShaderNodeTexCoord")
    wave = tree.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "X"
    wave.wave_profile = "SAW"
    wave.inputs["Scale"].default_value = stripe_scale
    wave.inputs["Distortion"].default_value = 0.0
    tree.links.new(tc.outputs["Object"], wave.inputs["Vector"])

    ramp = tree.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.interpolation = "CONSTANT"
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (*col_a[:3], 1.0)
    ramp.color_ramp.elements[1].position = 0.5
    ramp.color_ramp.elements[1].color = (*col_b[:3], 1.0)
    tree.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 90.0
    tree.links.new(tc.outputs["Object"], noise.inputs["Vector"])
    rough_sock = _mix_float_linear_light(tree, 0.78, noise.outputs["Fac"], factor=0.16)
    tree.links.new(rough_sock, bsdf.inputs["Roughness"])
    _set_input(bsdf, "Sheen Weight", 0.35)
    _set_input(bsdf, "Specular IOR Level", 0.25)

    bump = tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.04
    bump.inputs["Distance"].default_value = 0.005
    tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def make_glass_mat(name="Glass_Arch", tint=(0.24, 0.48, 0.62), roughness=0.05):
    """Reflective tinted architectural glass (fast glossy-clear coat without slow caustics)."""
    return make_pbr_mat(
        name,
        base_color=tint,
        roughness=roughness,
        metallic=0.12,
        specular=0.95,
        coat=0.85,
        coat_rough=0.02,
        noise_scale=6.0,
        rough_var=0.04,
        bump_strength=0.0,
        transmission=0.22,
        ior=1.52,
    )


def build_material_palette():
    """Return shared palette calibrated in linear RGB for AgX Medium High Contrast."""
    return {
        "plinth_walnut": make_pbr_mat("Plinth_Walnut", (0.11, 0.065, 0.040), roughness=0.46, noise_scale=12.0, bump_strength=0.05),
        "plinth_slate": make_pbr_mat("Plinth_Slate", (0.14, 0.16, 0.19), roughness=0.56, noise_scale=14.0, bump_strength=0.07),
        "grass_lush": make_pbr_mat("Grass_Lush", (0.085, 0.26, 0.060), roughness=0.84, noise_scale=24.0, bump_strength=0.12, wear_color=(0.14, 0.34, 0.08)),
        "grass_park": make_pbr_mat("Grass_Park", (0.075, 0.29, 0.068), roughness=0.82, noise_scale=20.0, bump_strength=0.11, wear_color=(0.13, 0.36, 0.09)),
        "sidewalk_stone": make_cc0_pbr_mat(
            "Sidewalk_Stone",
            "PavingStones152_1K-JPG",
            "PavingStones152_1K-JPG",
            tile_scale=0.58,
            tint=(0.88, 0.85, 0.78),
            normal_strength=0.45,
            fallback_fn=lambda: make_pbr_mat("Sidewalk_Stone_Proc", (0.46, 0.44, 0.39), roughness=0.72, noise_scale=16.0, bump_strength=0.08),
        ),
        "curb_granite": make_pbr_mat("Curb_Granite", (0.31, 0.31, 0.29), roughness=0.68, noise_scale=20.0, bump_strength=0.09),
        "asphalt": make_cc0_pbr_mat(
            "Road_Asphalt",
            "Asphalt033_1K-JPG",
            "Asphalt033_1K-JPG",
            tile_scale=0.48,
            tint=(0.56, 0.58, 0.62),
            normal_strength=0.50,
            fallback_fn=lambda: make_pbr_mat("Road_Asphalt_Proc", (0.065, 0.070, 0.082), roughness=0.78, noise_scale=44.0, bump_strength=0.11),
        ),
        "road_paint_white": make_pbr_mat("Road_Paint_White", (0.76, 0.74, 0.69), roughness=0.56, noise_scale=28.0, bump_strength=0.04),
        "road_paint_yellow": make_pbr_mat("Road_Paint_Yellow", (0.76, 0.46, 0.06), roughness=0.54, noise_scale=25.0, bump_strength=0.04),
        "stucco_cream": make_pbr_mat("Stucco_Cream", (0.68, 0.60, 0.47), roughness=0.68, noise_scale=18.0, bump_strength=0.07),
        "stucco_butter": make_pbr_mat("Stucco_Butter", (0.76, 0.56, 0.25), roughness=0.64, noise_scale=16.0, bump_strength=0.06),
        "stucco_white": make_pbr_mat("Stucco_White", (0.74, 0.75, 0.76), roughness=0.58, noise_scale=14.0, bump_strength=0.04),
        "stucco_mint": make_pbr_mat("Stucco_Mint", (0.42, 0.64, 0.50), roughness=0.62, noise_scale=16.0, bump_strength=0.05),
        "brick_red": make_brick_mat("Brick_Red", (0.36, 0.085, 0.055), (0.28, 0.068, 0.044), (0.58, 0.53, 0.46), scale=3.8),
        "brick_warm": make_brick_mat("Brick_Warm", (0.46, 0.17, 0.085), (0.38, 0.13, 0.065), (0.60, 0.55, 0.48), scale=3.8),
        "roof_terracotta": make_pbr_mat("Roof_Terracotta", (0.46, 0.115, 0.050), roughness=0.48, noise_scale=15.0, bump_strength=0.08, wear_color=(0.58, 0.16, 0.07)),
        "roof_slate": make_pbr_mat("Roof_Slate", (0.095, 0.125, 0.165), roughness=0.46, noise_scale=16.0, bump_strength=0.07),
        "roof_teal": make_pbr_mat("Roof_Teal", (0.055, 0.24, 0.26), roughness=0.42, metallic=0.12, noise_scale=14.0, bump_strength=0.05),
        "roof_green": make_pbr_mat("Roof_Green", (0.065, 0.21, 0.12), roughness=0.45, noise_scale=14.0, bump_strength=0.06),
        "wood_warm": make_pbr_mat("Wood_Warm", (0.28, 0.13, 0.055), roughness=0.52, noise_scale=22.0, bump_strength=0.07),
        "wood_dark": make_pbr_mat("Wood_Dark", (0.12, 0.065, 0.035), roughness=0.48, noise_scale=20.0, bump_strength=0.07),
        "wood_white": make_pbr_mat("Wood_White", (0.76, 0.74, 0.69), roughness=0.48, noise_scale=18.0, bump_strength=0.03),
        "wood_green": make_pbr_mat("Wood_Forest_Green", (0.045, 0.19, 0.11), roughness=0.42, coat=0.25, noise_scale=16.0, bump_strength=0.04),
        "metal_dark": make_pbr_mat("Metal_Iron", (0.07, 0.08, 0.095), roughness=0.36, metallic=0.86, noise_scale=24.0, bump_strength=0.03),
        "metal_silver": make_pbr_mat("Metal_Steel", (0.50, 0.53, 0.56), roughness=0.28, metallic=0.88, noise_scale=20.0, bump_strength=0.02),
        "metal_brass": make_pbr_mat("Metal_Brass", (0.68, 0.44, 0.11), roughness=0.26, metallic=0.92, noise_scale=18.0, bump_strength=0.02),
        "accent_red": make_pbr_mat("Accent_Red", (0.64, 0.055, 0.055), roughness=0.34, coat=0.40, noise_scale=14.0, bump_strength=0.02),
        "accent_teal": make_pbr_mat("Accent_Teal", (0.045, 0.34, 0.33), roughness=0.38, coat=0.25, noise_scale=14.0, bump_strength=0.02),
        "accent_amber": make_pbr_mat("Accent_Amber", (0.74, 0.38, 0.05), roughness=0.36, coat=0.25, noise_scale=14.0, bump_strength=0.02),
        "accent_blue": make_pbr_mat("Accent_Blue", (0.07, 0.24, 0.56), roughness=0.38, coat=0.25, noise_scale=14.0, bump_strength=0.02),
        "glass": make_glass_mat(),
        "interior_warm": make_pbr_mat("Interior_Warm", (0.85, 0.58, 0.22), roughness=0.6, emission_color=(1.0, 0.75, 0.36), emission_strength=1.4),
        "lamp_glow": make_pbr_mat("Lamp_Glow", (1.0, 0.85, 0.50), roughness=0.2, emission_color=(1.0, 0.84, 0.48), emission_strength=3.5),
        "water": make_pbr_mat("Water_Fountain", (0.08, 0.42, 0.58), roughness=0.05, specular=0.9, coat=0.8, transmission=0.45, ior=1.33, noise_scale=12.0, bump_strength=0.04),
        "bark": make_pbr_mat("Tree_Bark", (0.16, 0.095, 0.050), roughness=0.86, noise_scale=28.0, bump_strength=0.16),
        "foliage_emerald": make_pbr_mat("Foliage_Emerald", (0.065, 0.25, 0.055), roughness=0.68, subsurface=0.12, noise_scale=28.0, bump_strength=0.14, wear_color=(0.13, 0.36, 0.08)),
        "foliage_lime": make_pbr_mat("Foliage_Lime", (0.14, 0.35, 0.070), roughness=0.65, subsurface=0.14, noise_scale=24.0, bump_strength=0.14, wear_color=(0.24, 0.46, 0.11)),
        "foliage_autumn": make_pbr_mat("Foliage_Autumn", (0.58, 0.18, 0.04), roughness=0.66, subsurface=0.12, noise_scale=24.0, bump_strength=0.14),
        "flower_coral": make_pbr_mat("Flower_Coral", (0.76, 0.14, 0.12), roughness=0.52, subsurface=0.1),
        "flower_gold": make_pbr_mat("Flower_Gold", (0.84, 0.54, 0.06), roughness=0.50, subsurface=0.1),
        "tire_rubber": make_pbr_mat("Tire_Rubber", (0.04, 0.04, 0.045), roughness=0.82, noise_scale=35.0, bump_strength=0.06),
        "awning_red": make_striped_awning_mat("Awning_Red_Cream", (0.60, 0.075, 0.065), (0.80, 0.75, 0.65), stripe_scale=6.5),
        "awning_green": make_striped_awning_mat("Awning_Green_Cream", (0.055, 0.28, 0.15), (0.80, 0.76, 0.65), stripe_scale=6.5),
        "awning_amber": make_striped_awning_mat("Awning_Amber_Cream", (0.68, 0.34, 0.055), (0.82, 0.76, 0.66), stripe_scale=6.5),
    }
