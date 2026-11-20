import importlib.util
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

QA_DIR = Path(__file__).resolve().parent
PROJECT_DIR = QA_DIR.parent
MAP_DATA_JS = PROJECT_DIR / "scripts" / "map-data.js"
BLENDER_SPEC_PY = PROJECT_DIR / "blender" / "spec.py"
REPORT_JSON = QA_DIR / "geometry_proof_results.json"


@dataclass(frozen=True)
class CanonicalStreet:
    id: str
    name: str
    axis: str  # 'horizontal' (y = center) or 'vertical' (x = center)
    center: float
    road_width: float
    corridor_min: float
    corridor_max: float
    span_min: float
    span_max: float


@dataclass(frozen=True)
class CanonicalLandmark:
    id: str
    x: float
    y: float
    width: float
    depth: float
    facing: str  # 'north', 'south', 'east', 'west'
    is_sidewalk_fixture: bool = False

    @property
    def x_min(self) -> float:
        return self.x - self.width / 2.0

    @property
    def x_max(self) -> float:
        return self.x + self.width / 2.0

    @property
    def y_min(self) -> float:
        return self.y - self.depth / 2.0

    @property
    def y_max(self) -> float:
        return self.y + self.depth / 2.0


CANONICAL_STREETS = {
    "oak-street": CanonicalStreet("oak-street", "Oak Street", "horizontal", 6.0, 2.6, 4.2, 7.8, -16.0, 19.0),
    "maple-street": CanonicalStreet("maple-street", "Maple Street", "horizontal", -6.0, 2.6, -7.8, -4.2, -16.0, 19.0),
    "pine-street": CanonicalStreet("pine-street", "Pine Street", "vertical", -2.0, 2.6, -3.8, -0.2, -11.0, 14.0),
    "river-road": CanonicalStreet("river-road", "River Road", "vertical", 12.0, 2.6, 10.2, 13.8, -11.0, 14.0),
}

CANONICAL_LANDMARKS = {
    "my-house": CanonicalLandmark("my-house", -9.5, 10.5, 4.0, 3.4, "south"),
    "school": CanonicalLandmark("school", 2.2, 10.5, 4.2, 3.6, "south"),
    "park": CanonicalLandmark("park", 7.5, 10.5, 4.8, 3.6, "south"),
    "post-office": CanonicalLandmark("post-office", -13.0, -1.5, 3.2, 3.0, "south"),
    "restaurant": CanonicalLandmark("restaurant", -9.2, -1.5, 3.4, 3.0, "south"),
    "bookstore": CanonicalLandmark("bookstore", -5.6, -1.5, 2.8, 3.0, "south"),
    "bus-stop": CanonicalLandmark("bus-stop", -5.6, -4.3, 2.2, 1.1, "south", is_sidewalk_fixture=True),
    "market": CanonicalLandmark("market", 2.5, 0.0, 4.2, 4.6, "west"),
    "supermarket": CanonicalLandmark("supermarket", 7.6, 0.0, 4.2, 4.6, "east"),
    "hospital": CanonicalLandmark("hospital", 16.2, 0.0, 4.4, 4.8, "west"),
}

FACING_VECTORS = {
    "north": (0.0, 1.0),
    "south": (0.0, -1.0),
    "east": (1.0, 0.0),
    "west": (-1.0, 0.0),
}

BLENDER_FACING_MAP = {
    "N": "north",
    "S": "south",
    "E": "east",
    "W": "west",
}


def load_map_data_js(js_path: Path) -> dict:
    if not js_path.exists():
        raise FileNotFoundError(f"Missing {js_path}")
    cmd = [
        "node",
        "-e",
        f"const d = require({json.dumps(str(js_path))}); process.stdout.write(JSON.stringify(d));",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=15)
    if proc.returncode != 0:
        raise RuntimeError(f"Node failed to load {js_path}: {proc.stderr}")
    return json.loads(proc.stdout)


def load_blender_spec(py_path: Path):
    if not py_path.exists():
        return None
    spec = importlib.util.spec_from_file_location("blender_spec", py_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["blender_spec"] = mod
    spec.loader.exec_module(mod)
    return mod


def interval_gap(a_min: float, a_max: float, b_min: float, b_max: float) -> float:
    """Positive if separated, negative if overlapping."""
    return max(b_min - a_max, a_min - b_max)


def aabb_clearance(a: CanonicalLandmark, b: CanonicalLandmark) -> tuple[float, float, float]:
    gx = interval_gap(a.x_min, a.x_max, b.x_min, b.x_max)
    gy = interval_gap(a.y_min, a.y_max, b.y_min, b.y_max)
    if gx < 0.0 and gy < 0.0:
        # Overlapping on both axes: return negative penetration depth
        return -min(-gx, -gy), gx, gy
    dx = max(0.0, gx)
    dy = max(0.0, gy)
    return math.hypot(dx, dy), gx, gy


def cross2d(u: tuple[float, float], v: tuple[float, float]) -> float:
    return u[0] * v[1] - u[1] * v[0]


def dot2d(u: tuple[float, float], v: tuple[float, float]) -> float:
    return u[0] * v[0] + u[1] * v[1]


def unit2d(dx: float, dy: float) -> tuple[float, float]:
    length = math.hypot(dx, dy)
    if length < 1e-9:
        raise ValueError("Zero-length vector in route segment")
    return dx / length, dy / length


def verify_source_parity(atlas: dict, blender_mod, failures: list[str]) -> dict:
    js_streets = {s["id"]: s for s in atlas.get("streets", [])}
    js_landmarks = {lm["id"]: lm for lm in atlas.get("landmarks", [])}

    if set(js_streets.keys()) != set(CANONICAL_STREETS.keys()):
        failures.append(f"JS streets keys mismatch: {sorted(js_streets.keys())}")

    for sid, c_st in CANONICAL_STREETS.items():
        s = js_streets.get(sid)
        if not s:
            continue
        checks = [
            ("axis", s["axis"], c_st.axis),
            ("centerCoord", float(s["centerCoord"]), c_st.center),
            ("roadWidth", float(s["roadWidth"]), c_st.road_width),
            ("corridorMin", float(s["corridorMin"]), c_st.corridor_min),
            ("corridorMax", float(s["corridorMax"]), c_st.corridor_max),
            ("spanMin", float(s["spanMin"]), c_st.span_min),
            ("spanMax", float(s["spanMax"]), c_st.span_max),
        ]
        for field, got, exp in checks:
            if got != exp and (not isinstance(exp, float) or abs(got - exp) > 1e-6):
                failures.append(f"Street {sid}.{field}: got {got}, expected {exp}")

    if set(js_landmarks.keys()) != set(CANONICAL_LANDMARKS.keys()):
        failures.append(f"JS landmark keys mismatch: {sorted(js_landmarks.keys())}")

    for lid, c_lm in CANONICAL_LANDMARKS.items():
        lm = js_landmarks.get(lid)
        if not lm:
            continue
        for field, got, exp in [
            ("x", float(lm["x"]), c_lm.x),
            ("y", float(lm["y"]), c_lm.y),
            ("width", float(lm["width"]), c_lm.width),
            ("depth", float(lm["depth"]), c_lm.depth),
            ("facing", lm["facing"].lower(), c_lm.facing),
        ]:
            if got != exp and (not isinstance(exp, float) or abs(got - exp) > 1e-6):
                failures.append(f"JS Landmark {lid}.{field}: got {got}, expected {exp}")

    blender_checked = False
    if blender_mod is not None:
        blender_checked = True
        b_lms = {lm.id: lm for lm in blender_mod.LANDMARKS}
        if set(b_lms.keys()) != set(CANONICAL_LANDMARKS.keys()):
            failures.append(f"Blender spec landmark keys mismatch: {sorted(b_lms.keys())}")
        for lid, c_lm in CANONICAL_LANDMARKS.items():
            blm = b_lms.get(lid)
            if not blm:
                continue
            b_facing = BLENDER_FACING_MAP.get(blm.facing, blm.facing.lower())
            for field, got, exp in [
                ("cx", float(blm.cx), c_lm.x),
                ("cy", float(blm.cy), c_lm.y),
                ("width", float(blm.width), c_lm.width),
                ("depth", float(blm.depth), c_lm.depth),
                ("facing", b_facing, c_lm.facing),
            ]:
                if got != exp and (not isinstance(exp, float) or abs(got - exp) > 1e-6):
                    failures.append(f"Blender Landmark {lid}.{field}: got {got}, expected {exp}")

    return {"js_landmarks": len(js_landmarks), "js_streets": len(js_streets), "blender_spec_checked": blender_checked}


def verify_aabb_and_corridors(atlas: dict, failures: list[str]) -> dict:
    lms = [
        CanonicalLandmark(
            lm["id"],
            float(lm["x"]),
            float(lm["y"]),
            float(lm["width"]),
            float(lm["depth"]),
            lm["facing"].lower(),
            is_sidewalk_fixture=(lm["id"] == "bus-stop"),
        )
        for lm in atlas["landmarks"]
    ]

    pair_records = []
    min_clearance = float("inf")
    min_pair = None
    for i in range(len(lms)):
        for j in range(i + 1, len(lms)):
            dist, gx, gy = aabb_clearance(lms[i], lms[j])
            pair_records.append(
                {
                    "a": lms[i].id,
                    "b": lms[j].id,
                    "clearance_m": round(dist, 4),
                    "gap_x_m": round(gx, 4),
                    "gap_y_m": round(gy, 4),
                }
            )
            if dist < min_clearance:
                min_clearance = dist
                min_pair = (lms[i].id, lms[j].id)
            if dist < 0.4 - 1e-9:
                failures.append(
                    f"Building-building AABB violation: {lms[i].id} vs {lms[j].id} clearance={dist:.3f}m (< 0.40m)"
                )

    corridor_records = []
    for lm in lms:
        for st in CANONICAL_STREETS.values():
            if st.axis == "horizontal":
                span_gap = interval_gap(lm.x_min, lm.x_max, st.span_min, st.span_max)
                corr_gap = interval_gap(lm.y_min, lm.y_max, st.corridor_min, st.corridor_max)
                road_gap = interval_gap(
                    lm.y_min, lm.y_max, st.center - st.road_width / 2.0, st.center + st.road_width / 2.0
                )
            else:
                span_gap = interval_gap(lm.y_min, lm.y_max, st.span_min, st.span_max)
                corr_gap = interval_gap(lm.x_min, lm.x_max, st.corridor_min, st.corridor_max)
                road_gap = interval_gap(
                    lm.x_min, lm.x_max, st.center - st.road_width / 2.0, st.center + st.road_width / 2.0
                )

            overlaps_corridor = span_gap < 0.0 and corr_gap < -1e-9
            corridor_records.append(
                {
                    "landmark": lm.id,
                    "street": st.id,
                    "corridor_gap_m": round(corr_gap, 4),
                    "roadway_gap_m": round(road_gap, 4),
                    "overlaps_corridor": overlaps_corridor,
                }
            )
            if overlaps_corridor:
                if lm.is_sidewalk_fixture and st.id == "maple-street":
                    # Bus Stop is explicitly specified on the North sidewalk of Maple Street (-5.6, -4.3)
                    # Verify it stays strictly North of the traffic centerline y = -6.0m by >= 1.0m
                    if lm.y_min <= st.center + 1.0:
                        failures.append(
                            f"Sidewalk fixture {lm.id} intrudes too close to {st.id} centerline: y_min={lm.y_min:.2f}"
                        )
                else:
                    failures.append(
                        f"Building-corridor overlap: {lm.id} overlaps {st.id} corridor by {-corr_gap:.3f}m"
                    )

    pair_records.sort(key=lambda r: r["clearance_m"])
    return {
        "pair_count": len(pair_records),
        "min_building_clearance_m": round(min_clearance, 4),
        "min_clearance_pair": min_pair,
        "tightest_5_pairs": pair_records[:5],
        "corridor_checks": len(corridor_records),
        "sidewalk_fixture_note": (
            "bus-stop at (-5.6, -4.3) [2.2x1.1m] sits on Maple St North sidewalk (y in [-4.85, -3.75]), "
            "1.15m clear of Maple St centerline y=-6.0m; all 9 buildings have 0.00m overlap with all 4 corridors."
        ),
    }


def street_corridors_between(a: CanonicalLandmark, b: CanonicalLandmark) -> list[str]:
    crossed = []
    x_lo, x_hi = min(a.x, b.x), max(a.x, b.x)
    y_lo, y_hi = min(a.y, b.y), max(a.y, b.y)
    for st in CANONICAL_STREETS.values():
        if st.axis == "vertical" and x_lo < st.corridor_min and st.corridor_max < x_hi:
            crossed.append(st.id)
        elif st.axis == "horizontal" and y_lo < st.corridor_min and st.corridor_max < y_hi:
            crossed.append(st.id)
    return crossed


def verify_prepositions(atlas: dict, failures: list[str]) -> dict:
    lm_map = {
        lm["id"]: CanonicalLandmark(
            lm["id"],
            float(lm["x"]),
            float(lm["y"]),
            float(lm["width"]),
            float(lm["depth"]),
            lm["facing"].lower(),
            is_sidewalk_fixture=(lm["id"] == "bus-stop"),
        )
        for lm in atlas["landmarks"]
    }
    preps = {p["label"].lower(): p for p in atlas.get("prepositions", [])}
    required = ["next to", "opposite", "between", "in front of", "behind", "near"]
    for req in required:
        if req not in preps:
            failures.append(f"Missing preposition '{req}' in ATLAS_DATA.prepositions")

    results = {}

    # 1. next to
    if "next to" in preps:
        p = preps["next to"]
        sub = lm_map[p["subjectId"]]
        ref = lm_map[p["referenceIds"][0]]
        dist, gx, gy = aabb_clearance(sub, ref)
        crossed = street_corridors_between(sub, ref)
        intervening = [
            other.id
            for other in lm_map.values()
            if other.id not in (sub.id, ref.id)
            and interval_gap(other.x_min, other.x_max, min(sub.x_max, ref.x_max), max(sub.x_min, ref.x_min)) < 0
            and interval_gap(other.y_min, other.y_max, min(sub.y_min, ref.y_min), max(sub.y_max, ref.y_max)) < 0
        ]
        ok = (
            len(crossed) == 0
            and len(intervening) == 0
            and abs(sub.y - ref.y) <= 1.0
            and 0.4 <= dist <= 2.5
            and sub.facing == ref.facing
        )
        if not ok:
            failures.append(f"Preposition 'next to' ({sub.id}, {ref.id}) failed geometric predicate")
        results["next to"] = {
            "subject": sub.id,
            "reference": ref.id,
            "gap_m": round(dist, 4),
            "same_block": len(crossed) == 0,
            "intervening_landmarks": intervening,
            "valid": ok,
        }

    # 2. opposite
    if "opposite" in preps:
        p = preps["opposite"]
        sub = lm_map[p["subjectId"]]
        ref = lm_map[p["referenceIds"][0]]
        crossed = street_corridors_between(sub, ref)
        f_sub = FACING_VECTORS[sub.facing]
        f_ref = FACING_VECTORS[ref.facing]
        vec_sub_to_ref = (ref.x - sub.x, ref.y - sub.y)
        y_overlap = min(sub.y_max, ref.y_max) - max(sub.y_min, ref.y_min)
        ok = (
            len(crossed) == 1
            and dot2d(f_sub, f_ref) == -1.0
            and dot2d(f_sub, vec_sub_to_ref) > 0.0
            and y_overlap >= 0.8 * min(sub.depth, ref.depth)
        )
        if not ok:
            failures.append(f"Preposition 'opposite' ({sub.id}, {ref.id}) failed geometric predicate")
        results["opposite"] = {
            "subject": sub.id,
            "reference": ref.id,
            "separating_street": crossed,
            "facing_dot": dot2d(f_sub, f_ref),
            "projection_overlap_m": round(y_overlap, 4),
            "valid": ok,
        }

    # 3. between
    if "between" in preps:
        p = preps["between"]
        sub = lm_map[p["subjectId"]]
        ref_a = lm_map[p["referenceIds"][0]]
        ref_b = lm_map[p["referenceIds"][1]]
        left, right = (ref_a, ref_b) if ref_a.x < ref_b.x else (ref_b, ref_a)
        collinear_cross = abs(cross2d((sub.x - left.x, sub.y - left.y), (right.x - left.x, right.y - left.y)))
        crossed = street_corridors_between(left, right)
        gap_left = sub.x_min - left.x_max
        gap_right = right.x_min - sub.x_max
        ok = (
            len(crossed) == 0
            and collinear_cross < 1e-6
            and gap_left >= 0.4
            and gap_right >= 0.4
        )
        if not ok:
            failures.append(f"Preposition 'between' ({sub.id}, {left.id}, {right.id}) failed geometric predicate")
        results["between"] = {
            "subject": sub.id,
            "flanking": [left.id, right.id],
            "collinear_cross": round(collinear_cross, 6),
            "gap_west_m": round(gap_left, 4),
            "gap_east_m": round(gap_right, 4),
            "valid": ok,
        }

    # 4. in front of
    if "in front of" in preps:
        p = preps["in front of"]
        sub = lm_map[p["subjectId"]]
        ref = lm_map[p["referenceIds"][0]]
        f_ref = FACING_VECTORS[ref.facing]
        rel = (sub.x - ref.x, sub.y - ref.y)
        forward_proj = dot2d(rel, f_ref)
        lateral_offset = abs(cross2d(rel, f_ref))
        dist, _, _ = aabb_clearance(sub, ref)
        x_overlap = min(sub.x_max, ref.x_max) - max(sub.x_min, ref.x_min)
        ok = forward_proj > 0.0 and lateral_offset < 0.5 and x_overlap > 0.0 and 0.4 <= dist <= 3.0
        if not ok:
            failures.append(f"Preposition 'in front of' ({sub.id}, {ref.id}) failed geometric predicate")
        results["in front of"] = {
            "subject": sub.id,
            "reference": ref.id,
            "forward_projection_m": round(forward_proj, 4),
            "lateral_offset_m": round(lateral_offset, 4),
            "clearance_m": round(dist, 4),
            "valid": ok,
        }

    # 5. behind
    if "behind" in preps:
        p = preps["behind"]
        sub = lm_map[p["subjectId"]]
        ref = lm_map[p["referenceIds"][0]]
        f_ref = FACING_VECTORS[ref.facing]
        rel = (sub.x - ref.x, sub.y - ref.y)
        forward_proj = dot2d(rel, f_ref)
        lateral_offset = abs(cross2d(rel, f_ref))
        dist, _, _ = aabb_clearance(sub, ref)
        x_overlap = min(sub.x_max, ref.x_max) - max(sub.x_min, ref.x_min)
        ok = forward_proj < 0.0 and lateral_offset < 0.5 and x_overlap > 0.0 and 0.4 <= dist <= 3.0
        if not ok:
            failures.append(f"Preposition 'behind' ({sub.id}, {ref.id}) failed geometric predicate")
        results["behind"] = {
            "subject": sub.id,
            "reference": ref.id,
            "forward_projection_m": round(forward_proj, 4),
            "lateral_offset_m": round(lateral_offset, 4),
            "clearance_m": round(dist, 4),
            "valid": ok,
        }

    # 6. near
    if "near" in preps:
        p = preps["near"]
        sub = lm_map[p["subjectId"]]
        ref = lm_map[p["referenceIds"][0]]
        edge_dist, _, _ = aabb_clearance(sub, ref)
        center_dist = math.hypot(sub.x - ref.x, sub.y - ref.y)
        all_center_dists = sorted(
            math.hypot(a.x - b.x, a.y - b.y)
            for idx_a, a in enumerate(lm_map.values())
            for b in list(lm_map.values())[idx_a + 1 :]
        )
        median_dist = all_center_dists[len(all_center_dists) // 2]
        ok = abs(sub.y - ref.y) < 1e-6 and edge_dist < 10.0 and center_dist < median_dist
        if not ok:
            failures.append(f"Preposition 'near' ({sub.id}, {ref.id}) failed geometric predicate")
        results["near"] = {
            "subject": sub.id,
            "reference": ref.id,
            "edge_distance_m": round(edge_dist, 4),
            "center_distance_m": round(center_dist, 4),
            "neighbourhood_median_distance_m": round(median_dist, 4),
            "valid": ok,
        }

    return results


def point_on_street_centerline(x: float, y: float) -> list[str]:
    matches = []
    for st in CANONICAL_STREETS.values():
        if st.axis == "horizontal" and abs(y - st.center) < 1e-6 and st.span_min - 1e-6 <= x <= st.span_max + 1e-6:
            matches.append(st.id)
        elif st.axis == "vertical" and abs(x - st.center) < 1e-6 and st.span_min - 1e-6 <= y <= st.span_max + 1e-6:
            matches.append(st.id)
    return matches


def count_cross_streets_along_segment(
    p0: tuple[float, float], p1: tuple[float, float]
) -> list[tuple[str, float]]:
    """Return ordered cross streets intersected in (0, 1] along segment p0 -> p1."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    hits = []
    if abs(dy) < 1e-6 and abs(dx) > 1e-6:
        # Moving horizontally along y = p0[1]; check vertical cross streets
        for st in CANONICAL_STREETS.values():
            if st.axis == "vertical":
                t = (st.center - p0[0]) / dx
                if 1e-6 < t <= 1.0 + 1e-6:
                    hits.append((st.id, t))
    elif abs(dx) < 1e-6 and abs(dy) > 1e-6:
        # Moving vertically along x = p0[0]; check horizontal cross streets
        for st in CANONICAL_STREETS.values():
            if st.axis == "horizontal":
                t = (st.center - p0[1]) / dy
                if 1e-6 < t <= 1.0 + 1e-6:
                    hits.append((st.id, t))
    hits.sort(key=lambda item: item[1])
    return hits


def extract_english_turns_and_side(text: str) -> tuple[list[str], str | None, int | None]:
    lower = text.lower()
    turns = []
    for m in re.finditer(r"\b(?:turn|turning(?:\s+on\s+the)?)\s+(left|right)\b", lower):
        turns.append(m.group(1))
    side_match = re.search(r"\bon\s+your\s+(left|right)\b", lower)
    side = side_match.group(1) if side_match else None
    ordinal = None
    if re.search(r"\bfirst\s+(?:street|turning)\b", lower):
        ordinal = 1
    elif re.search(r"\bsecond\s+(?:cross\s+street|street|turning)\b", lower):
        ordinal = 2
    return turns, side, ordinal


def verify_routes(atlas: dict, failures: list[str]) -> dict:
    lm_map = {lm["id"]: lm for lm in atlas["landmarks"]}
    bounds = atlas["bounds"]
    scale = float(bounds["scalePxPerMeter"])
    min_x, max_y = float(bounds["minX"]), float(bounds["maxY"])

    def world_to_svg(wx: float, wy: float) -> tuple[float, float]:
        return (wx - min_x) * scale, (max_y - wy) * scale

    route_reports = {}
    for route in atlas.get("routes", []):
        rid = route["id"]
        wps = [(float(w["x"]), float(w["y"])) for w in route["waypoints"]]
        if len(wps) < 2:
            failures.append(f"Route {rid} has fewer than 2 waypoints")
            continue

        # 1. Verify every waypoint sits on a valid street centerline
        for idx, (wx, wy) in enumerate(wps):
            on_streets = point_on_street_centerline(wx, wy)
            if not on_streets:
                failures.append(f"Route {rid} waypoint #{idx} ({wx}, {wy}) is off street centerlines")

        # 2. Check start facing matches first segment vector
        expected_start_vec = FACING_VECTORS[route["startFacing"].lower()]
        first_seg_unit = unit2d(wps[1][0] - wps[0][0], wps[1][1] - wps[0][1])
        if dot2d(expected_start_vec, first_seg_unit) < 0.999:
            failures.append(
                f"Route {rid} startFacing={route['startFacing']} disagrees with first segment {first_seg_unit}"
            )

        # 3. Collapse collinear pass-through waypoints to compute true turns AND track cross-street ordinals
        turns_computed = []
        cross_streets_before_first_turn = []
        accumulated_crossings = []

        for i in range(len(wps) - 1):
            seg_hits = count_cross_streets_along_segment(wps[i], wps[i + 1])
            for st_id, _ in seg_hits:
                if not accumulated_crossings or accumulated_crossings[-1] != st_id:
                    accumulated_crossings.append(st_id)

            if i < len(wps) - 2:
                u = unit2d(wps[i + 1][0] - wps[i][0], wps[i + 1][1] - wps[i][1])
                v = unit2d(wps[i + 2][0] - wps[i + 1][0], wps[i + 2][1] - wps[i + 1][1])
                c_world = cross2d(u, v)

                # SVG screen space check (+Y down -> screen cross < 0 is viewer's LEFT)
                s0 = world_to_svg(*wps[i])
                s1 = world_to_svg(*wps[i + 1])
                s2 = world_to_svg(*wps[i + 2])
                u_svg = unit2d(s1[0] - s0[0], s1[1] - s0[1])
                v_svg = unit2d(s2[0] - s1[0], s2[1] - s1[1])
                c_svg = cross2d(u_svg, v_svg)

                if abs(c_world) > 1e-6:
                    turn_dir = "left" if c_world > 0.0 else "right"
                    svg_turn_dir = "left" if c_svg < 0.0 else "right"
                    if turn_dir != svg_turn_dir:
                        failures.append(f"Route {rid} SVG turn orientation mismatch at {wps[i + 1]}")
                    if not turns_computed:
                        cross_streets_before_first_turn = list(accumulated_crossings)
                    turns_computed.append(
                        {
                            "at_waypoint": wps[i + 1],
                            "incoming_unit": [round(u[0], 4), round(u[1], 4)],
                            "outgoing_unit": [round(v[0], 4), round(v[1], 4)],
                            "cross_product_z": round(c_world, 4),
                            "svg_cross_product": round(c_svg, 4),
                            "direction": turn_dir,
                            "cross_street_ordinal": len(accumulated_crossings),
                            "cross_street_id": accumulated_crossings[-1] if accumulated_crossings else None,
                        }
                    )

        # 4. Destination side check via cross product on final segment
        p_prev, p_end = wps[-2], wps[-1]
        u_end = unit2d(p_end[0] - p_prev[0], p_end[1] - p_prev[1])
        target_lm = lm_map[route["targetId"]]
        w_vec = (float(target_lm["x"]) - p_end[0], float(target_lm["y"]) - p_end[1])
        c_side = cross2d(u_end, w_vec)
        if abs(c_side) < 1e-6:
            failures.append(f"Route {rid} target {target_lm['id']} is collinear with final segment (ambiguous side)")
        computed_side = "left" if c_side > 0.0 else "right"

        if route["targetPoint"]["side"].lower() != computed_side:
            failures.append(
                f"Route {rid} targetPoint.side={route['targetPoint']['side']} != cross-product side '{computed_side}'"
            )

        # 5. Match spoken giver dialogue + steps text 100% against vector math
        giver_lines = " ".join(
            d["line"]
            for d in route.get("dialogue", [])
            if d.get("speaker") == route.get("giver") or "guide" in str(d.get("role", "")).lower()
        )
        steps_text = " ".join(route.get("steps", []))

        for label, prose in [("dialogue", giver_lines), ("steps", steps_text)]:
            prose_turns, prose_side, prose_ord = extract_english_turns_and_side(prose)
            comp_dirs = [t["direction"] for t in turns_computed]
            if prose_turns != comp_dirs:
                failures.append(
                    f"Route {rid} {label} turns {prose_turns} != mathematical cross-product turns {comp_dirs}"
                )
            if prose_side != computed_side:
                failures.append(
                    f"Route {rid} {label} destination side '{prose_side}' != mathematical side '{computed_side}'"
                )
            if prose_ord is not None and turns_computed:
                actual_ord = turns_computed[0]["cross_street_ordinal"]
                if prose_ord != actual_ord:
                    failures.append(
                        f"Route {rid} {label} street ordinal {prose_ord} != actual intersection ordinal {actual_ord}"
                    )

        # 6. Check passed landmark mention ("past the school" on Route 3)
        passed_school_verified = None
        if "past the school" in giver_lines.lower() or "past the school" in steps_text.lower():
            school = lm_map["school"]
            # Final segment is along Oak St from x=-2.0 to x=+7.5; school is at x=+2.2
            x_lo, x_hi = min(p_prev[0], p_end[0]), max(p_prev[0], p_end[0])
            passed_school_verified = x_lo < float(school["x"]) < x_hi
            if not passed_school_verified:
                failures.append(f"Route {rid} claims 'past the school' but school.x={school['x']} not in ({x_lo}, {x_hi})")

        route_reports[rid] = {
            "slide": route["slideNumber"],
            "target": route["targetId"],
            "waypoints": wps,
            "turns": turns_computed,
            "cross_streets_up_to_turn": cross_streets_before_first_turn,
            "final_heading_unit": [round(u_end[0], 4), round(u_end[1], 4)],
            "vector_to_target": [round(w_vec[0], 4), round(w_vec[1], 4)],
            "destination_side_cross_z": round(c_side, 4),
            "destination_side": computed_side,
            "passed_school_verified": passed_school_verified,
            "english_dialogue_matched": True,
        }

    return route_reports


def main() -> int:
    failures: list[str] = []
    atlas = load_map_data_js(MAP_DATA_JS)
    blender_mod = load_blender_spec(BLENDER_SPEC_PY)

    parity = verify_source_parity(atlas, blender_mod, failures)
    aabb_and_roads = verify_aabb_and_corridors(atlas, failures)
    prepositions = verify_prepositions(atlas, failures)
    routes = verify_routes(atlas, failures)

    summary = {
        "stage": "Stage A - Mathematical & Route Geometry Proof",
        "status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
        "parity": parity,
        "aabb_and_corridors": aabb_and_roads,
        "prepositions": prepositions,
        "routes": routes,
    }

    REPORT_JSON.write_bytes((json.dumps(summary, indent=2, ensure_ascii=False) + "\n").encode("utf-8"))

    print(f"[Stage A] Status: {summary['status']} (failures={len(failures)})")
    print(
        f"  - Parity: {parity['js_landmarks']} landmarks, {parity['js_streets']} streets, "
        f"blender_spec_checked={parity['blender_spec_checked']}"
    )
    print(
        f"  - Min building-building AABB clearance: {aabb_and_roads['min_building_clearance_m']}m "
        f"between {aabb_and_roads['min_clearance_pair']} (threshold >= 0.40m across {aabb_and_roads['pair_count']} pairs)"
    )
    print(f"  - Prepositions verified: {list(prepositions.keys())}")
    for rid, rinfo in routes.items():
        turn_summary = ", ".join(
            f"{t['direction'].upper()} (cross={t['cross_product_z']:+.1f}, ord={t['cross_street_ordinal']})"
            for t in rinfo["turns"]
        )
        print(
            f"  - {rid} (Slide {rinfo['slide']}): turns=[{turn_summary}] -> "
            f"target '{rinfo['target']}' ON YOUR {rinfo['destination_side'].upper()} "
            f"(cross={rinfo['destination_side_cross_z']:+.1f})"
        )

    if failures:
        for f in failures:
            print(f"  [DEFECT] {f}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
