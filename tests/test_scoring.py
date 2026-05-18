"""Unit tests for src/scoring — cost formulas, weight profiles, road class scores."""
import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from scoring import (
    ROAD_CLASS_SCORES,
    DAY_WEIGHTS,
    NIGHT_WEIGHTS,
    get_weights,
    get_buffer_size,
    road_class_score,
    safety_cost,
    balanced_cost,
    composite_score,
    tobler_speed,
    route_time_seconds,
)


class TestSafetyCost:
    def test_perfect_score_equals_length(self):
        assert safety_cost(100, 1.0) == 100.0

    def test_worst_score_is_five_times_length(self):
        assert safety_cost(100, 0.0) == 500.0

    def test_mid_score(self):
        assert safety_cost(100, 0.5) == 300.0

    def test_zero_length(self):
        assert safety_cost(0, 0.5) == 0.0

    def test_custom_multiplier(self):
        assert safety_cost(100, 0.0, multiplier=8) == 900.0


class TestBalancedCost:
    def test_perfect_score(self):
        assert balanced_cost(100, 1.0) == 100.0

    def test_worst_score_is_three_times_length(self):
        assert balanced_cost(100, 0.0) == 300.0

    def test_lower_multiplier_than_safety(self):
        length, score = 200, 0.3
        assert balanced_cost(length, score) < safety_cost(length, score)


class TestCompositeScore:
    def test_day_weights_sum_to_one(self):
        assert sum(DAY_WEIGHTS.values()) == pytest.approx(1.0)

    def test_night_weights_sum_to_one(self):
        assert sum(NIGHT_WEIGHTS.values()) == pytest.approx(1.0)

    def test_perfect_scores_give_one(self):
        assert composite_score(1.0, 1.0, 1.0, is_night=False) == pytest.approx(1.0)
        assert composite_score(1.0, 1.0, 1.0, is_night=True) == pytest.approx(1.0)

    def test_zero_scores_give_zero(self):
        assert composite_score(0.0, 0.0, 0.0, is_night=False) == pytest.approx(0.0)

    def test_night_increases_infra_weight(self):
        crime, walk, infra = 0.5, 0.5, 1.0
        day = composite_score(crime, walk, infra, is_night=False)
        night = composite_score(crime, walk, infra, is_night=True)
        assert night > day


class TestGetWeights:
    def test_day(self):
        w = get_weights(is_night=False)
        assert w["crime"] == 0.50
        assert w["infra"] == 0.25

    def test_night(self):
        w = get_weights(is_night=True)
        assert w["crime"] == 0.45
        assert w["infra"] == 0.30


class TestGetBufferSize:
    def test_short_route(self):
        assert get_buffer_size(300) == "short"

    def test_medium_route(self):
        assert get_buffer_size(1000) == "medium"

    def test_long_route(self):
        assert get_buffer_size(3000) == "long"

    def test_boundary_500(self):
        assert get_buffer_size(499) == "short"
        assert get_buffer_size(500) == "medium"

    def test_boundary_2000(self):
        assert get_buffer_size(2000) == "medium"
        assert get_buffer_size(2001) == "long"


class TestRoadClassScore:
    def test_footway(self):
        assert road_class_score("footway") == 1.00

    def test_pedestrian(self):
        assert road_class_score("pedestrian") == 1.00

    def test_residential(self):
        assert road_class_score("residential") == 0.70

    def test_motorway(self):
        assert road_class_score("motorway") == 0.00

    def test_unknown_returns_neutral(self):
        assert road_class_score("service") == 0.5

    def test_list_returns_max(self):
        assert road_class_score(["residential", "footway"]) == 1.00

    def test_all_entries_in_zero_one(self):
        for tag, score in ROAD_CLASS_SCORES.items():
            assert 0.0 <= score <= 1.0, f"{tag} score {score} out of range"


class TestToblerSpeed:
    def test_flat_ground(self):
        speed = tobler_speed(0.0)
        assert 1.0 < speed < 1.5

    def test_steep_uphill_is_slower(self):
        assert tobler_speed(0.2) < tobler_speed(0.0)

    def test_slight_downhill_is_fastest(self):
        assert tobler_speed(-0.05) > tobler_speed(0.0)

    def test_always_positive(self):
        for grade in [-0.3, -0.1, 0.0, 0.1, 0.3]:
            assert tobler_speed(grade) > 0


class TestRouteTimeSeconds:
    def test_flat_route(self):
        lengths = [100, 200, 150]
        grades = [0.0, 0.0, 0.0]
        t = route_time_seconds(lengths, grades)
        assert t > 0
        flat_speed = tobler_speed(0.0)
        assert t == pytest.approx(450 / flat_speed)

    def test_uphill_takes_longer(self):
        flat = route_time_seconds([1000], [0.0])
        uphill = route_time_seconds([1000], [0.15])
        assert uphill > flat

    def test_empty_route(self):
        assert route_time_seconds([], []) == 0.0
