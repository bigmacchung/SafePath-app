"""SafePath — safer walking routes in San Diego."""
import json
import urllib.request
from datetime import datetime, timezone, timedelta

import streamlit as st
import folium
from streamlit_folium import st_folium

from routing import (
    load_graph,
    snap_to_nearest,
    compute_routes,
    geocode_address,
    EXAMPLE_ADDRESSES,
    ROUTE_COLORS,
)

st.set_page_config(
    page_title="SafePath",
    page_icon=":material/directions_walk:",
    layout="wide",
)

# ---- Session state ----
st.session_state.setdefault("step", "pick")
st.session_state.setdefault("route_mode", None)

PT = timezone(timedelta(hours=-7))


@st.cache_data(ttl=86400, show_spinner=False)
def _get_sun_times() -> dict | None:
    try:
        url = (
            "https://api.sunrise-sunset.org/json"
            "?lat=32.7157&lng=-117.1611&formatted=0&date=today"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "SafePath/1.0"})
        resp = urllib.request.urlopen(req, timeout=5)
        data = json.loads(resp.read())
        if data.get("status") != "OK":
            return None
        r = data["results"]
        sunrise_utc = datetime.fromisoformat(r["sunrise"])
        sunset_utc = datetime.fromisoformat(r["sunset"])
        sunrise_local = sunrise_utc.astimezone(PT)
        sunset_local = sunset_utc.astimezone(PT)
        return {
            "sunrise": sunrise_local.strftime("%-I:%M %p"),
            "sunset": sunset_local.strftime("%-I:%M %p"),
            "sunset_hour": sunset_local.hour,
            "sunrise_hour": sunrise_local.hour,
        }
    except Exception:
        return None


def _is_after_dark() -> bool:
    sun = _get_sun_times()
    if sun:
        now = datetime.now(PT)
        sunset_today = now.replace(
            hour=sun["sunset_hour"], minute=0, second=0, microsecond=0
        )
        sunrise_today = now.replace(
            hour=sun["sunrise_hour"], minute=0, second=0, microsecond=0
        )
        return now >= sunset_today or now < sunrise_today
    hour = datetime.now().hour
    return hour >= 18 or hour < 6


# ---- Sidebar ----
with st.sidebar:
    st.title(":material/directions_walk: SafePath")
    st.caption("Safer walking routes in San Diego")

    sun = _get_sun_times()
    now_str = datetime.now(PT).strftime("%-I:%M %p")
    after_dark = _is_after_dark()

    with st.container(border=True):
        if after_dark:
            st.markdown(
                f":material/dark_mode: **{now_str}** — After dark"
            )
        else:
            st.markdown(
                f":material/wb_sunny: **{now_str}** — Daytime"
            )
        if sun:
            st.caption(
                f"Dawn {sun['sunrise']}  /  Dusk {sun['sunset']}"
            )

    st.divider()

    start_addr = st.text_input(
        ":material/location_on: Start address",
        placeholder="e.g. Gaslamp Quarter, San Diego",
        key="start_addr",
    )
    end_addr = st.text_input(
        ":material/flag: Destination",
        placeholder="e.g. Balboa Park, San Diego",
        key="end_addr",
    )

    with st.expander(":material/list: Example addresses"):
        for addr in EXAMPLE_ADDRESSES:
            st.caption(addr)

    st.write("")

    find = st.button(
        ":material/route: Find Routes",
        type="primary",
        use_container_width=True,
    )

    st.divider()

    with st.expander(":material/info: About"):
        st.caption("**Scoring**: 0 = worst, 1 = best")
        st.caption("**Data**: SDPD calls, EPA walkability, city streetlights")
        st.caption("**Team**: DS3 @ UC San Diego")

# ---- Load graph (cached after first run) ----
G = load_graph()

# ---- Step 1: User clicks Find Routes → geocode + validate ----
if find:
    if not start_addr or not end_addr:
        st.error("Enter both a start and destination address.", icon=":material/error:")
        st.stop()
    if start_addr.strip().lower() == end_addr.strip().lower():
        st.error("Start and destination must be different.", icon=":material/error:")
        st.stop()

    with st.status("Finding your route...", expanded=True) as status:
        st.write(":material/search: Looking up addresses...")
        geo_start = geocode_address(start_addr)
        geo_end = geocode_address(end_addr)

        if geo_start is None:
            status.update(label="Address not found", state="error")
            st.error(f"Could not find **{start_addr}** in San Diego.")
            st.stop()
        if geo_end is None:
            status.update(label="Address not found", state="error")
            st.error(f"Could not find **{end_addr}** in San Diego.")
            st.stop()

        st.write(f":material/check_circle: Found **{geo_start['display'][:60]}**")
        st.write(f":material/check_circle: Found **{geo_end['display'][:60]}**")
        status.update(label="Addresses found", state="complete", expanded=False)

    st.session_state.find_start = geo_start["display"]
    st.session_state.find_end = geo_end["display"]
    st.session_state.start_coords = (geo_start["lat"], geo_start["lon"])
    st.session_state.end_coords = (geo_end["lat"], geo_end["lon"])
    st.session_state.route_mode = None
    if "routes" in st.session_state:
        del st.session_state.routes
    if "meta" in st.session_state:
        del st.session_state.meta
    st.session_state.step = "choose"

# ---- Step 2: Choose route mode ----
if st.session_state.step == "choose":
    sn = st.session_state.get("find_start", "")
    en = st.session_state.get("find_end", "")
    after_dark = _is_after_dark()

    with st.container(border=True):
        if after_dark:
            st.warning(
                ":material/dark_mode: **It's after dark.** "
                "Do you want to use Extra Caution for this trip?",
                icon=":material/dark_mode:",
            )
        else:
            st.info(
                ":material/wb_sunny: **Daytime walking.** "
                "How would you like to walk?",
                icon=":material/wb_sunny:",
            )

        st.markdown(
            f":material/location_on: **{sn}**  \n"
            f":material/arrow_downward:  \n"
            f":material/flag: **{en}**"
        )

    st.write("")

    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown(":material/shield: **Extra Caution**")
            st.caption(
                "Prioritizes well-lit streets, avoids high-crime areas. "
                "Uses nighttime safety scoring. May add distance."
            )
            if st.button(
                ":material/shield: Extra Caution",
                use_container_width=True,
                type="primary" if after_dark else "secondary",
                key="btn_caution",
            ):
                st.session_state.route_mode = "caution"
                st.session_state.step = "compute"
                st.rerun()
    with c2:
        with st.container(border=True):
            st.markdown(":material/speed: **Faster Route**")
            st.caption(
                "Shortest walking distance with basic safety scoring. "
                "Uses daytime weights. Gets you there quickly."
            )
            if st.button(
                ":material/speed: Faster Route",
                use_container_width=True,
                type="secondary" if after_dark else "primary",
                key="btn_faster",
            ):
                st.session_state.route_mode = "faster"
                st.session_state.step = "compute"
                st.rerun()

    st.stop()

# ---- Step 3: Compute routes ----
if st.session_state.step == "compute":
    sn = st.session_state.find_start
    en = st.session_state.find_end
    mode = st.session_state.route_mode
    is_night = mode == "caution"

    start_coords = st.session_state.start_coords
    end_coords = st.session_state.end_coords

    with st.status("Computing routes...", expanded=True) as status:
        st.write(":material/location_on: Snapping to nearest road...")
        orig = snap_to_nearest(G, *start_coords)
        dest = snap_to_nearest(G, *end_coords)

        st.write(":material/route: Running pathfinder (3 profiles)...")
        routes = compute_routes(G, orig, dest, is_night)

        st.write(":material/check_circle: Routes ready!")
        status.update(label="Routes computed", state="complete", expanded=False)

    st.session_state.routes = routes
    st.session_state.meta = {
        "start_coords": start_coords,
        "end_coords": end_coords,
        "start_name": sn,
        "end_name": en,
        "is_night": is_night,
        "route_mode": mode,
    }
    st.session_state.step = "results"
    st.rerun()

# ---- Default view (no routes yet) ----
if "routes" not in st.session_state:
    st.write("")
    left, center_col, right = st.columns([1, 2, 1])
    with center_col:
        st.markdown(
            "### :material/directions_walk: Plan a safer walk in San Diego"
        )
        st.markdown(
            "Enter a start and destination in the sidebar, "
            "then click **Find Routes** to compare three walking profiles."
        )

        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(":material/shield: **Extra Caution**")
                st.caption("Avoids high-risk areas, prefers lit streets")
            with c2:
                st.markdown(":material/balance: **Balanced**")
                st.caption("Mix of safety and distance")
            with c3:
                st.markdown(":material/speed: **Fastest**")
                st.caption("Shortest walking path")

    st.write("")
    m = folium.Map(
        location=[32.7400, -117.1500],
        zoom_start=13,
        tiles="CartoDB positron",
    )
    st_folium(m, use_container_width=True, height=500, key="default_map")
    st.stop()

# ---- Display results ----
routes = st.session_state.routes
meta = st.session_state.meta

# Mode + trip header
with st.container(border=True):
    h1, h2 = st.columns([3, 1])
    with h1:
        st.markdown(
            f":material/location_on: **{meta['start_name']}**  \n"
            f":material/flag: **{meta['end_name']}**"
        )
    with h2:
        if meta["route_mode"] == "caution":
            st.markdown(":material/shield: **Extra Caution** mode")
            st.caption("Night scoring active")
        else:
            st.markdown(":material/speed: **Faster Route** mode")
            st.caption("Day scoring active")

center = [
    (meta["start_coords"][0] + meta["end_coords"][0]) / 2,
    (meta["start_coords"][1] + meta["end_coords"][1]) / 2,
]

# Tabs: Map and Comparison (AGENTS.md Layout Components pattern)
tab_map, tab_compare = st.tabs([
    ":material/map: Map",
    ":material/bar_chart: Compare Routes",
])

with tab_map:
    m = folium.Map(location=center, zoom_start=15, tiles="CartoDB positron")

    for name, route in routes.items():
        if route:
            folium.PolyLine(
                route["coords"],
                color=ROUTE_COLORS[name],
                weight=5,
                opacity=0.8,
                tooltip=(
                    f"{name}: {route['distance_km']:.1f} km, "
                    f"{route['walk_min']:.0f} min"
                ),
            ).add_to(m)

    folium.Marker(
        meta["start_coords"],
        tooltip=f"Start: {meta['start_name']}",
        icon=folium.Icon(color="green", icon="play", prefix="fa"),
    ).add_to(m)
    folium.Marker(
        meta["end_coords"],
        tooltip=f"End: {meta['end_name']}",
        icon=folium.Icon(color="red", icon="flag", prefix="fa"),
    ).add_to(m)

    st_folium(m, use_container_width=True, height=500, key="route_map")

    # Legend
    legend_cols = st.columns(3)
    for i, (name, color) in enumerate(ROUTE_COLORS.items()):
        route = routes.get(name)
        if route:
            legend_cols[i].markdown(
                f"<span style='color:{color}; font-size:1.3em'>&#9679;</span> "
                f"**{name}** — {route['distance_km']:.1f} km, "
                f"{route['walk_min']:.0f} min",
                unsafe_allow_html=True,
            )
        else:
            legend_cols[i].markdown(
                f"<span style='color:{color}; font-size:1.3em'>&#9679;</span> "
                f"**{name}** — no route",
                unsafe_allow_html=True,
            )

with tab_compare:
    cols = st.columns(3)
    for i, (name, route) in enumerate(routes.items()):
        with cols[i]:
            if route:
                with st.container(border=True):
                    st.markdown(
                        f"<span style='color:{ROUTE_COLORS[name]}; "
                        f"font-size:1.2em'>&#9679;</span> **{name}**",
                        unsafe_allow_html=True,
                    )
                    c1, c2 = st.columns(2)
                    c1.metric(
                        ":material/straighten: Distance",
                        f"{route['distance_km']:.2f} km",
                    )
                    c2.metric(
                        ":material/schedule: Walk time",
                        f"{route['walk_min']:.0f} min",
                    )
                    st.progress(
                        route["safety_score"],
                        text=f":material/shield: Safety: {route['safety_score']:.0%}",
                    )
                    with st.expander(":material/analytics: Score breakdown"):
                        b1, b2, b3 = st.columns(3)
                        b1.metric("Crime", f"{route['avg_crime']:.2f}")
                        b2.metric("Walkability", f"{route['avg_walk']:.2f}")
                        b3.metric("Infrastructure", f"{route['avg_infra']:.2f}")
            else:
                with st.container(border=True):
                    st.warning(
                        f"No {name.lower()} route found.",
                        icon=":material/warning:",
                    )

    # Trade-off summary
    caution = routes.get("Extra Caution")
    fastest = routes.get("Fastest")
    if caution and fastest and caution["distance_km"] != fastest["distance_km"]:
        st.write("")
        extra_km = caution["distance_km"] - fastest["distance_km"]
        extra_min = caution["walk_min"] - fastest["walk_min"]
        safety_diff = caution["safety_score"] - fastest["safety_score"]

        with st.container(border=True):
            if extra_km > 0:
                st.markdown(
                    f":material/compare_arrows: The extra caution route adds "
                    f"**{extra_km:.1f} km** (+{extra_min:.0f} min) but scores "
                    f"**{safety_diff:+.0%}** higher on safety."
                )
            elif extra_km < 0:
                st.markdown(
                    ":material/check_circle: The extra caution route is shorter "
                    "than the fastest route because the fastest path crosses "
                    "high-penalty edges."
                )

# ---- Disclaimer ----
st.divider()
st.caption(
    ":material/info: SafePath uses historical SDPD calls, EPA walkability data, "
    "and city streetlight records. Scores reflect what the data suggests, not a "
    "guarantee of safety. Always use your own judgment."
)
