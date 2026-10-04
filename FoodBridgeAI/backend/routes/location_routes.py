from flask import Blueprint, request, jsonify
from backend.services.location_service import (
    get_location_hierarchy,
    reverse_geocode_to_hierarchy
)
from database.db import get_db

location_bp = Blueprint("location_bp", __name__)


@location_bp.route("/hierarchy", methods=["GET"])
def hierarchy():
    """
    Returns nested location hierarchy:
    City -> Area -> [Colonies]
    Powers the cascading dropdowns seamlessly.
    """
    data = get_location_hierarchy()
    return jsonify({"success": True, "hierarchy": data})


@location_bp.route("/reverse-geocode", methods=["POST"])
def reverse_geocode():
    """
    Called when user clicks 'Use My Current Location'.
    Internally uses HTML5 browser GPS coordinates and matches them
    to human-readable City -> Area -> Colony.
    Never exposes coordinates to the user interface.
    """
    data = request.get_json() or {}
    try:
        lat = float(data.get("latitude"))
        lng = float(data.get("longitude"))
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "Valid internal coordinates required for geocoding lookup"
        }), 400

    result = reverse_geocode_to_hierarchy(lat, lng)
    return jsonify({
        "success": True,
        "location": result
    })


@location_bp.route("/cities", methods=["GET"])
def get_cities():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT city FROM locations_master ORDER BY city")
    cities = [r["city"] for r in cursor.fetchall()]
    conn.close()
    return jsonify({"success": True, "cities": cities})
