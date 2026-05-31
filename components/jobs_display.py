"""
components/jobs_display.py
Renders the animated job board panel — sector filter pills + job cards.
"""

import streamlit as st

# Lucide SVG snippets used inline in the card panel
_ICON_BUILDING = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'style="vertical-align:middle;margin-right:3px;opacity:0.6;">'
    '<rect x="2" y="7" width="20" height="14" rx="2"/>'
    '<path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>'
    '</svg>'
)

_ICON_MAPPIN = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'style="vertical-align:middle;margin-right:3px;opacity:0.6;">'
    '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/>'
    '<circle cx="12" cy="10" r="3"/>'
    '</svg>'
)

_ICON_SEARCH = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" '
    'style="opacity:0.3;">'
    '<circle cx="11" cy="11" r="8"/>'
    '<line x1="21" y1="21" x2="16.65" y2="16.65"/>'
    '</svg>'
)

_ICON_ALL = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'style="vertical-align:middle;margin-right:3px;">'
    '<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>'
    '<rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>'
    '</svg>'
)

_JOBS_CSS = """
<style>
@keyframes cardIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.jobs-header {
    display: flex; align-items: baseline; gap: 10px; margin: 18px 0 4px 0;
}
.jobs-title { font-size: 1.05rem; font-weight: 700; color: #e2e8f0; letter-spacing: -0.01em; }
.jobs-count { font-size: 0.7rem; color: #475569; text-transform: uppercase; letter-spacing: 0.08em; }
.pill-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 16px 0; }
.pill {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 4px 14px; border-radius: 20px; font-size: 0.72rem;
    font-weight: 600; letter-spacing: 0.05em; border: 1px solid transparent;
}
.pill svg { flex-shrink: 0; }
.jobs-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 12px; margin-bottom: 24px;
}
.job-card {
    background: linear-gradient(145deg, #0f1624, #111827);
    border: 1px solid #1f2d45; border-radius: 10px;
    padding: 14px 16px 12px; position: relative; overflow: hidden;
    animation: cardIn 0.45s ease both;
}
.job-card-accent { position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.job-sector-pill {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 0.65rem; font-weight: 700; letter-spacing: 0.08em;
    text-transform: uppercase; padding: 2px 8px; border-radius: 20px; margin-bottom: 8px;
}
.job-sector-pill svg { flex-shrink: 0; }
.job-title { font-size: 0.88rem; font-weight: 600; color: #e2e8f0; line-height: 1.35; margin-bottom: 4px; }
.job-meta  { display: flex; align-items: center; font-size: 0.73rem; color: #64748b; margin-bottom: 2px; }
.job-location { display: flex; align-items: center; font-size: 0.72rem; color: #475569; margin-bottom: 10px; }
.job-description {
    font-size: 0.72rem; color: #475569; line-height: 1.5; margin-bottom: 12px;
    display: -webkit-box; -webkit-line-clamp: 3;
    -webkit-box-orient: vertical; overflow: hidden;
}
.job-footer { display: flex; align-items: center; justify-content: space-between; margin-top: 4px; }
.job-date { font-size: 0.65rem; color: #334155; font-family: 'JetBrains Mono', monospace; }
.job-apply-btn {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 14px; border-radius: 6px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.04em;
    text-decoration: none; transition: all 0.18s;
}
.jobs-empty {
    text-align: center; padding: 40px 20px; color: #334155;
    font-size: 0.82rem; border: 1px dashed #1f2d45; border-radius: 10px;
}
.jobs-empty-icon { margin-bottom: 10px; display:flex; justify-content:center; }
</style>
"""

_ICON_ARROW = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="11" height="11" viewBox="0 0 24 24" '
    'fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">'
    '<line x1="5" y1="12" x2="19" y2="12"/>'
    '<polyline points="12 5 19 12 12 19"/>'
    '</svg>'
)


def _sector_pill_html(sector, color, icon, count):
    bg  = color + "18"
    bdr = color + "55"
    return (
        f'<div class="pill" style="background:{bg};border-color:{bdr};color:{color};">'
        f'{icon}{sector} <span style="opacity:0.5">({count})</span></div>'
    )


def _job_card_html(job, delay_s):
    color   = job["color"]
    icon    = job["icon"]
    sector  = job["sector"]
    bg_pill = color + "22"
    bg_btn  = color + "22"
    bdr_btn = color + "55"
    has_map = "lat" in job and "lon" in job
    map_badge = (
        "" if has_map else
        '<span style="font-size:0.6rem;color:#475569;padding:1px 6px;'
        'border:1px solid #1f2d45;border-radius:10px;margin-left:4px;">no pin</span>'
    )

    return f"""
<div class="job-card" style="animation-delay:{delay_s:.2f}s">
    <div class="job-card-accent" style="background:{color};opacity:0.7"></div>
    <div class="job-sector-pill" style="background:{bg_pill};color:{color};">{icon}{sector}</div>
    <div class="job-title">{job['title']}</div>
    <div class="job-meta">{_ICON_BUILDING}{job['company']}</div>
    <div class="job-location">{_ICON_MAPPIN}{job['location']}{map_badge}</div>
    <div class="job-description">{job['description']}</div>
    <div class="job-footer">
        <span class="job-date">{job.get('created','')}</span>
        <a href="{job['url']}" target="_blank" rel="noopener"
           class="job-apply-btn"
           style="background:{bg_btn};border:1px solid {bdr_btn};color:{color};">
           Apply {_ICON_ARROW}
        </a>
    </div>
</div>
"""


def render_jobs_panel(jobs, sector_filter="All"):
    st.markdown(_JOBS_CSS, unsafe_allow_html=True)

    if not jobs:
        st.markdown(f"""
        <div class="jobs-empty">
            <div class="jobs-empty-icon">{_ICON_SEARCH}</div>
            No live listings found. Check your Adzuna credentials or try again later.
        </div>
        """, unsafe_allow_html=True)
        return

    from collections import Counter
    from utils.jobs import SECTOR_COLORS, SECTOR_ICONS

    sector_counts = Counter(j["sector"] for j in jobs)
    all_sectors   = ["All"] + [s for s in ["IT", "Banking", "Healthcare", "Security", "Other"]
                                if s in sector_counts]

    visible = jobs if sector_filter == "All" else [j for j in jobs if j["sector"] == sector_filter]

    st.markdown(f"""
    <div class="jobs-header">
        <div class="jobs-title">Live Gauteng Opportunities</div>
        <div class="jobs-count">{len(visible)} of {len(jobs)} listings</div>
    </div>
    """, unsafe_allow_html=True)

    pills_html = '<div class="pill-row">'
    for s in all_sectors:
        if s == "All":
            cnt, color, icon = len(jobs), "#94a3b8", _ICON_ALL
        else:
            cnt   = sector_counts.get(s, 0)
            color = SECTOR_COLORS.get(s, "#94a3b8")
            icon  = SECTOR_ICONS.get(s, "")
        pills_html += _sector_pill_html(s, color, icon, cnt)
    pills_html += "</div>"
    st.markdown(pills_html, unsafe_allow_html=True)

    cards_html = '<div class="jobs-grid">'
    for i, job in enumerate(visible):
        cards_html += _job_card_html(job, delay_s=i * 0.04)
    cards_html += "</div>"
    st.markdown(cards_html, unsafe_allow_html=True)