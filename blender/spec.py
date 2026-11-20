"""Single-source-of-truth coordinates, dimensions, and render specs for Greenleaf Neighbourhood."""

from dataclasses import dataclass
from pathlib import Path

BLENDER_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BLENDER_DIR.parent
OUTPUT_DIR = PROJECT_DIR / "assets" / "blender"
CC0_HDRI_PATH = PROJECT_DIR / "assets" / "cc0-sources" / "daylight_hdri.hdr"

# Coordinate system: North = +Y, East = +X, Ground = Z = 0.0 (meters).
STREETS = {
    "oak": {
        "name": "Oak Street",
        "axis": "x",
        "center": 6.0,
        "road_width": 2.6,
        "corridor_width": 3.6,
        "span": (-16.0, 19.0),
    },
    "maple": {
        "name": "Maple Street",
        "axis": "x",
        "center": -6.0,
        "road_width": 2.6,
        "corridor_width": 3.6,
        "span": (-16.0, 19.0),
    },
    "pine": {
        "name": "Pine Street",
        "axis": "y",
        "center": -2.0,
        "road_width": 2.6,
        "corridor_width": 3.6,
        "span": (-11.0, 14.0),
    },
    "river": {
        "name": "River Road",
        "axis": "y",
        "center": 12.0,
        "road_width": 2.6,
        "corridor_width": 3.6,
        "span": (-11.0, 14.0),
    },
}


@dataclass(frozen=True)
class LandmarkSpec:
    id: str
    label: str
    cx: float
    cy: float
    width: float   # East-West extent (world X)
    depth: float   # North-South extent (world Y)
    facing: str    # 'S' (-Y), 'W' (-X), 'E' (+X), 'N' (+Y)
    plinth_style: str = "lawn"
    allow_corridor_overlap: bool = False


LANDMARKS = (
    LandmarkSpec("my-house", "My House", -9.5, 10.5, 4.0, 3.4, "S", "lawn"),
    LandmarkSpec("school", "School", 2.2, 10.5, 4.2, 3.6, "S", "paving"),
    LandmarkSpec("park", "Park", 7.5, 10.5, 4.8, 3.6, "S", "lawn"),
    LandmarkSpec("post-office", "Post Office", -13.0, -1.5, 3.2, 3.0, "S", "paving"),
    LandmarkSpec("restaurant", "Restaurant", -9.2, -1.5, 3.4, 3.0, "S", "paving"),
    LandmarkSpec("bookstore", "Bookstore", -5.6, -1.5, 2.8, 3.0, "S", "paving"),
    LandmarkSpec("bus-stop", "Bus Stop", -5.6, -4.3, 2.2, 1.1, "S", "sidewalk", True),
    LandmarkSpec("market", "Market", 2.5, 0.0, 4.2, 4.6, "W", "paving"),
    LandmarkSpec("supermarket", "Supermarket", 7.6, 0.0, 4.2, 4.6, "E", "paving"),
    LandmarkSpec("hospital", "Hospital", 16.2, 0.0, 4.4, 4.8, "W", "paving"),
)

LANDMARK_BY_ID = {lm.id: lm for lm in LANDMARKS}

FACING_ROT_Z = {
    "S": 0.0,
    "E": 1.5707963267948966,
    "N": 3.141592653589793,
    "W": -1.5707963267948966,
}

BOARD_BOUNDS = {
    "x_min": -16.4,
    "x_max": 19.4,
    "y_min": -11.4,
    "y_max": 14.4,
}
