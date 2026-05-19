"""SafePath — safer walking routes in San Diego."""
from datetime import datetime

import streamlit as st
import folium
from streamlit_folium import st_folium

from routing import (
    load_graph,
    snap_to_nearest,
    compute_routes,
    PRESETS,
    ROUTE_COLORS,
)

st.set_page_config(
    page_title="SafePath",
    page_icon=":material/directions_walk:",
    layout="wide",
)

# ---- Session state ----
st.session_state.setdefault("pending_find", False)
st.session_state.setdefault("dark_resolved", False)
st.session_state.setdefault("use_extra_caution", False)


def _is_after_dark() -> bool:
    hour = datetime.now().hour
    return hour >= 18 or hour < 6


@st.dialog("It's after dark")
def _dark_caution_dialog():
    st.markdown(
        ":material/dark_mode: **Do you want to use Extra Caution for this trip?**"
    )
    st.write(
        "It's currently after dark in San Diego. "
        "Extra Caution switches to night scoring, which prioritizes "
        "well-lit streets and uses nighttime crime patterns."
    )
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        if st.button(
            ":material/shield: Yes, extra caution",
            type="primary",
            use_container_width=True,
            key="dark_yes",
        ):
            st.session_state.use_extra_caution = True
            st.session_state.dark_resolved = True
            st.rerun()
    with c2:
        if st.button(
            "No, keep day mode",
            use_container_width=True,
            key="dark_no",
        ):
            st.session_state.use_extra_caution = False
            st.session_state.dark_resolved = True
            st.rerun()


# ---- Sidebar ----
with st.sidebar:
    st.title(":material/directions_walk: SafePath")
    st.caption("Safer walking routes in San Diego")

    st.divider()

    preset_names = list(PRESETS.keys())
    start_name = st.selectbox("Start", preset_names, index=0, key="start")
    end_name = st.selectbox("Destination", preset_names, index=1, key="end")

    st.divider()

    is_night = st.toggle(":material/dark_mode: Night mode", value=False)

    st.divider()

    find = st.button(
        ":material/route: Find Routes",
        type="primary",
        use_container_width=True,
    )

    st.divider()
    st.caption("Scores: 0 = worst, 1 = best")
    st.caption("Data: SDPD calls, EPA walkability, city streetlights")
    st.caption("SafePath team — DS3 @ UC San Diego")

# ---- Load graph (cached after first run) ----
G = load_graph()

# ---- Handle Find Routes click ----
if find:
    if start_name == end_name:
        st.error("Start and destination must be different.")
        st.stop()
    st.session_state.pending_find = True
    st.session_state.dark_resolved = False
    st.session_state.use_extra_caution = False
    st.session_state.find_start = start_name
    st.session_state.find_end = end_name
    st.session_state.find_night_toggle = is_night

# ---- Dark caution check ----
if st.session_state.pending_find and not st.session_state.dark_resolved:
    if _is_after_dark() and not st.session_state.get("find_night_toggle", False):
        _dark_caution_dialog()
    else:
        st.session_state.dark_resolved = True

# ---- Compute routes once dark check is resolved ----
if st.session_state.pending_find and st.session_state.dark_resolved:
    sn = st.session_state.find_start
    en = st.session_state.find_end
    night_toggle = st.session_state.get("find_night_toggle", False)
    effective_night = night_toggle or st.session_state.use_extra_caution

    start_coords = PRESETS[sn]
    end_coords = PRESETS[en]

    orig = snap_to_nearest(G, *start_coords)
    dest = snap_to_nearest(G, *end_coords)

    with st.spinner("Computing routes..."):
        routes = compute_routes(G, orig, dest, effective_night)

    st.session_state.routes = routes
    st.session_state.meta = {
        "start_coords": start_coords,
        "end_coords": end_coords,
        "start_name": sn,
        "end_name": en,
        "is_night": effective_night,
        "extra_caution": st.session_state.use_extra_caution,
    }
    st.session_state.pending_find = False

# ---- Default view ----
if "routes" not in st.session_state:
    m = folium.Map(
        location=[32.7400, -117.1500],
        zoom_start=13,
        tiles="CartoDB positron",
    )
    for name, (lat, lon) in PRESETS.items():
        folium.CircleMarker(
            [lat, lon],
            radius=6,
            color="#3498db",
            fill=True,
            fill_opacity=0.7,
            tooltip=name,
        ).add_to(m)
    st_folium(m, use_container_width=True, height=600, key="default_map")
    st.info("Select a start and destination, then click **Find Routes**.")
    st.stop()

# ---- Display results from session state ----
routes = st.session_state.routes
meta = st.session_state.meta

# Extra caution banner
if meta.get("extra_caution"):
    st.warning(
        ":material/shield: **Extra Caution is on.** "
        "Routes use night scoring (well-lit streets, nighttime crime weights).",
        icon=":material/dark_mode:",
    )

center = [
    (meta["start_coords"][0] + meta["end_coords"][0]) / 2,
    (meta["start_coords"][1] + meta["end_coords"][1]) / 2,
]

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
    legend_cols[i].markdown(
        f"<span style='color:{color}; font-size:1.4em'>&#9679;</span> "
        f"**{name}**",
        unsafe_allow_html=True,
    )

st.divider()

# ---- Route comparison cards ----
st.subheader("Route Comparison")

time_label = "Night" if meta["is_night"] else "Day"
if meta.get("extra_caution"):
    time_label += " (Extra Caution)"
st.caption(f"Profile: {time_label}")

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
                c1.metric("Distance", f"{route['distance_km']:.2f} km")
                c2.metric("Walk time", f"{route['walk_min']:.0f} min")
                st.progress(
                    route["safety_score"],
                    text=f"Safety: {route['safety_score']:.0%}",
                )
                with st.expander("Score breakdown"):
                    st.markdown(f"Crime: **{route['avg_crime']:.2f}**")
                    st.markdown(f"Walkability: **{route['avg_walk']:.2f}**")
                    st.markdown(
                        f"Infrastructure: **{route['avg_infra']:.2f}**"
                    )
        else:
            st.warning(f"No {name.lower()} route found.")

# ---- Trade-off summary ----
safest = routes.get("Safest")
shortest = routes.get("Shortest")
if safest and shortest and safest["distance_km"] != shortest["distance_km"]:
    st.divider()
    extra_km = safest["distance_km"] - shortest["distance_km"]
    extra_min = safest["walk_min"] - shortest["walk_min"]
    safety_diff = safest["safety_score"] - shortest["safety_score"]

    if extra_km > 0:
        st.info(
            f"The safest route adds **{extra_km:.1f} km** "
            f"(+{extra_min:.0f} min) but scores "
            f"**{safety_diff:+.0%}** higher on safety."
        )
    elif extra_km < 0:
        st.success(
            "The safest route is shorter than the distance-only route "
            "because the shortest path crosses high-penalty edges."
        )

# ---- Disclaimer ----
st.divider()
st.caption(
    "SafePath uses historical SDPD calls, EPA walkability data, and city "
    "streetlight records. Scores reflect what the data suggests, not a "
    "guarantee of safety. Always use your own judgment."
)
