"""
utils/jobs.py
Adzuna SA API client — fetches live Gauteng internships/learnerships,
classifies them by sector, and geocodes their locations.
"""

import requests
import streamlit as st


app_id  = st.secrets["ADZUNA_APP_ID"]
app_key = st.secrets["ADZUNA_APP_KEY"]

ADZUNA_BASE = "https://api.adzuna.com/v1/api/jobs/za/search/1"

SECTOR_KEYWORDS = {
    "IT": [
        "developer", "programmer", "devops", "cloud", "engineer", "network",
        "software", "data", "cyber", "it support", "systems", "analyst",
        "frontend", "backend", "fullstack", "database", "qa", "testing",
        "machine learning", "python", "java",
    ],
    "Banking": [
        "bank", "finance", "financial", "accounting", "accountant", "auditor",
        "credit", "wealth", "investment", "trader", "actuary", "fintech",
        "compliance", "risk analyst", "teller", "loans",
    ],
    "Healthcare": [
        "nurse", "nursing", "medical", "hospital", "clinic", "health",
        "pharmacy", "pharmacist", "doctor", "radiographer", "physiotherapist",
        "occupational", "dietitian", "paramedic", "dental", "optometrist",
    ],
    "Security": [
        "security", "guard", "officer", "patrol", "risk", "investigator",
        "armed response", "cctv", "surveillance", "bodyguard", "vip protection",
        "access control", "fidelity", "g4s", "bidvest", "protection",
    ],
}

SECTOR_COLORS = {
    "IT":         "#00f3ff",
    "Banking":    "#FFD700",
    "Healthcare": "#50C878",
    "Security":   "#FF4D4D",
    "Other":      "#94a3b8",
}

# Lucide SVG icons — stroke="currentColor" inherits sector color automatically
SECTOR_ICONS = {
    # Monitor (laptop screen)
    "IT": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align:middle;margin-right:3px;">'
        '<rect x="2" y="3" width="20" height="14" rx="2"/>'
        '<line x1="8" y1="21" x2="16" y2="21"/>'
        '<line x1="12" y1="17" x2="12" y2="21"/>'
        '</svg>'
    ),
    # Landmark / bank columns
    "Banking": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align:middle;margin-right:3px;">'
        '<line x1="3" y1="22" x2="21" y2="22"/>'
        '<line x1="6" y1="18" x2="6" y2="11"/>'
        '<line x1="10" y1="18" x2="10" y2="11"/>'
        '<line x1="14" y1="18" x2="14" y2="11"/>'
        '<line x1="18" y1="18" x2="18" y2="11"/>'
        '<polygon points="12 2 20 7 4 7"/>'
        '</svg>'
    ),
    # Cross / plus in circle
    "Healthcare": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align:middle;margin-right:3px;">'
        '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>'
        '</svg>'
    ),
    # Shield
    "Security": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align:middle;margin-right:3px;">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
        '</svg>'
    ),
    # Briefcase
    "Other": (
        '<svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="vertical-align:middle;margin-right:3px;">'
        '<rect x="2" y="7" width="20" height="14" rx="2"/>'
        '<path d="M16 7V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2"/>'
        '<line x1="12" y1="12" x2="12" y2="16"/>'
        '<line x1="10" y1="14" x2="14" y2="14"/>'
        '</svg>'
    ),
}


def classify_job_sector(title: str, description: str = "") -> str:
    text = (title + " " + description).lower()
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(k in text for k in keywords):
            return sector
    return "Other"


def fetch_gauteng_jobs(
    keyword: str = "internship OR learnership",
    results_per_page: int = 20,
    app_id: str = app_id,
    app_key: str = app_key,
) -> list:
    params = {
        "app_id":           app_id,
        "app_key":          app_key,
        "results_per_page": results_per_page,
        "what":             keyword,
        "where":            "Gauteng",
        "content-type":     "application/json",
        "sort_by":          "date",
    }
    try:
        resp = requests.get(ADZUNA_BASE, params=params, timeout=8)
        resp.raise_for_status()
        raw_jobs = resp.json().get("results", [])
    except Exception:
        return []

    enriched = []
    for job in raw_jobs:
        title       = job.get("title", "Unknown Role")
        company     = job.get("company", {}).get("display_name", "Unknown Company")
        location    = job.get("location", {}).get("display_name", "Gauteng")
        description = job.get("description", "")
        redirect    = job.get("redirect_url", "#")
        created     = job.get("created", "")[:10]
        sector      = classify_job_sector(title, description)

        enriched.append({
            "title":       title,
            "company":     company,
            "location":    location,
            "description": description[:200] + "…" if len(description) > 200 else description,
            "url":         redirect,
            "created":     created,
            "sector":      sector,
            "color":       SECTOR_COLORS[sector],
            "icon":        SECTOR_ICONS[sector],
        })
    return enriched


def _clean_location(location: str) -> str:
    if not location:
        return "Gauteng"
    if location.startswith("http") or location.startswith("www"):
        return "Gauteng"
    parts = [p.strip() for p in location.split(",")]
    clean = [
        p for p in parts
        if "/" not in p
        and "http" not in p
        and ".co." not in p
        and ".com" not in p
        and ".za" not in p
        and not p.startswith("www")
    ]
    return ", ".join(clean) if clean else "Gauteng"


def geocode_jobs(jobs: list, get_coordinates_fn) -> list:
    vague = {"gauteng", "south africa", "gauteng, south africa", ""}

    for job in jobs:
        location = _clean_location(job["location"])
        if location.lower() in vague:
            continue

        company = job["company"] if "http" not in job["company"] else ""

        try:
            query = f"{company}, {location}, Gauteng".strip(", ")
            coords = get_coordinates_fn(query)
            if coords:
                job["lat"], job["lon"], _ = coords
                continue
            coords2 = get_coordinates_fn(f"{location}, Gauteng, South Africa")
            if coords2:
                job["lat"], job["lon"], _ = coords2
        except Exception:
            pass

    return jobs