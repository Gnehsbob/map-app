import os
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
import requests 
from dotenv import load_dotenv 
import streamlit as st


load_dotenv()


# Save the database inside your persistent vault
DB_PATH = Path("/mnt/vault/map-app/traffic.db")

# Global API Key 
TOMTOM_API_KEY = st.secrets["TOMTOM_API_KEY"]

def init_db():
    """Initializes the SQLite database with the SRE traffic schema."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trips (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,                -- ISO timestamp of trip start
                day_of_week INTEGER,            -- 0=Monday ... 6=Sunday
                hour INTEGER,                   -- 0-23
                route_hash TEXT,                -- MD5 of route geometry
                origin_lat REAL,
                origin_lon REAL,
                dest_lat REAL,
                dest_lon REAL,
                distance_m REAL,
                osrm_duration_s REAL,           -- OSRM baseline estimation
                actual_duration_s REAL,         -- Filled after user reports arrival
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
        """)

def record_trip(origin, dest, distance_m, osrm_duration_s, route_geojson):
    """Logs the initial trip parameters when a route is generated."""
    start_time = datetime.now().isoformat()
    hour = datetime.now().hour
    dow = datetime.now().weekday()
    
    # Generate a unique hash from the first 10 coordinate points of the route
    coords = route_geojson["geometry"]["coordinates"]
    route_hash = hashlib.md5(str(coords[:10]).encode()).hexdigest()
    
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            """INSERT INTO trips
               (start_time, day_of_week, hour, route_hash, origin_lat, origin_lon,
                dest_lat, dest_lon, distance_m, osrm_duration_s, actual_duration_s)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)""",
            (start_time, dow, hour, route_hash,
             origin[0], origin[1], dest[0], dest[1],
             distance_m, osrm_duration_s)
        )
        return cursor.lastrowid

def update_actual_duration(trip_id, actual_duration_s):
    """Updates the database with the real-world travel time on arrival."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE trips SET actual_duration_s = ? WHERE id = ?",
            (actual_duration_s, trip_id)
        )

def get_congestion_factor(route_hash, hour, day_of_week):
    """Calculates historical congestion factor (Actual / OSRM) for a route and hour."""
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """SELECT actual_duration_s, osrm_duration_s
               FROM trips
               WHERE route_hash = ?
                 AND day_of_week = ?
                 AND hour BETWEEN ? AND ?
                 AND actual_duration_s IS NOT NULL""",
            (route_hash, day_of_week, hour - 1, hour + 1)
        ).fetchall()
    
    if not rows:
        return 1.0  # Default to baseline (no traffic delays)
    
    factors = [actual / osrm for actual, osrm in rows if osrm > 0]
    if not factors:
        return 1.0
    return sum(factors) / len(factors)

def mine_realtime_traffic(start_coords, end_coords, osrm_duration_s, distance_m, route_geojson):
    """
    Silently queries TomTom for real-time traffic, calculates the congestion factor,
    and logs it automatically into the SQLite database.
    """
    # TomTom expects: latitude,longitude
    start_str = f"{start_coords[0]},{start_coords[1]}"
    end_str = f"{end_coords[0]},{end_coords[1]}"
    
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{start_str}:{end_str}/json"
    params = {
        "key": TOMTOM_API_KEY,
        "traffic": "true",
        "travelMode": "car"
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            data = response.json()
            # TomTom returns travelTimeInSeconds (includes live traffic)
            tomtom_duration_s = data["routes"][0]["summary"]["travelTimeInSeconds"]
            
            # Write to SQLite immediately
            start_time = datetime.now().isoformat()
            hour = datetime.now().hour
            dow = datetime.now().weekday()
            
            # Hash the route geometry
            coords = route_geojson["geometry"]["coordinates"]
            route_hash = hashlib.md5(str(coords[:10]).encode()).hexdigest()
            
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    """INSERT INTO trips
                       (start_time, day_of_week, hour, route_hash, origin_lat, origin_lon,
                        dest_lat, dest_lon, distance_m, osrm_duration_s, actual_duration_s)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (start_time, dow, hour, route_hash,
                     start_coords[0], start_coords[1], end_coords[0], end_coords[1],
                     distance_m, osrm_duration_s, tomtom_duration_s)
                )
            return tomtom_duration_s
    except Exception as e:
        # Silently fail if API is down or key is exhausted 
        pass
    return None