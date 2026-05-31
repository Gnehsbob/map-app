"""
components/metrics_display.py
Animated KPI metric cards with trip-aware labelling.
"""

import streamlit as st


def render_metrics(metrics):
    """
    Display animated distance, fuel and cost cards.
    metrics dict must include: distance_km, liters_used, cost_zar, trip_label
    """
    st.markdown("""
    <style>
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(14px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .metrics-row {
        display: flex;
        gap: 14px;
        margin: 14px 0 10px 0;
    }
    .metric-card {
        flex: 1;
        background: linear-gradient(145deg, #0f1624, #111827);
        border: 1px solid #1f2d45;
        border-radius: 12px;
        padding: 18px 20px 14px;
        position: relative;
        overflow: hidden;
        animation: fadeSlideUp 0.5s ease both;
    }
    .metric-card:nth-child(1) { animation-delay: 0.05s; border-top: 2px solid #00f3ff55; }
    .metric-card:nth-child(2) { animation-delay: 0.15s; border-top: 2px solid #3b82f655; }
    .metric-card:nth-child(3) { animation-delay: 0.25s; border-top: 2px solid #10b98155; }
    .metric-card::before {
        content: '';
        position: absolute;
        top: -40px; right: -40px;
        width: 100px; height: 100px;
        border-radius: 50%;
        opacity: 0.04;
    }
    .metric-card:nth-child(1)::before { background: #00f3ff; }
    .metric-card:nth-child(2)::before { background: #3b82f6; }
    .metric-card:nth-child(3)::before { background: #10b981; }
    .metric-label {
        font-size: 0.68rem;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 1.75rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1;
        margin-bottom: 6px;
    }
    .metric-card:nth-child(1) .metric-value { color: #00f3ff; }
    .metric-card:nth-child(2) .metric-value { color: #60a5fa; }
    .metric-card:nth-child(3) .metric-value { color: #34d399; }
    .metric-sub {
        font-size: 0.72rem;
        color: #334155;
        margin-top: 4px;
    }
    .trip-info-bar {
        animation: fadeSlideUp 0.5s ease 0.35s both;
        background: rgba(0,243,255,0.04);
        border: 1px solid rgba(0,243,255,0.12);
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 0.78rem;
        color: #64748b;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .trip-info-bar span.accent { color: #00f3ff; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

    trip_label  = metrics.get("trip_label", "1 trip (one way)")
    one_way_km  = round(metrics["distance_km"] / metrics["trips"], 2)

    st.markdown(f"""
    <div class="trip-info-bar">
        <span class="accent">{trip_label}</span>
        &nbsp;·&nbsp; One-way distance: <span class="accent">{one_way_km} km</span>
        &nbsp;·&nbsp; Inland 95 @ R23.00 / L
    </div>
    <div class="metrics-row">
        <div class="metric-card">
            <div class="metric-label">Total Distance</div>
            <div class="metric-value">{metrics['distance_km']} km</div>
            <div class="metric-sub">{metrics['trips']} leg(s) × {one_way_km} km</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Fuel Consumption</div>
            <div class="metric-value">{metrics['liters_used']} L</div>
            <div class="metric-sub">Combined for all legs</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Est. Fuel Cost</div>
            <div class="metric-value">R {metrics['cost_zar']}</div>
            <div class="metric-sub">Inland 95 estimate</div>
        </div>
    </div>
    """, unsafe_allow_html=True)