# Status

> **TL;DR.** Crime, walkability, and street lights are cleaned. Scoring engine is functional with day/night profiles. Routing produces three distinct routes (fastest, safest, balanced) validated on 6+ test pairs across San Diego. Next: Ruhan builds Streamlit frontend; team prepares final demo and presentation. Bike lane data deferred to a future version.

> **Team norms ([28 April meeting](https://docs.google.com/document/d/1gufXZGHToZtFlsREL3u_rizqxXCKs3DR3LbKhO05fSc/edit?usp=sharing)):** post a Discord update after every meaningful change, and react to every message in `#safepath` so the sender knows it was seen.

_Last updated: end of Week 6 (2026-05-17). Previous snapshot: [`status/week4_status.md`](status/week4_status.md)._

Past weekly snapshots live in [`status/`](status/). This file is the single source of truth for "where are we right now."

## This week's owners

| Person | Task | Reference | Status |
| - | - | - | - |
| Matthew | Design the weighted score for safety + convenience | [`design_document.md`](design_document.md) §7-8 | in progress |
| Max | ~~Clean bike lane dataset~~ (deferred to future version) | -- | deferred |
| Ruhan | Feature engineering + initial scoring on sample routes (now includes lighting) | [`design_document.md`](design_document.md) §5-6 | not started |
| Ajay | Compare how different weights change route results | [`design_document.md`](design_document.md) §7 | blocked on Matthew |

## Big picture

Crime, walkability, and street lights are cleaned. Scoring engine is functional and routing is validated. Bike lane data was deferred to a future version. The next milestone is the Streamlit frontend.

## Done

| What | Where |
| - | - |
| Crime preprocessing | [`crime-df-preprocessing.ipynb`](../notebooks/crime-df-preprocessing.ipynb) → `crime_final_gdf.gpkg` |
| Walkability preprocessing | [`walkability-df-preprocessing.ipynb`](../notebooks/walkability-df-preprocessing.ipynb) → `walkability_final_gdf.gpkg` |
| Streetlight cleaning + validation | `src/data/get_streetlights.py` + `src/data/clean_streetlights.py` → `data/processed/streetlights/streetlights_processed.geojson` (55,506 active lights, validation + tie-out PASS, snapshot 2026-04-30) |
| UCSD Clery aggregates extracted + validated | `data/processed/ucsd_clery/ucsd_clery_stats_2022_2024.csv` (66 rows: 22 offenses × 3 years, all 5/5 validation + 5/5 source-tieout PASS). Source: UCSD Annual Security & Fire Safety Report 2025 §XVI. Use as **validator** for the daily-log scrape, not as a point feature — see [`docs/data/ucsd_crime/00_NEXT_SESSION.md`](data/ucsd_crime/00_NEXT_SESSION.md) §4. |
| Crime + walkability files shared | team [Google Drive](https://drive.google.com/drive/folders/1DSxQlvn6lq-D_tax9uDd42b5rNIIyQQ8?usp=sharing) |
| Technical documentation consolidated | `docs/design_document.md` (data pipeline, scoring, design decisions) |

## In progress

1. **Matthew** is drafting the weighting between crime, walkability, lighting, and road class.
2. **Ruhan** is wiring up the OSM walking graph and attaching crime + walkability features to a small test area. Lighting (L1 from [`FEATURE_CONTRACT.md`](data/streetlights/FEATURE_CONTRACT.md)) can be added on the same slice now that the source data is ready.

## Not started

1. Compute lighting features L1–L5 against OSM edges (waiting on UCSD campus polygon decision for L4).

## Blocked

| Who | What | Blocked on |
| - | - | - |
| Ajay | weight comparison | needs at least one draft scoring formula from Matthew |
| ~~Bike comfort feature~~ | Deferred to future version |
| Lighting L4 (`lighting_data_quality_flag`) | UCSD campus polygon source decision (SANGIS vs. hand-built bbox) |
| UCSD `campus_incident_score` (F10) | daily UCSD Police log scrape not yet downloaded ([`data/raw/ucsd_police_logs/logs_20260501.csv`](../data/raw/ucsd_police_logs/logs_20260501.csv) is empty) + location-string lookup table not yet built. See [`docs/data/ucsd_crime/00_NEXT_SESSION.md`](data/ucsd_crime/00_NEXT_SESSION.md) §5. |

## Open questions to resolve this week

1. Should the user choose a time of day (day vs night) in the app, or do we infer it from the system clock?
2. How do we label neighborhoods with very few SDPD calls? Truly safe, or underreported?
3. What is the default for a missing feature on an edge: drop the term, or use a neutral 0.5? (Lighting already has a built-in `0.5` fallback for UCSD-interior edges.)
4. UCSD campus polygon: SANGIS layer or hand-built bbox for v0?

## Pick this up if you have time

These do not need a specific owner. Anyone can grab one.

| Task | Why it helps |
| - | - |
| Open the cleaned `.gpkg` and `.geojson` files in a fresh notebook and call `.explore()` | sanity checks the cleaned data |
| Spot check 10 random crime addresses against [Google Maps](https://www.google.com/maps) | validates geocoding quality |
| Sketch the Streamlit result page on paper | unblocks the Week 6 UI work |

## Mentor meetings

| Date | Type | Key decisions |
| - | - | - |
| 2026-04-14 | Mentor (Vanshika) | Defined safety features; agreed on crime + walkability as core data sources |
| 2026-04-21 | Mentor (Vanshika) | Reviewed crime cleaning approach; approved disposition filtering strategy |
| 2026-04-28 | Mentor (Vanshika) | Set team norms (Discord updates, message reactions); reviewed streetlight data strategy |
| 2026-05-05 | Mentor (Vanshika) | Reviewed scoring engine progress; discussed day/night profile split |
| 2026-05-12 | Mentor (Vanshika) | Reviewed routing output; approved three-route approach (fastest/safest/balanced); planned Streamlit timeline |

All meetings include the full team. Vanshika provides weekly technical direction and reviews each teammate's output before merging.

## Where things live

| Type of thing | Lives in |
| - | - |
| Final code, instructions, project knowledge | this repo |
| Large processed data (crime, walkability) | team [Google Drive](https://drive.google.com/drive/folders/1DSxQlvn6lq-D_tax9uDd42b5rNIIyQQ8?usp=sharing) |
| Streetlight data | committed to the repo under `data/` |
| Quick chat | Discord |
| Meeting notes + brainstorming | Google Drive notes folder |
| Sprint timeline + design intent | [original design doc](https://docs.google.com/document/d/1gufXZGHToZtFlsREL3u_rizqxXCKs3DR3LbKhO05fSc/edit?usp=sharing) |
| GitHub crash course | [workshop slides](https://docs.google.com/presentation/d/1WPHBVzyirhDXo6mF61rogD_oO6OWuwoV/edit?slide=id.p1#slide=id.p1) |

## Capacity reminder

5 people, roughly 5 to 10 hours each per week. **Plan small.** One file or one notebook per person per week is plenty. Drop a note in Discord when you start something so two people do not pick up the same task.

## How to update this file

1. Edit the table for "This week's owners" first. Status column should read: `not started`, `in progress`, `blocked`, or `done`.
2. Move finished items into the "Done" table with a date.
3. Move new questions into "Open questions."
4. Commit straight to `main` if changes are small. Otherwise open a PR.

If you want a frozen snapshot of this week's status, copy this file into [`status/week5_status.md`](status/) before making big edits.
