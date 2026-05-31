"""
app.py — Gauteng Transit & Cost Engine

"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import streamlit.components.v1 as components

from components import render_sidebar, render_metrics, build_map_html, render_jobs_panel
from utils      import get_coordinates, get_osrm_route, calculate_transit_metrics
from utils.traffic_db import init_db
from utils.jobs import fetch_gauteng_jobs, geocode_jobs
from dotenv import load_dotenv

load_dotenv()


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title=None, page_icon=None)
init_db()

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0e1117; }
.block-container { padding-top: 0.3rem; padding-bottom: 0; max-width: 100%; }
iframe { border: none !important; border-radius: 0 !important; box-shadow: none !important; display: block; }
[data-testid="metric-container"] { display: none; }
.page-header { display: flex; align-items: baseline; gap: 12px; margin-bottom: 2px; animation: fadeIn 0.4s ease; }
.page-title { font-size: 1.4rem; font-weight: 700; color: #e2e8f0; letter-spacing: -0.02em; }
.page-caption { font-size: 0.75rem; color: #334155; letter-spacing: 0.06em; text-transform: uppercase; }
[data-testid="stSpinner"] { color: #00f3ff !important; }
.section-divider { border: none; border-top: 1px solid #1a2235; margin: 8px 0; }
.jobs-section-divider { border: none; border-top: 1px solid #1a2235; margin: 20px 0 4px 0; }
.legend-bar { display: flex; flex-wrap: wrap; gap: 10px; margin: 6px 0 14px 0; animation: fadeIn 0.5s ease; }
.legend-item { display: inline-flex; align-items: center; gap: 6px; font-size: 0.7rem; color: #64748b; letter-spacing: 0.04em; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; box-shadow: 0 0 6px currentColor; }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header"><div class="page-title">Gauteng Transit &amp; Cost Engine</div></div>
<div class="page-caption">Hardware-accelerated 3D vector map &nbsp;·&nbsp; Real-time fuel metrics &nbsp;·&nbsp; Live job opportunities</div>
<hr class="section-divider">
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
(
    start_input, end_input, vehicle, trips, generate,
    show_jobs, job_keyword, job_sector_filter, fetch_jobs, 
    show_metrics,
) = render_sidebar()

# ── Session state ──────────────────────────────────────────────────────────────
for key, default in {
    "cached_jobs":    [],
    "last_keyword":   "",
    "cached_route":   None,
    "cached_metrics": None,
    "first_load":     True,   # triggers auto-render on startup
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


default_start = os.getenv("START_LOCATION", "Johannesburg, South Africa")
default_end = os.getenv("END_LOCATION", "Pretoria, South Africa")

# ── Job fetch ──────────────────────────────────────────────────────────────────
if show_jobs and (fetch_jobs or job_keyword != st.session_state.last_keyword):
    with st.spinner(f"Fetching live Gauteng listings for '{job_keyword}'…"):
        raw_jobs = fetch_gauteng_jobs(keyword=job_keyword, results_per_page=25)
    if raw_jobs:
        with st.spinner("Geocoding job locations for map pins…"):
            enriched = geocode_jobs(raw_jobs, get_coordinates)
        st.session_state.cached_jobs  = enriched
        st.session_state.last_keyword = job_keyword
    else:
        st.warning("No listings returned — check your Adzuna credentials in utils/jobs.py")
        st.session_state.cached_jobs = []

jobs_for_map = st.session_state.cached_jobs if show_jobs else []

# ── Route computation — runs on first load OR when Generate is clicked ─────────
should_compute = generate or st.session_state.first_load

if should_compute:
    with st.spinner("Resolving addresses…"):
        start_data = get_coordinates(start_input)
        end_data   = get_coordinates(end_input)

    if not start_data or not end_data:
        st.error("Could not resolve one or both addresses. Try a more specific location.")
        st.stop()

    start_lat, start_lon, start_name = start_data
    end_lat,   end_lon,   end_name   = end_data

    with st.spinner("Calculating road route…"):
        route_result = get_osrm_route((start_lat, start_lon), (end_lat, end_lon))

    if not route_result:
        st.error("Routing failed. Please try again.")
        st.stop()

    geom, distance_m, duration_s = route_result

    route_geojson = {
        "type": "Feature", "properties": {},
        "geometry": {"type": "LineString", "coordinates": geom},
    }

    # Cache everything so the map survives reruns (job fetch, filter change, etc.)
    st.session_state.cached_route = {
        "route_geojson": route_geojson,
        "start_lat": start_lat, "start_lon": start_lon, "start_name": start_name,
        "end_lat":   end_lat,   "end_lon":   end_lon,   "end_name":   end_name,
        "midpoint_lat": (start_lat + end_lat) / 2,
        "midpoint_lon": (start_lon + end_lon) / 2,
        "distance_m": distance_m,
    }
    st.session_state.cached_metrics = calculate_transit_metrics(distance_m, vehicle, trips=trips)
    st.session_state.first_load = False   # never auto-compute again until page refresh

    # Silent TomTom traffic miner
    try:
        from utils.traffic_db import mine_realtime_traffic
        mine_realtime_traffic((start_lat, start_lon), (end_lat, end_lon),
                              duration_s, distance_m, route_geojson)
    except Exception:
        pass

# ── Render map + metrics (whenever a cached route exists) ──────────────────────
if st.session_state.cached_route:
    r = st.session_state.cached_route
    if show_metrics:
        
        render_metrics(st.session_state.cached_metrics)

    pinned = [j for j in jobs_for_map if "lat" in j]

    if show_jobs and jobs_for_map:
        st.markdown(f"""
        <div class="legend-bar">
            <span class="legend-item"><span class="legend-dot" style="background:#00f3ff;color:#00f3ff;"></span>IT / Tech</span>
            <span class="legend-item"><span class="legend-dot" style="background:#FFD700;color:#FFD700;"></span>Banking</span>
            <span class="legend-item"><span class="legend-dot" style="background:#50C878;color:#50C878;"></span>Healthcare</span>
            <span class="legend-item"><span class="legend-dot" style="background:#FF4D4D;color:#FF4D4D;"></span>Security</span>
            <span style="font-size:0.68rem;color:#334155;margin-left:6px;">
                · {len(pinned)} of {len(jobs_for_map)} listings mapped
            </span>
        </div>
        """, unsafe_allow_html=True)

    map_html = build_map_html(
        midpoint_lat=r["midpoint_lat"], midpoint_lon=r["midpoint_lon"],
        route_geojson=r["route_geojson"],
        start_lat=r["start_lat"], start_lon=r["start_lon"], start_name=r["start_name"],
        end_lat=r["end_lat"],     end_lon=r["end_lon"],     end_name=r["end_name"],
        job_pins=jobs_for_map,
    )
    components.html(map_html, height=620, scrolling=False)

# ── Job board panel ────────────────────────────────────────────────────────────
if show_jobs and st.session_state.cached_jobs:
    st.markdown('<hr class="jobs-section-divider">', unsafe_allow_html=True)
    render_jobs_panel(st.session_state.cached_jobs, sector_filter=job_sector_filter)
elif show_jobs and not st.session_state.cached_jobs:
    st.info("Toggle on and click **Fetch Live Jobs** in the sidebar to load opportunities.")
