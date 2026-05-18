"""SafePath scoring and routing cost functions.

Extracted from notebooks/safety-score-edge.ipynb so the logic can be
imported by the Streamlit app and tested independently of the geospatial
stack (osmnx, geopandas).

All scores follow the convention: 1 = safest/best, 0 = worst.
"""
from __future__ import annotations

import math
from typing import Sequence

# ---------------------------------------------------------------------------
# Road class score mapping (OSM highway tag → pedestrian suitability)
# ---------------------------------------------------------------------------

ROAD_CLASS_SCORES: dict[str, float] = {
    "footway": 1.00,
    "pedestrian": 1.00,
    "path": 0.90,
    "cycleway": 0.85,
    "living_street": 0.80,
    "residential": 0.70,
    "unclassified": 0.60,
    "tertiary": 0.50,
    "tertiary_link": 0.50,
    "secondary": 0.35,
    "secondary_link": 0.35,
    "primary": 0.20,
    "primary_link": 0.20,
    "trunk": 0.10,
    "trunk_link": 0.10,
    "motorway": 0.00,
    "motorway_link": 0.00,
}

NEUTRAL_SCORE = 0.5

# ---------------------------------------------------------------------------
# Routing weight profiles
# ---------------------------------------------------------------------------

DAY_WEIGHTS = {"crime": 0.50, "walk": 0.25, "infra": 0.25}
NIGHT_WEIGHTS = {"crime": 0.45, "walk": 0.25, "infra": 0.30}


def get_weights(is_night: bool) -> dict[str, float]:
    """Return the feature-weight dict for the current time of day."""
    return NIGHT_WEIGHTS if is_night else DAY_WEIGHTS


# ---------------------------------------------------------------------------
# Buffer size selection
# ---------------------------------------------------------------------------

def get_buffer_size(route_length_m: float) -> str:
    """Pick the crime-score buffer column suffix based on total route length.

    Returns one of 'short', 'medium', or 'long'.
    """
    if route_length_m < 500:
        return "short"
    if route_length_m <= 2000:
        return "medium"
    return "long"


# ---------------------------------------------------------------------------
# Road class score lookup
# ---------------------------------------------------------------------------

def road_class_score(highway_type: str | list[str]) -> float:
    """Map an OSM highway tag (or list of tags) to a pedestrian suitability score.

    If the tag is a list (MultiDiGraph edge with multiple types), returns the
    maximum score (most pedestrian-friendly type wins).
    """
    if isinstance(highway_type, list):
        return max(
            ROAD_CLASS_SCORES.get(t, NEUTRAL_SCORE) for t in highway_type
        )
    return ROAD_CLASS_SCORES.get(highway_type, NEUTRAL_SCORE)


# ---------------------------------------------------------------------------
# Cost formulas
# ---------------------------------------------------------------------------

def composite_score(
    crime_score: float,
    walk_score: float,
    infra_score: float,
    is_night: bool,
) -> float:
    """Weighted average of per-edge feature scores.

    Returns a value in [0, 1] where 1 = safest.
    """
    w = get_weights(is_night)
    return (
        w["crime"] * crime_score
        + w["walk"] * walk_score
        + w["infra"] * infra_score
    )


def safety_cost(length: float, score: float, multiplier: float = 4) -> float:
    """Convert a safety score into a routing cost NetworkX can minimize.

    A perfectly safe edge (score=1) costs exactly its physical length.
    A worst-case edge (score=0) costs length * (1 + multiplier).
    """
    return length * (1 + multiplier * (1 - score))


def balanced_cost(length: float, score: float, multiplier: float = 2) -> float:
    """Balanced routing cost — same formula as safety_cost with a lower multiplier."""
    return safety_cost(length, score, multiplier)


# ---------------------------------------------------------------------------
# Tobler's Hiking Function (terrain-adjusted walking speed)
# ---------------------------------------------------------------------------

def tobler_speed(grade: float) -> float:
    """Tobler's Hiking Function: walking speed (m/s) adjusted for slope.

    grade is rise/run (e.g. 0.1 = 10% uphill, -0.05 = slight downhill).
    Peaks at ~1.4 m/s on a slight downhill (-0.05 grade).
    """
    return 1.4 * math.exp(-3.5 * abs(grade + 0.05))


def route_time_seconds(
    lengths: Sequence[float], grades: Sequence[float]
) -> float:
    """Estimate walking time in seconds for a sequence of edge lengths and grades."""
    total = 0.0
    for length, grade in zip(lengths, grades):
        speed = tobler_speed(grade)
        if speed > 0:
            total += length / speed
    return total
