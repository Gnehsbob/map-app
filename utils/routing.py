"""
utils/routing.py
Geocoding (Photon) and route-calculation (OSRM) helpers.
"""

from __future__ import annotations
from typing import Optional, Tuple, List
import requests
import streamlit as st
import re
import os

_URL_PATTERN = re.compile(r'https?://|www\.|\.co\.za|\.com|\.net|\.org')


def get_coordinates(address: str) -> Optional[Tuple[float, float, str]]:
    """Resolve a free-text address to (lat, lon, display_name) via Photon."""

    # Guard: reject blank or URL-contaminated queries silently
    if not address or _URL_PATTERN.search(address):
        return None

    # URL-encode safely
    clean = address.strip()
    url = f"https://photon.komoot.io/api/?q={requests.utils.quote(clean)}&limit=1"
    headers = {
    'User-Agent': f"GautengRoutingEngine/1.0 ({os.getenv('EMAIL_HEADER', 'work@kgosi.co.za')})"
}

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if data["features"]:
            lon, lat = data["features"][0]["geometry"]["coordinates"]
            name = data["features"][0]["properties"].get("name", address)
            return lat, lon, name

    except Exception as exc:
        st.error(f"Geocoding error: {exc}")

    return None


def get_osrm_route(
    start: Tuple[float, float],
    end: Tuple[float, float],
) -> Optional[Tuple[List, float, float]]:
    """Calculate a driving route between two (lat, lon) pairs via OSRM."""
    url = (
        f"https://router.project-osrm.org/route/v1/driving/"
        f"{start[1]},{start[0]};{end[1]},{end[0]}"
        f"?overview=full&geometries=geojson"
    )

    try:
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        if data["routes"]:
            route = data["routes"][0]
            return (
                route["geometry"]["coordinates"],
                route["distance"],
                route["duration"],
            )

    except Exception as exc:
        st.error(f"Routing error: {exc}")

    return None