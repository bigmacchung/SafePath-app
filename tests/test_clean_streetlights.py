"""Unit tests for src/data/clean_streetlights.py."""
import pytest

from src.data import clean, in_bbox, SD_BBOX


def _make_feature(lon, lat, status="A", mapng="AB", sapobjnr="100"):
    """Helper to build a minimal GeoJSON feature."""
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [lon, lat]},
        "properties": {
            "STATUS": status,
            "MAPNG_STAT_CD": mapng,
            "SAPOBJNR": sapobjnr,
            "DRAWING_DATE": None,
        },
    }


def _make_fc(*features):
    return {"type": "FeatureCollection", "features": list(features)}


class TestInBbox:
    def test_inside(self):
        assert in_bbox(-117.1, 32.7) is True

    def test_outside_west(self):
        assert in_bbox(-118.0, 32.7) is False

    def test_outside_north(self):
        assert in_bbox(-117.1, 34.0) is False

    def test_on_boundary(self):
        assert in_bbox(SD_BBOX[0], SD_BBOX[1]) is True


class TestClean:
    def test_active_light_passes(self):
        fc = _make_fc(_make_feature(-117.1, 32.7))
        _, processed, counts = clean(fc)
        assert counts["kept"] == 1
        assert len(processed["features"]) == 1

    def test_inactive_status_dropped(self):
        fc = _make_fc(_make_feature(-117.1, 32.7, status="I"))
        _, processed, counts = clean(fc)
        assert counts["kept"] == 0
        assert counts["dropped_status_not_a"] == 1

    def test_wrong_mapng_dropped(self):
        fc = _make_fc(_make_feature(-117.1, 32.7, mapng="RM"))
        _, processed, counts = clean(fc)
        assert counts["kept"] == 0
        assert counts["dropped_mapng_not_kept"] == 1

    def test_out_of_bbox_dropped(self):
        fc = _make_fc(_make_feature(-118.5, 32.7))
        _, processed, counts = clean(fc)
        assert counts["kept"] == 0
        assert counts["dropped_out_of_bbox"] == 1

    def test_null_geometry_dropped(self):
        feature = {
            "type": "Feature",
            "geometry": None,
            "properties": {"STATUS": "A", "MAPNG_STAT_CD": "AB"},
        }
        _, processed, counts = clean(_make_fc(feature))
        assert counts["kept"] == 0
        assert counts["dropped_null_geometry"] == 1

    def test_duplicate_sapobjnr_flagged(self):
        f1 = _make_feature(-117.1, 32.7, sapobjnr="SAME")
        f2 = _make_feature(-117.0, 32.8, sapobjnr="SAME")
        _, processed, counts = clean(_make_fc(f1, f2))
        assert counts["kept"] == 2
        assert counts["dup_sapobjnr_flagged"] == 1
        flags = [f["properties"]["dup_sapobjnr_flag"] for f in processed["features"]]
        assert flags == [0, 1]

    def test_processed_schema(self):
        fc = _make_fc(_make_feature(-117.1, 32.7))
        _, processed, _ = clean(fc)
        props = processed["features"][0]["properties"]
        assert set(props.keys()) == {
            "sap_obj_nr", "status", "mapng_stat_cd",
            "drawing_date", "dup_sapobjnr_flag", "data_quality_flag",
        }
        assert props["data_quality_flag"] == "ok"

    def test_tieout(self):
        features = [
            _make_feature(-117.1, 32.7, sapobjnr="1"),
            _make_feature(-117.1, 32.7, status="I", sapobjnr="2"),
            _make_feature(-117.1, 32.7, mapng="RM", sapobjnr="3"),
            _make_feature(-118.5, 32.7, sapobjnr="4"),
        ]
        _, processed, counts = clean(_make_fc(*features))
        assert counts["raw"] == 4
        assert counts["kept"] == 1
        dropped = (
            counts["dropped_null_geometry"]
            + counts["dropped_out_of_bbox"]
            + counts["dropped_status_not_a"]
            + counts["dropped_mapng_not_kept"]
        )
        assert counts["raw"] - dropped == counts["kept"]
