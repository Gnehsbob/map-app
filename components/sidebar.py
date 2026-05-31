"""
components/sidebar.py
Sleek animated sidebar — navigation settings + trip multiplier + job hunter.
"""

import streamlit as st

VEHICLE_OPTIONS = ["sedan", "suv", "bakkie"]
VEHICLE_LABELS  = ["Sedan (e.g. VW Polo)", "SUV (e.g. Fortuner)", "Bakkie (e.g. Hilux)"]

JOB_KEYWORD_PRESETS = [
    "internship OR learnership",
    "internship",
    "learnership",
    "graduate programme",
    "entry level",
]

SECTOR_OPTIONS = ["All", "IT", "Banking", "Healthcare", "Security", "Other"]


def render_sidebar():
    st.markdown("""
    <style>
    [data-testid="stSidebar"] { background: #0a0d14; border-right: 1px solid #1a2235; }
    [data-testid="stSidebar"] .stTextInput input {
        background: #111827; border: 1px solid #1f2d45; color: #e2e8f0;
        border-radius: 6px; transition: border-color 0.2s;
    }
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: #00f3ff !important; box-shadow: 0 0 0 2px rgba(0,243,255,0.12);
    }
    div[data-testid="stSidebarContent"] label {
        color: #94a3b8 !important; font-size: 0.78rem !important;
        letter-spacing: 0.06em; text-transform: uppercase;
    }
    .sidebar-brand {
        font-size: 0.65rem; color: #334155; letter-spacing: 0.1em;
        text-transform: uppercase; margin-bottom: 1.2rem;
        padding-bottom: 0.8rem; border-bottom: 1px solid #1a2235;
    }
    .trip-badge {
        display: inline-block; background: rgba(0,243,255,0.08);
        border: 1px solid rgba(0,243,255,0.2); color: #00f3ff;
        font-size: 0.72rem; padding: 2px 10px; border-radius: 20px;
        margin-top: 4px; letter-spacing: 0.04em;
    }
    .sidebar-section {
        border-top: 1px solid #1a2235;
        margin: 14px 0 10px 0;
        padding-top: 12px;
    }
    .sidebar-section-label {
        font-size: 0.62rem; color: #334155;
        text-transform: uppercase; letter-spacing: 0.12em;
        margin-bottom: 10px; display: flex; align-items: center; gap: 6px;
    }
    .sidebar-section-label svg { opacity: 0.5; }
    div[data-testid="stSidebar"] button[kind="primary"],
    div[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #00f3ff22, #0066ff22) !important;
        border: 1px solid #00f3ff55 !important; color: #00f3ff !important;
        border-radius: 8px !important; font-size: 0.85rem !important;
        letter-spacing: 0.05em; transition: all 0.2s ease !important;
    }
    div[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #00f3ff33, #0066ff33) !important;
        border-color: #00f3ff !important; box-shadow: 0 0 16px rgba(0,243,255,0.2) !important;
    }
    .job-btn button {
        background: linear-gradient(135deg, #FFD70022, #ff990022) !important;
        border: 1px solid #FFD70055 !important; color: #FFD700 !important;
    }
    .job-btn button:hover {
        background: linear-gradient(135deg, #FFD70033, #ff990033) !important;
        border-color: #FFD700 !important; box-shadow: 0 0 16px rgba(255,215,0,0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    _icon_target = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>'
        '</svg>'
    )

    _icon_gauge = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 2a10 10 0 1 0 10 10"/>'
        '<path d="M12 6v6l4 2"/>'
        '</svg>'
    )

    with st.sidebar:
        st.markdown('<div class="sidebar-brand">Gauteng Transit Engine v2</div>', unsafe_allow_html=True)

        start_input = st.text_input("Origin",      value="Sandton City, Johannesburg", placeholder="e.g. Sandton City")
        end_input   = st.text_input("Destination", value="Pretoria, South Africa",     placeholder="e.g. OR Tambo International")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        vehicle_idx = st.selectbox(
            "Vehicle Profile",
            options=[0, 1, 2],
            format_func=lambda i: VEHICLE_LABELS[i],
        )
        vehicle = VEHICLE_OPTIONS[vehicle_idx]

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        trips = st.slider("Number of Trips", min_value=1, max_value=10, value=1, step=1,
                          help="1 = one way  ·  2 = return  ·  4 = 2x return  ·  etc.")

        if trips == 1:   badge = "1 trip — one way"
        elif trips == 2: badge = "2 trips — return"
        else:
            r     = trips // 2
            extra = " + 1 one-way" if trips % 2 else ""
            badge = f"{trips} trips — {r}x return{extra}"

        st.markdown(f'<div class="trip-badge">{badge}</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Fuel estimates toggle ──────────────────────────────────────────────
        st.markdown(f"""
        <div class="sidebar-section">
            <div class="sidebar-section-label">{_icon_gauge}&nbsp;Trip Metrics</div>
        </div>
        """, unsafe_allow_html=True)

        show_metrics = st.toggle(
            "Show fuel estimates",
            value=False,
            help="Shows distance, fuel consumption and cost after route generation.",
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        generate = st.button("Generate Route", use_container_width=True)

        # ── Job Hunter section ─────────────────────────────────────────────────
        st.markdown(f"""
        <div class="sidebar-section">
            <div class="sidebar-section-label">{_icon_target}&nbsp;Job Hunter</div>
        </div>
        """, unsafe_allow_html=True)

        show_jobs = st.toggle(
            "Show live job listings",
            value=False,
            help="Pulls active Gauteng internships & learnerships from Adzuna and overlays them on the map.",
        )

        job_keyword = st.selectbox(
            "Search keyword",
            options=JOB_KEYWORD_PRESETS,
            index=0,
            disabled=not show_jobs,
        )

        job_sector_filter = st.selectbox(
            "Filter by sector",
            options=SECTOR_OPTIONS,
            index=0,
            disabled=not show_jobs,
        )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        st.markdown('<div class="job-btn">', unsafe_allow_html=True)
        fetch_jobs = st.button(
            "Fetch Live Jobs",
            use_container_width=True,
            disabled=not show_jobs,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    return (
        start_input, end_input, vehicle, trips, generate,
        show_jobs, job_keyword, job_sector_filter, fetch_jobs,
        show_metrics,   # ← was missing from return tuple
    )