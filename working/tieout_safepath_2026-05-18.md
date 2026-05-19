# Source Tie-Out Report: SafePath

## Gate Decision: PROCEED

**Generated:** 2026-05-18
**Source:** `data/` directory (SafePath repo)
**Agent:** `agents/source-tieout.md` (Step 4.5)
**Dual-path method:** Path A (helpers/tieout_helpers.py read_source_direct + profile_dataframe) vs Path B (independent reader: pandas.read_csv, geopandas.read_file, sqlite3, json.load)
**Files checked:** 7

---

## Summary

All 7 data files verified via dual-path reads. Row counts, column names, and null totals match exactly across both paths. No data loading errors detected. Gate decision: PROCEED to analysis.

---

## File: edge_scores_infrastructure.csv

**Path A:** `read_source_direct()` -> 587,375 rows, 11 columns, 0 nulls
**Path B:** `pd.read_csv()` -> 587,375 rows, 11 columns, 0 nulls
**Status:** PASS

| Check | Path A | Path B | Status |
|-------|--------|--------|--------|
| Row count | 587,375 | 587,375 | PASS |
| Column count | 11 | 11 | PASS |
| Column names | match | match | PASS |
| Total nulls | 0 | 0 | PASS |

## File: crime_final_gdf.gpkg

**Path A:** `gpd.read_file()` -> 45,742 rows
**Path B:** `sqlite3` direct query -> 45,742 rows
**Status:** PASS

| Check | Path A (geopandas) | Path B (sqlite3) | Status |
|-------|-------------------|------------------|--------|
| Row count | 45,742 | 45,742 | PASS |

## File: walkability_final_gdf.gpkg

**Path A:** `gpd.read_file()` -> 1,462 rows
**Path B:** `sqlite3` direct query -> 1,462 rows
**Status:** PASS

| Check | Path A (geopandas) | Path B (sqlite3) | Status |
|-------|-------------------|------------------|--------|
| Row count | 1,462 | 1,462 | PASS |

## File: streetlights_processed.geojson

**Path A:** `json.load()` -> 55,506 features
**Path B:** `gpd.read_file()` -> 55,506 rows
**Status:** PASS

| Check | Path A (json) | Path B (geopandas) | Status |
|-------|--------------|-------------------|--------|
| Feature count | 55,506 | 55,506 | PASS |

## File: geocode_cache.json

**Path A:** `json.load()` -> 2,673 dict keys
**Path B:** regex count of `"lat":` entries -> 2,673
**Status:** PASS

| Check | Path A (dict) | Path B (regex) | Status |
|-------|--------------|----------------|--------|
| Entry count | 2,673 | 2,673 | PASS |

## File: edge_scores.csv

**Path A:** `read_source_direct()` -> 684,012 rows
**Path B:** `pd.read_csv()` -> 684,012 rows
**Status:** PASS

| Check | Path A | Path B | Status |
|-------|--------|--------|--------|
| Row count | 684,012 | 684,012 | PASS |

## File: streetlights_20260430.geojson (raw)

**Path A:** `json.load()` -> 56,049 features
**Path B:** `gpd.read_file()` -> 56,049 rows
**Status:** PASS

| Check | Path A (json) | Path B (geopandas) | Status |
|-------|--------------|-------------------|--------|
| Feature count | 56,049 | 56,049 | PASS |

---

## Files Skipped
- `sd_walk_graph.graphml`: GraphML parsed via xml.etree.ElementTree only (no second reader available). Node count: 251,999, Edge count: 684,012.
- `route_features_prototype.csv`: Schema-only test file (20 rows), not a production data file.
- `docs/references/*.csv`: Reference lookup tables, not analysis data.

## Recommendations
Gate decision is PROCEED. All production data files verified. No data loading issues detected.
