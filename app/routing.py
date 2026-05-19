"""Graph loading, route computation, geocoding, and nearest-node lookup."""
from __future__ import annotations

import gzip
import pickle
from pathlib import Path

import networkx as nx
import numpy as np
import pandas as pd
import streamlit as st
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

from scoring import (
    composite_score,
    safety_cost,
    balanced_cost,
    NEUTRAL_SCORE,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
GZ_PATH = DATA_DIR / "sd_walk_graph_scored.pkl.gz"

# Fallback for local dev with raw data
RAW_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"
GRAPH_PATH = RAW_DATA_DIR / "sd_walk_graph.graphml"
SCORES_PATH = RAW_DATA_DIR / "edge_scores_infrastructure.csv"

# San Diego bounding box for geocoding validation
SD_BOUNDS = {"min_lat": 32.53, "max_lat": 33.12, "min_lon": -117.33, "max_lon": -116.90}

EXAMPLE_ADDRESSES = [
    "Gaslamp Quarter, San Diego",
    "Balboa Park, San Diego",
    "Hillcrest, San Diego",
    "North Park, San Diego",
    "Pacific Beach, San Diego",
    "Ocean Beach, San Diego",
    "Normal Heights, San Diego",
    "City Heights, San Diego",
    "Golden Hill, San Diego",
    "Little Italy, San Diego",
]

ROUTE_COLORS = {
    "Safest": "#27ae60",
    "Balanced": "#f39c12",
    "Shortest": "#3498db",
}


@st.cache_data(show_spinner=False)
def geocode_address(address: str) -> dict | None:
    """Geocode an address to lat/lon within San Diego.

    Returns {"lat": ..., "lon": ..., "display": ...} or None if not found.
    """
    if not address or not address.strip():
        return None

    query = address.strip()
    if "san diego" not in query.lower() and "sd" not in query.lower():
        query += ", San Diego, CA"

    try:
        geolocator = Nominatim(user_agent="safepath-app", timeout=5)
        location = geolocator.geocode(query, exactly_one=True)
    except (GeocoderTimedOut, GeocoderUnavailable):
        return None

    if location is None:
        return None

    lat, lon = location.latitude, location.longitude
    if not (
        SD_BOUNDS["min_lat"] <= lat <= SD_BOUNDS["max_lat"]
        and SD_BOUNDS["min_lon"] <= lon <= SD_BOUNDS["max_lon"]
    ):
        return None

    return {"lat": lat, "lon": lon, "display": location.address}


def _safe_float(val, default=NEUTRAL_SCORE):
    if val is None:
        return default
    try:
        f = float(val)
        return default if np.isnan(f) else f
    except (ValueError, TypeError):
        return default


@st.cache_resource(show_spinner="Loading San Diego walking network...")
def load_graph() -> nx.MultiDiGraph:
    # Fast path: load pre-scored compressed graph
    if GZ_PATH.exists():
        with gzip.open(GZ_PATH, "rb") as f:
            return pickle.load(f)

    # Slow path: build from raw data (local dev only)
    if not GRAPH_PATH.exists():
        st.error("Graph data not found. Place sd_walk_graph_scored.pkl.gz in app/data/.")
        st.stop()

    G = nx.read_graphml(GRAPH_PATH)

    for _, data in G.nodes(data=True):
        data["x"] = float(data["x"])
        data["y"] = float(data["y"])

    scores_df = pd.read_csv(SCORES_PATH)
    scores_df["_key"] = (
        scores_df["u"].astype(int).astype(str)
        + "_"
        + scores_df["v"].astype(int).astype(str)
        + "_"
        + scores_df["key"].astype(int).astype(str)
    )
    score_lookup = scores_df.set_index("_key").to_dict("index")

    for u, v, k, data in G.edges(keys=True, data=True):
        length = float(data.get("length", 0))
        data["length"] = length

        s = score_lookup.get(f"{u}_{v}_{k}")
        crime_day = _safe_float(s.get("crime_score_medium_day") if s else None)
        crime_night = _safe_float(s.get("crime_score_medium_night") if s else None)
        walk = _safe_float(s.get("walk_score") if s else None)
        infra = _safe_float(s.get("infrastructure_score") if s else None)

        data["crime_day"] = crime_day
        data["crime_night"] = crime_night
        data["walk_score"] = walk
        data["infra_score"] = infra

        score_d = composite_score(crime_day, walk, infra, is_night=False)
        score_n = composite_score(crime_night, walk, infra, is_night=True)

        data["cost_safety_day"] = safety_cost(length, score_d)
        data["cost_safety_night"] = safety_cost(length, score_n)
        data["cost_balanced_day"] = balanced_cost(length, score_d)
        data["cost_balanced_night"] = balanced_cost(length, score_n)
        data["cost_shortest"] = length

    # Save compressed for next time
    GZ_PATH.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(GZ_PATH, "wb", compresslevel=9) as f:
        pickle.dump(G, f, protocol=pickle.HIGHEST_PROTOCOL)

    return G


@st.cache_resource
def _node_index(_G):
    nodes = list(_G.nodes(data=True))
    ids = [n[0] for n in nodes]
    coords = np.array([[n[1]["y"], n[1]["x"]] for n in nodes])
    return ids, coords


def snap_to_nearest(G, lat: float, lon: float) -> str:
    ids, coords = _node_index(G)
    dists = (coords[:, 0] - lat) ** 2 + (coords[:, 1] - lon) ** 2
    return ids[int(np.argmin(dists))]


def compute_routes(G, orig: str, dest: str, is_night: bool) -> dict:
    t = "night" if is_night else "day"
    profiles = {
        "Safest": f"cost_safety_{t}",
        "Balanced": f"cost_balanced_{t}",
        "Shortest": "cost_shortest",
    }
    results = {}
    for name, weight in profiles.items():
        try:
            path = nx.shortest_path(G, orig, dest, weight=weight)
            results[name] = _route_stats(G, path, is_night, name)
        except nx.NetworkXNoPath:
            results[name] = None
    return results


def _route_stats(G, path: list[str], is_night: bool, profile: str) -> dict:
    coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in path]

    total_length = 0.0
    w_crime, w_walk, w_infra = 0.0, 0.0, 0.0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        edge = G[u][v][min(G[u][v].keys())]
        length = edge["length"]
        total_length += length

        crime_key = "crime_night" if is_night else "crime_day"
        w_crime += edge[crime_key] * length
        w_walk += edge["walk_score"] * length
        w_infra += edge["infra_score"] * length

    if total_length > 0:
        avg_crime = w_crime / total_length
        avg_walk = w_walk / total_length
        avg_infra = w_infra / total_length
    else:
        avg_crime = avg_walk = avg_infra = NEUTRAL_SCORE

    overall = composite_score(avg_crime, avg_walk, avg_infra, is_night)
    walk_min = total_length / 1.4 / 60

    return {
        "coords": coords,
        "distance_km": total_length / 1000,
        "walk_min": walk_min,
        "safety_score": overall,
        "avg_crime": avg_crime,
        "avg_walk": avg_walk,
        "avg_infra": avg_infra,
        "profile": profile,
    }
