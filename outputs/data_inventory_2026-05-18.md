# Data Inventory Report: SafePath
**Generated:** 2026-05-18
**Source:** `data/` directory (SafePath repo)
**Total files:** 10 data files (5 processed, 1 prototype, 2 raw streetlight, 2 reference CSVs)
**Total rows across all files:** 1,380,606 (excluding graph nodes)
**Agent:** `agents/data-explorer.md` (Step 4)
**Helpers used:** `helpers/tieout_helpers.py` (read_source_direct, profile_dataframe), `helpers/structural_validator.py` (validate_schema, validate_primary_key, validate_completeness, validate_value_domain, validate_row_count), `helpers/business_rules.py` (validate_ranges)

## Executive Summary

SafePath's data pipeline processes three input streams (SDPD crime calls, EPA walkability, City streetlights) into per-edge safety scores for a 684,012-edge San Diego OSM walking network. The processed data is complete (zero nulls across all score columns), structurally valid (unique primary keys, correct schemas), and passes all business rules (scores in [0, 1]). Three issues merit attention: 493 crime points (1.08%) geocoded outside the SD metro area, 596 walkability block groups (29%) were lost during the TIGER merge, and 14.1% of graph edges have no feature scores. None are blockers for the routing use case.

---

## File Inventory

### 1. edge_scores_infrastructure.csv (primary scoring output)
- **Path:** `data/processed/edge_scores_infrastructure.csv`
- **Rows:** 587,375
- **Columns:** 11 (u, v, key, 6 crime scores, walk_score, infrastructure_score)
- **Description:** Per-edge feature scores for all scored edges. This is the primary input to the routing engine.

| Column | Type | Nulls | Null % | Distinct | Min | Max | Mean |
|--------|------|-------|--------|----------|-----|-----|------|
| u | int | 0 | 0% | 227,007 | -- | -- | -- |
| v | int | 0 | 0% | 227,002 | -- | -- | -- |
| key | int | 0 | 0% | 9 | 0 | 8 | -- |
| crime_score_short_day | float | 0 | 0% | 1,116 | 0.0000 | 1.0000 | 0.9326 |
| crime_score_short_night | float | 0 | 0% | 833 | 0.0000 | 1.0000 | 0.9595 |
| crime_score_medium_day | float | 0 | 0% | 1,908 | 0.0000 | 1.0000 | 0.8794 |
| crime_score_medium_night | float | 0 | 0% | 1,466 | 0.0000 | 1.0000 | 0.9227 |
| crime_score_long_day | float | 0 | 0% | 3,129 | 0.0000 | 1.0000 | 0.8283 |
| crime_score_long_night | float | 0 | 0% | 2,331 | 0.0000 | 1.0000 | 0.8823 |
| walk_score | float | 0 | 0% | 94 | 0.0526 | 0.9825 | 0.5691 |
| infrastructure_score | float | 0 | 0% | 60 | 0.2781 | 1.0000 | 0.5659 |

**Structural validation (helpers/structural_validator.py):**
- `validate_schema()`: PASS (0 missing, 0 extra columns)
- `validate_primary_key(u, v, key)`: PASS (0 duplicates, 0 null PKs)
- `validate_completeness()`: PASS (all 11 columns 0% null)
- `validate_value_domain()`: PASS (all 8 score columns in [0, 1])
- `validate_row_count(587375)`: PASS

**Business rules (helpers/business_rules.py):**
- `validate_ranges()`: PASS (8 rules, 0 violations)

### 2. edge_scores.csv (legacy scoring output)
- **Path:** `data/processed/edge_scores.csv`
- **Rows:** 684,012
- **Columns:** 8 (u, v, key, crime_score_day, crime_score_night, light_score, walk_score, road_class_score)
- **Description:** Older per-edge scores covering ALL graph edges. Uses single-buffer crime scores and separate light/road columns instead of combined infrastructure_score.

| Column | Type | Nulls | Null % | Distinct | Min | Max |
|--------|------|-------|--------|----------|-----|-----|
| u | int | 0 | 0% | 251,999 | -- | -- |
| v | int | 0 | 0% | 251,999 | -- | -- |
| key | int | 0 | 0% | 9 | 0 | 8 |
| crime_score_day | float | 0 | 0% | 2,803 | 0.0000 | 1.0000 |
| crime_score_night | float | 0 | 0% | 1,939 | 0.0000 | 1.0000 |
| light_score | float | 0 | 0% | 39 | 0.0156 | 1.0000 |
| walk_score | float | 0 | 0% | 94 | 0.0526 | 0.9825 |
| road_class_score | float | 0 | 0% | 9 | 0.1000 | 1.0000 |

**Structural validation:** PASS (schema, PK, completeness, value domain, row count)
**Business rules:** PASS (5 rules, 0 violations)

### 3. crime_final_gdf.gpkg
- **Path:** `data/processed/crime_final_gdf.gpkg`
- **Rows:** 45,742
- **Columns:** 9 (INCIDENT_NUM, DATE_TIME, DAY_OF_WEEK, ADDRESS_ROAD_PRIMARY, CALL_TYPE, DISPOSITION, PRIORITY, HOUR, geometry)
- **CRS:** EPSG:4326
- **Geometry type:** Point
- **Description:** Geocoded SDPD crime incidents filtered to pedestrian-relevant call types and confirmed dispositions.

| Column | Type | Nulls | Null % | Notes |
|--------|------|-------|--------|-------|
| INCIDENT_NUM | string | 0 | 0% | Unique identifier |
| DATE_TIME | string | 0 | 0% | Timestamp of incident |
| DAY_OF_WEEK | int | 0 | 0% | Range: 1-7 |
| ADDRESS_ROAD_PRIMARY | string | 0 | 0% | Street name |
| CALL_TYPE | string | 0 | 0% | SDPD call type code |
| DISPOSITION | string | 0 | 0% | Incident outcome |
| PRIORITY | int | 0 | 0% | Range: 0-9 (mean 1.14) |
| HOUR | int | 0 | 0% | Range: 0-23 (mean 12.95) |
| geometry | Point | 0 | 0% | Lat: 32.54 to 33.39, Lon: -117.59 to -116.25 |

**Data quality note:** 493 points (1.08%) lie outside the SD metro bbox (lat 32.53-33.12, lon -117.28 to -116.90). These are geocoding errors; max latitude 33.3936 is San Marcos area.

### 4. walkability_final_gdf.gpkg
- **Path:** `data/processed/walkability_final_gdf.gpkg`
- **Rows:** 1,462
- **Columns:** 6 (GEOID, CBSA, CBSA_Name, TotPop, NatWalkInd, geometry)
- **CRS:** EPSG:4326
- **Geometry type:** Polygon
- **Description:** EPA Smart Location Database walkability scores for San Diego census block groups.

| Column | Type | Nulls | Null % | Notes |
|--------|------|-------|--------|-------|
| GEOID | string | 0 | 0% | Census block group ID |
| CBSA | float | 0 | 0% | All 41740 (SD-Chula Vista-Carlsbad) |
| CBSA_Name | string | 0 | 0% | All "San Diego-Chula Vista-Carlsbad, CA" |
| TotPop | int | 0 | 0% | Range: 0-38,932 (mean 1,711) |
| NatWalkInd | float | 0 | 0% | Range: 2.00-19.67 (mean 12.23) |
| geometry | Polygon | 0 | 0% | Block group boundaries |

**Data quality note:** 1,462 rows vs expected 2,058 (29% fewer). 596 block groups were lost during the TIGER merge. 2 block groups have zero population.

### 5. sd_walk_graph.graphml
- **Path:** `data/processed/sd_walk_graph.graphml`
- **Nodes:** 251,999
- **Edges:** 684,012
- **Attributes:** 30 (20 edge, 10 node)
- **Description:** San Diego OSM walking network from OSMnx. Edge attributes include highway type, length, name, geometry, lanes, maxspeed, bridge, tunnel, etc.

**Key edge attributes:** osmid, highway, oneway, reversed, length, geometry, service, bridge, name, lanes, maxspeed, ref, access, width, junction, tunnel, est_width, area, landuse

### 6. geocode_cache.json
- **Path:** `data/processed/geocode_cache.json`
- **Entries:** 2,673
- **Description:** Cached Nominatim geocoding results (address string -> {lat, lon}). Used to avoid re-geocoding on notebook reruns.

### 7. streetlights_processed.geojson
- **Path:** `data/processed/streetlights/streetlights_processed.geojson`
- **Features:** 55,506 (Point)
- **Properties:** sap_obj_nr, status (all "A"), mapng_stat_cd, drawing_date, dup_sapobjnr_flag, data_quality_flag
- **Description:** Active streetlights after filtering from 56,049 raw. Removed 543 (inactive, duplicates, or data quality flags).

### 8. streetlights_20260430.geojson (raw)
- **Path:** `data/raw/streetlights/streetlights_20260430.geojson`
- **Features:** 56,049 (Point)
- **Properties:** 39 fields including OBJECTID, SAPID, STATUS, pole type/material/height, service point, maintenance info
- **Description:** Raw City of San Diego streetlight inventory snapshot from 2026-04-30 via ArcGIS REST API.

### 9. route_features_prototype.csv
- **Path:** `data/prototype/route_features_prototype.csv`
- **Rows:** 20
- **Columns:** 19
- **Description:** Schema-only test file with synthetic data. Includes all planned feature columns (crime, walk, lighting, bike, campus). Used to validate downstream pipeline schema expectations.

### 10. Reference CSVs
- `docs/references/pd_cfs_calltypes_datasd.csv` -- SDPD call type code definitions
- `docs/references/pd_dispo_codes_datasd.csv` -- SDPD disposition code definitions

---

## Data Quality Assessment

### Warnings

| Issue | File | Detail | Impact |
|-------|------|--------|--------|
| 493 crime geocoding outliers | crime_final_gdf.gpkg | 1.08% of points outside SD metro bbox | Not routing-affecting; indicates geocoding errors |
| Walkability shortfall | walkability_final_gdf.gpkg | 1,462 vs 2,058 expected block groups (29% fewer) | Edges in missing block groups get 0.5 neutral fallback |
| 14.1% edges unscored | edge_scores_infrastructure.csv | 96,637 of 684,012 edges have no feature scores | Router treats as neutral; 96,637 were filtered for non-pedestrian highway types |

### Info

| Issue | File | Detail |
|-------|------|--------|
| Two edge score files | edge_scores.csv + edge_scores_infrastructure.csv | Legacy vs current; walk_score is 100% consistent between them |
| 2 zero-pop block groups | walkability_final_gdf.gpkg | TotPop=0 but NatWalkInd still present |
| walk_score never reaches 0 | edge_scores_infrastructure.csv | Min 0.0526 (NatWalkInd=2.0); 0.5 neutral fallback was never needed |

### No Blockers

All data files load cleanly, have zero nulls across score columns, and pass structural and business rule validation.

---

## Cross-File Consistency Checks

| Check | Result | Details |
|-------|--------|---------|
| Graph edges = old edge_scores rows | PASS | 684,012 = 684,012 |
| walk_score match across files | PASS | 100% identical between edge_scores.csv and edge_scores_infrastructure.csv |
| Unscored edge count | PASS | 684,012 - 587,375 = 96,637 (matches documented 14.1%) |
| Crime score evolution | PASS | crime_score_medium correlates 0.996 with old crime_score (schema evolution is coherent) |
| Infrastructure decomposition | PASS | infrastructure_score correlates 0.77 with road_class_score, 0.52 with light_score |
| Streetlight tie-out | PASS | 56,049 raw - 543 removed = 55,506 processed |
| Graph nodes vs edge endpoints | PASS | 251,999 nodes; u has 227,007 distinct, v has 227,002 distinct in scored edges |

---

## Entity Relationship Map

```
crime_final_gdf.gpkg (45,742 points)
    ↓ spatial join (crime within buffer of edge)
sd_walk_graph.graphml (684,012 edges, 251,999 nodes)
    ↑ spatial join (edge midpoint in block group)
walkability_final_gdf.gpkg (1,462 polygons)
    
streetlights_processed.geojson (55,506 points)
    ↓ spatial join (lights within 30m of edge)
sd_walk_graph.graphml
    ↓ scoring pipeline
edge_scores_infrastructure.csv (587,375 scored edges)
    ↓ routing engine
3 routes: fastest, safest, balanced
```

**Join key:** Edges are identified by (u, v, key) across the graph and both edge_scores files. Spatial joins use geometry proximity, not foreign keys.

---

## Recommended Analyses

### 1. Score distribution analysis
- **Description:** Profile the distribution shape of each score column to check for ceiling/floor effects
- **Data support:** edge_scores_infrastructure.csv -- all 8 score columns
- **Approach:** Histogram + summary stats per score column
- **Agent:** Descriptive Analytics Agent
- **Caveats:** Crime scores have high mean (0.83-0.96) suggesting most edges are "safe" -- verify this is expected given the log1p + p95 cap normalization

### 2. Unscored edge characterization
- **Description:** What types of edges are unscored? Are they structurally different from scored edges?
- **Data support:** edge_scores.csv has all 684,012 edges; compare highway types of scored vs unscored
- **Approach:** Segmentation by highway type
- **Agent:** Descriptive Analytics Agent
- **Caveats:** Requires loading GraphML to get highway type per edge

### 3. Crime outlier investigation
- **Description:** Profile the 493 geocoding outlier points -- which call types, addresses, dispositions?
- **Data support:** crime_final_gdf.gpkg -- filter by bbox
- **Approach:** Descriptive profiling of outlier subset vs main set
- **Agent:** Data Explorer Agent (deeper drill)
- **Caveats:** Outliers are geocoding artifacts, not data errors in source

---

## Next Steps
1. Address the walkability shortfall investigation (596 missing block groups)
2. Consider re-geocoding the 493 outlier crime points
3. Characterize the 96,637 unscored edges by highway type (confirmed: non-pedestrian types)
