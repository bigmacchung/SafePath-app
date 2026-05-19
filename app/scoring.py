"""SafePath scoring and routing cost functions.

Copied from max/audit-fixes branch (vanshika-s/SafePath).
All scores: 1 = safest/best, 0 = worst.
"""
from __future__ import annotations

import math
from typing import Sequence

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

DAY_WEIGHTS = {"crime": 0.50, "walk": 0.25, "infra": 0.25}
NIGHT_WEIGHTS = {"crime": 0.45, "walk": 0.25, "infra": 0.30}


def get_weights(is_night: bool) -> dict[str, float]:
    return NIGHT_WEIGHTS if is_night else DAY_WEIGHTS


def get_buffer_size(route_length_m: float) -> str:
    if route_length_m < 500:
        return "short"
    if route_length_m <= 2000:
        return "medium"
    return "long"


def road_class_score(highway_type: str | list[str]) -> float:
    if isinstance(highway_type, list):
        return max(
            ROAD_CLASS_SCORES.get(t, NEUTRAL_SCORE) for t in highway_type
        )
    return ROAD_CLASS_SCORES.get(highway_type, NEUTRAL_SCORE)


def composite_score(
    crime_score: float,
    walk_score: float,
    infra_score: float,
    is_night: bool,
) -> float:
    w = get_weights(is_night)
    return (
        w["crime"] * crime_score
        + w["walk"] * walk_score
        + w["infra"] * infra_score
    )


def safety_cost(length: float, score: float, multiplier: float = 4) -> float:
    return length * (1 + multiplier * (1 - score))


def balanced_cost(length: float, score: float, multiplier: float = 2) -> float:
    return safety_cost(length, score, multiplier)


def tobler_speed(grade: float) -> float:
    return 1.4 * math.exp(-3.5 * abs(grade + 0.05))


def route_time_seconds(
    lengths: Sequence[float], grades: Sequence[float],
) -> float:
    total = 0.0
    for length, grade in zip(lengths, grades):
        speed = tobler_speed(grade)
        if speed > 0:
            total += length / speed
    return total
