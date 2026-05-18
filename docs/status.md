# Status

> **TL;DR.** Crime, walkability, and street lights are cleaned. Scoring engine is functional with day/night profiles. Routing produces three distinct routes (fastest, safest, balanced) validated on 6+ test pairs across San Diego. Next: Ruhan builds Streamlit frontend; team prepares final demo and presentation. Bike lane data deferred to a future version.

> **Team norms ([28 April meeting](https://docs.google.com/document/d/1gufXZGHToZtFlsREL3u_rizqxXCKs3DR3LbKhO05fSc/edit?usp=sharing)):** post a Discord update after every meaningful change, and react to every message so the sender knows it was seen.

_Last updated: end of Week 6 (2026-05-17). Previous snapshot: [`status/week4_status.md`](status/week4_status.md)._

Past weekly snapshots live in [`status/`](status/). This file is the single source of truth for "where are we right now."

## This week's owners

| Person | Task | Reference | Status |
| - | - | - | - |
| Matthew | Streetlights: combine road score + light score; add timing to routes | [`design_document.md`](design_document.md) §5-6 | in progress |
| Max | Double-check streetlight coverage; finalize safety scoring questions for app UX; UCSD campus crime status | [`design_document.md`](design_document.md) §5, §10 | in progress |
| Ruhan | Streamlit frontend: template design, layout, color scheme | `app/` (planned) | not started |
| Ajay | Balanced route: safety score cutoff + fastest from there; test 5 start/end pairs and screenshot results on Discord | [`design_document.md`](design_document.md) §7 | in progress |

## Big picture

Crime, walkability, and street lights are cleaned. Scoring engine is functional and routing is validated. Bike lane data was deferred to a future version. The next milestone is the Streamlit frontend.

## Done

| What | Where |
| - | - |
| Crime preprocessing | [`crime-df-preprocessing.ipynb`](../notebooks/crime-df-preprocessing.ipynb) → `crime_final_gdf.gpkg` |
| Walkability preprocessing | [`walkability-df-preprocessing.ipynb`](../notebooks/walkability-df-preprocessing.ipynb) → `walkability_final_gdf.gpkg` |
| Streetlight cleaning + validation | `src/data/get_streetlights.py` + `src/data/clean_streetlights.py` → `data/processed/streetlights/streetlights_processed.geojson` (55,506 active lights, validation + tie-out PASS, snapshot 2026-04-30) |
| UCSD Clery aggregates extracted + validated | `data/processed/ucsd_clery/ucsd_clery_stats_2022_2024.csv` (66 rows: 22 offenses × 3 years, all 5/5 validation + 5/5 source-tieout PASS). Source: UCSD Annual Security & Fire Safety Report 2025 §XVI. Use as **validator** for the daily-log scrape, not as a point feature. |
| Crime + walkability files shared | team [Google Drive](https://drive.google.com/drive/folders/1DSxQlvn6lq-D_tax9uDd42b5rNIIyQQ8?usp=sharing) |
| Technical documentation consolidated | `docs/design_document.md` (data pipeline, scoring, design decisions) |

## In progress

1. **Matthew** is combining streetlights (road score + light score: 30% of edges have real light data, 70% use road fallback) and adding route timing.
2. **Ruhan** is building the Streamlit frontend. First step: design a template with features, color scheme, layout, and pop-up interactions. Prompt will be shared on Discord for team input.
3. **Ajay** has initial sunset/sunrise detection working (suntime package; team is also considering the [astral](https://astral.readthedocs.io/en/latest/package.html) package as an alternative). Now testing balanced route logic (safety score cutoff approach) and running test routes across different start/end pairs.

## Not started

1. Compute lighting features L1–L5 against OSM edges (waiting on UCSD campus polygon decision for L4).

## Blocked

| Who | What | Blocked on |
| - | - | - |
| ~~Bike comfort feature~~ | Deferred to future version | -- |
| Lighting L4 (`lighting_data_quality_flag`) | UCSD campus polygon source decision (SANGIS vs. hand-built bbox) |
| UCSD `campus_incident_score` (F10) | daily UCSD Police log scrape not yet downloaded ([`data/raw/ucsd_police_logs/logs_20260501.csv`](../data/raw/ucsd_police_logs/logs_20260501.csv) is empty) + location-string lookup table not yet built. If campus crime data not available, mention during presentation as a next step (May 12 meeting). |
| Accessibility features | Tabled for now but noted as important (May 12 meeting). Would increase walkability score weighting. |

## Open questions to resolve this week

1. Naming: should we say "Safest" or "Extra Caution" for the safest route? (May 12 meeting suggested renaming.)
2. Balanced route: does it offer enough difference from fastest + safest on short-distance routes? (Vanshika, May 12 meeting)
3. Pre-route questions for the app: rush level, departure/arrival time, solo vs group, "It's after dark -- use Extra Caution?" pop-up (Max is designing the UX for these, May 12 meeting)
4. How do we label neighborhoods with very few SDPD calls? Truly safe, or underreported?
5. UCSD campus polygon: SANGIS layer or hand-built bbox for v0?

## Pick this up if you have time

These do not need a specific owner. Anyone can grab one.

| Task | Why it helps |
| - | - |
| Open the cleaned `.gpkg` and `.geojson` files in a fresh notebook and call `.explore()` | sanity checks the cleaned data |
| Spot check 10 random crime addresses against [Google Maps](https://www.google.com/maps) | validates geocoding quality |
| Draft the Streamlit prompt for Discord (features, color scheme, font, pop-ups, landing page) | gets team input on the UI before Ruhan builds it (May 12 meeting) |
| Explore the astral package as an alternative to suntime for sunrise/sunset | May 12 meeting suggested this as an option |

## Team meetings

All meetings are on Zoom with full attendance (Matthew, Max, Ruhan, Ajay, Vanshika). Full minutes are on the team [Google Drive](https://docs.google.com/document/d/1gufXZGHToZtFlsREL3u_rizqxXCKs3DR3LbKhO05fSc/edit?usp=sharing).

| Date | Key topics |
| - | - |
| 2026-04-13 (Mon, 6:30-7:30pm) | Kickoff: project overview and roadmap, intro to datasets (OSM, SD crime, POIs), team roles. Decided: meetings move to Tuesdays 9pm, Discord for communication, final product is Streamlit app |
| 2026-04-21 (Tue, 9:15-9:42pm) | Filter crime and walkability datasets to San Diego, clean and standardize formats, explore datasets to identify key variables. Next: all members set up GitHub + Streamlit |
| 2026-04-28 (Tue, 9:00-10:00pm) | Assigned work: Matthew (weighted scores), Ruhan (test scoring on sample routes), Max (cleaning remaining datasets), Ajay (comparing weighted scores). Team norms: Discord update after every change, react to every message |
| 2026-05-05 (Tue, 9:00-10:20pm) | Route options + scoring already generated. Streetlights: only covers ~30% of SD, need fallback variables (Matthew). Sunset timing: figure out what constitutes night, use a library (Ajay). Balanced route: test 50/50 vs 70/30 splits. User profiles tabled for now. UCSD crime data: confirm if SD data covers UCSD (Vanshika) |
| 2026-05-12 (Tue, 9:00-10:00pm) | Streetlights: combine road + light score, 30% real light / 70% road fallback (Matthew). Sunset timing: Ajay used suntime package, team considering astral as alternative. Balanced route: use safety score cutoff then take fastest (Ajay). Safety scoring questions for app UX (Max). Streamlit frontend: Ruhan to design template, share prompt on Discord. Naming: consider "Extra Caution" instead of "Safest". If UCSD crime data not available, mention as next step in presentation (Max). Accessibility: tabled but important |

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

4 students + project lead (Vanshika). **Plan small.** One file or one notebook per person per week is plenty. Drop a note in Discord when you start something so two people do not pick up the same task.

## How to update this file

1. Edit the table for "This week's owners" first. Status column should read: `not started`, `in progress`, `blocked`, or `done`.
2. Move finished items into the "Done" table with a date.
3. Move new questions into "Open questions."
4. Commit straight to `main` if changes are small. Otherwise open a PR.

If you want a frozen snapshot of this week's status, copy this file into [`status/week5_status.md`](status/) before making big edits.
