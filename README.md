# SafePath

> **TL;DR.** SafePath recommends walking routes in San Diego that feel safer and more comfortable, not just the fastest. We score every street segment using crime, walkability, and lighting data, then pick three routes (fastest, safest, balanced) and explain why.

[![Status](https://img.shields.io/badge/status-active--development-yellow)](docs/status.md) [![Docs](https://img.shields.io/badge/docs-design_document-blue)](docs/design_document.md) [![Course](https://img.shields.io/badge/DS3-Spring_2026-purple)](https://www.ds3atucsd.com)

## What is SafePath

A route recommendation tool aimed at people who feel vulnerable walking alone. Students, women, anyone walking at night or in unfamiliar areas. The user enters a start and a destination, picks a preference (fastest, safest, balanced), and gets a route plus a plain English explanation of why it scored that way.

This is a quarter long student data science project run through [DS3 at UC San Diego](https://www.ds3atucsd.com).

## Start here (read in this order)

| # | Doc | What you get |
| - | - | - |
| 1 | This README | Project pitch, install, data setup |
| 2 | [`docs/design_document.md`](docs/design_document.md) | Data pipeline, scoring methodology, design decisions |
| 3 | [`docs/status.md`](docs/status.md) | Who is doing what, meeting log |

For meeting notes, see the team [Google Drive](https://docs.google.com/document/d/1gufXZGHToZtFlsREL3u_rizqxXCKs3DR3LbKhO05fSc/edit?usp=sharing) and [GitHub workshop slides](https://docs.google.com/presentation/d/1WPHBVzyirhDXo6mF61rogD_oO6OWuwoV/edit?slide=id.p1#slide=id.p1). Quick chat is on Discord.

## Environment setup

SafePath uses geospatial libraries (OSMnx, GeoPandas) that depend on C libraries. We recommend conda for a clean install.

**Option A: conda (recommended)**

```bash
git clone https://github.com/vanshika-s/SafePath.git
cd SafePath
conda create -n safepath python=3.11 -y
conda activate safepath
conda install -c conda-forge osmnx geopandas networkx geopy shapely fiona pyproj contextily -y
pip install streamlit suntime seaborn elevation
```

**Option B: pip only (if conda is not available)**

```bash
git clone https://github.com/vanshika-s/SafePath.git
cd SafePath
pip install -r requirements.txt
```

pip may fail on `osmnx` or `fiona` if the system is missing C dependencies (`GDAL`, `GEOS`, `PROJ`). If that happens, use conda.

**Verify the install:**

```bash
python -c "import osmnx, geopandas, networkx; print('OK')"
```

Then download data (next section), then open a notebook:

```bash
jupyter notebook notebooks/
```

**Run tests:**

```bash
pytest
```

46 unit tests cover the scoring module (`src/scoring/`) and the streetlight cleaning pipeline (`src/data/clean_streetlights.py`). No geospatial libraries needed -- tests run on any machine.

## Data setup (one time)

> **Why download instead of regenerating?** The crime preprocessing notebook geocodes thousands of addresses through Nominatim at 1 request per second, which takes hours. We share the cleaned outputs so you can skip that step.

### Step 1. Make the local data folder

Create `data/processed/` at the repo root. The notebooks read from `../data/processed/...` so the folder must live there. It is gitignored on purpose because the files are too large for GitHub.

```bash
mkdir -p data/processed
```

### Step 2. Download from Google Drive

Open the team folder: [SafePath processed data](https://drive.google.com/drive/folders/1DSxQlvn6lq-D_tax9uDd42b5rNIIyQQ8?usp=sharing).

Download all files into `data/processed/`:

| File | What it is | Needed by | Do not delete |
| - | - | - | - |
| `crime_final_gdf.gpkg` | geocoded crime points | scoring-engine | |
| `walkability_final_gdf.gpkg` | block group polygons with walkability scores | scoring-engine | |
| `geocode_cache.json` | cached Nominatim lookups | crime preprocessing | yes |
| `sd_walk_graph.graphml` | San Diego OSM walking network (684k edges) | scoring-engine, routing notebooks | |
| `edge_scores_infrastructure.csv` | per-edge feature scores (587k rows) | routing notebooks | |

### Step 3. Sanity check

Your folder should now look like:

```
data/processed/
  crime_final_gdf.gpkg
  walkability_final_gdf.gpkg
  geocode_cache.json
  sd_walk_graph.graphml
  edge_scores_infrastructure.csv
```

Done. The preprocessing notebooks need only the first three files. The scoring and routing notebooks need all five.

For deeper preprocessing details, see [`docs/design_document.md`](docs/design_document.md) sections 3-4.

## How to replicate results

After environment setup and data download, run the notebooks in this order:

| Step | Notebook | What it produces | Time |
| - | - | - | - |
| 1 | `notebooks/crime-df-preprocessing.ipynb` | `crime_final_gdf.gpkg` | hours (first run; uses geocode cache on reruns) |
| 2 | `notebooks/walkability-df-preprocessing.ipynb` | `walkability_final_gdf.gpkg` | seconds |
| 3 | `notebooks/scoring-engine.ipynb` | `edge_scores_infrastructure.csv` | 5-10 minutes |
| 4 | `notebooks/safety-score-edge.ipynb` | route comparison maps and statistics | 2-3 minutes |

Steps 1-2 are optional if you downloaded the processed files from Google Drive. Step 3 requires the processed files plus `sd_walk_graph.graphml`. Step 4 requires the edge scores file plus the graph.

All notebooks use relative paths (`../data/processed/...`) and should run from the `notebooks/` directory.

## Known limitations and bugs

| Issue | Severity | Details |
| - | - | - |
| Scoring formula differs across files | MEDIUM | `safety-score-edge.ipynb` uses `length * (1 + 4 * (1-score))`. `scoring-test.ipynb` now imports from `src/scoring/` for the canonical formula. |
| 493 crime points outside San Diego bbox | MEDIUM | 1.08% of geocoded crime points land outside the SD metro area (max lat 33.39, min lon -117.59). These are geocoding errors and do not affect routing. |
| Walkability has 1,462 rows vs. expected ~2,058 | MEDIUM | 596 block groups were lost during the TIGER merge. Not yet investigated. |
| 14.1% of graph edges have no feature scores | MEDIUM | 96,637 of 684,012 edges are unscored. The router treats them as neutral. |
| No Streamlit app yet | HIGH | `app/` is empty. Planned for Week 6-7. |
| Bike lane data deferred | LOW | Dropped from this iteration. May be added in a future version. |

## Repo layout

```
SafePath/
├── README.md                    you are here
├── requirements.txt
├── .gitignore
├── notebooks/
│   ├── crime-df-preprocessing.ipynb       crime data cleaning
│   ├── walkability-df-preprocessing.ipynb  walkability cleaning
│   ├── scoring-engine.ipynb               feature engineering (produces edge scores)
│   ├── scoring-test.ipynb                 scoring validation (imports from src/scoring/)
│   └── safety-score-edge.ipynb            routing engine (produces 3 routes)
├── docs/
│   ├── design_document.md       data pipeline, scoring, design decisions (main technical doc)
│   ├── status.md                who is doing what + meeting log
│   ├── status/                  weekly snapshots
│   ├── data/streetlights/       cleaning report, feature contract, coverage audit
│   └── references/              SDPD code books (CSV/PDF)
├── src/
│   ├── data/
│   │   ├── get_streetlights.py      ArcGIS REST download script
│   │   └── clean_streetlights.py    raw to processed streetlight pipeline
│   └── scoring/
│       └── scoring.py               cost formulas, weight profiles, road class scores
├── tests/
│   ├── test_scoring.py              unit tests for scoring module (34 tests)
│   └── test_clean_streetlights.py   unit tests for streetlight cleaning (12 tests)
├── data/
│   ├── raw/streetlights/        2026-04-30 GeoJSON snapshot + metadata
│   ├── processed/streetlights/  cleaned 55,506-point GeoJSON
│   └── prototype/               schema-only test CSV
└── app/                         planned, not yet built
```

## Reference materials

External docs we use to interpret the data:

| Source | Use |
| - | - |
| [SDPD Call Type Codes](https://data.sandiego.gov/datasets/police-calls-call-types/) | definitions for all 234 call type codes |
| [SDPD Disposition Codes](https://data.sandiego.gov/datasets/police-calls-disposition-codes/) | what each disposition letter means |
| [SDPD Priority Definitions (PDF)](https://seshat.datasd.org/police_calls_for_service/pd_cfs_priority_defs_datasd.pdf) | priority levels 0 to 4 and 9 |
| [EPA Smart Location Database v3.0 (PDF)](https://www.epa.gov/system/files/documents/2023-10/epa_sld_3.0_technicaldocumentationuserguide_may2021_0.pdf) | full data dictionary including `NatWalkInd` |

The first three are also bundled offline in [`docs/references/`](docs/references/).

## Team

Led by Vanshika, 4 students. This week's owners are tracked in [`docs/status.md`](docs/status.md).

## Where to read more

| You want to know about | Open |
| - | - |
| Data sources, cleaning, features, scoring, design decisions | [`design_document.md`](docs/design_document.md) |
| Why no additional streetlight data exists | [`EXTERNAL_DATASETS_AUDIT.md`](docs/data/streetlights/EXTERNAL_DATASETS_AUDIT.md) |
| Streetlight feature spec (L1-L5) | [`FEATURE_CONTRACT.md`](docs/data/streetlights/FEATURE_CONTRACT.md) |
| What is in flight this week | [`status.md`](docs/status.md) |
