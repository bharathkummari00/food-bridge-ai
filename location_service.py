"""
Location Service for Food Bridge AI
Handles hierarchical location mappings (City -> Area -> Colony)
and internal reverse geocoding to keep coordinates completely hidden from the UI.
"""

from typing import Dict, List, Any, Optional
from database.db import get_db
from ai.recommendation import haversine_distance


def get_location_hierarchy() -> Dict[str, Dict[str, List[str]]]:
    """
    Returns nested dictionary:
    {
      "CityName": {
        "AreaName": ["Colony1", "Colony2", ...]
      }
    }
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT city, area, colony FROM locations_master ORDER BY city, area, colony")
    rows = cursor.fetchall()
    conn.close()

    hierarchy = {}
    for r in rows:
        city = r["city"]
        area = r["area"]
        colony = r["colony"]

        if city not in hierarchy:
            hierarchy[city] = {}
        if area not in hierarchy[city]:
            hierarchy[city][area] = []
        if colony not in hierarchy[city][area]:
            hierarchy[city][area].append(colony)

    return hierarchy


def get_coords_for_location(city: str, area: str, colony: str) -> tuple:
    """
    Returns (latitude, longitude) for a given hierarchy.
    Defaults to Warangal center if not found.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT latitude, longitude FROM locations_master 
           WHERE LOWER(city) = LOWER(?) AND LOWER(area) = LOWER(?) AND LOWER(colony) = LOWER(?) 
           LIMIT 1""",
        (city.strip(), area.strip(), colony.strip())
    )
    row = cursor.fetchone()
    if not row:
        cursor.execute(
            """SELECT latitude, longitude FROM locations_master 
               WHERE LOWER(city) = LOWER(?) AND LOWER(area) = LOWER(?) 
               LIMIT 1""",
            (city.strip(), area.strip())
        )
        row = cursor.fetchone()
    conn.close()

    if row:
        return (row["latitude"], row["longitude"])
    return (17.9824, 79.5881)  # Default fallback centroid


def reverse_geocode_to_hierarchy(lat: float, lng: float) -> Dict[str, Any]:
    """
    Finds closest known City, Area, Colony without exposing coordinates to user.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT city, area, colony, landmark, latitude, longitude FROM locations_master")
    rows = cursor.fetchall()
    conn.close()

    best_match = None
    min_dist = float("inf")

    for r in rows:
        d = haversine_distance(lat, lng, r["latitude"], r["longitude"])
        if d < min_dist:
            min_dist = d
            best_match = r

    if best_match:
        return {
            "city": best_match["city"],
            "area": best_match["area"],
            "colony": best_match["colony"],
            "landmark": best_match["landmark"] or "",
            "display_name": f"{best_match['city']} -> {best_match['area']} -> {best_match['colony']}"
        }

    return {
        "city": "Warangal",
        "area": "Hanamkonda",
        "colony": "Subedari",
        "landmark": "Near Kakatiya University",
        "display_name": "Warangal -> Hanamkonda -> Subedari"
    }
