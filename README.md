# Gauteng Transit Engine

A hardware-accelerated 3D transit and cost calculator for Gauteng, South Africa.

## Features
- 3D vector map with real-time route calculation
- Fuel cost estimates per vehicle type
- Live Gauteng job listings (internships & learnerships) via Adzuna
- Job pins geocoded and overlaid on the map by sector

## Setup

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill in your keys
4. Run: `streamlit run app.py`

## Required API Keys
- Adzuna (jobs): https://developer.adzuna.com
- TomTom (traffic): https://developer.tomtom.com

## Screenshots

![Map View](assets/screenshot.png)
![Job Listings](assets/jobs.png)

