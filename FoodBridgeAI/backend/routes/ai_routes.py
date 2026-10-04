from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from database.db import get_db
from ai.recommendation import FoodRedistributionAI

ai_bp = Blueprint("ai_bp", __name__)
ai_engine = FoodRedistributionAI()


@ai_bp.route("/recommend/<int:donation_id>", methods=["GET"])
def recommend_for_single_donation(donation_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM donations WHERE id = ?", (donation_id,))
    d = cursor.fetchone()
    if not d:
        conn.close()
        return jsonify({"success": False, "error": "Donation not found"}), 404

    cursor.execute("SELECT * FROM users WHERE role = 'ngo' AND is_verified = 1")
    ngos = [dict(x) for x in cursor.fetchall()]
    conn.close()

    donation_dict = dict(d)
    recommendations = ai_engine.recommend_for_donation(donation_dict, ngos)

    return jsonify({
        "success": True,
        "donation": {
            "id": donation_dict["id"],
            "food_name": donation_dict["food_name"],
            "quantity": donation_dict["quantity"],
            "unit": donation_dict["unit"],
            "quality": donation_dict["quality"],
            "expiry_time": donation_dict["expiry_time"],
            "readable_location": f"{donation_dict['city']} → {donation_dict['area']} → {donation_dict['colony']}"
        },
        "recommendations": recommendations
    })


@ai_bp.route("/match-all", methods=["GET"])
def match_all_available():
    """
    Scans all available donations across the network and generates optimal
    matches with verified partner NGOs.
    """
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM donations WHERE status = 'Available' ORDER BY id ASC")
    donations = [dict(x) for x in cursor.fetchall()]

    cursor.execute("SELECT * FROM users WHERE role = 'ngo' AND is_verified = 1")
    ngos = [dict(x) for x in cursor.fetchall()]
    conn.close()

    matched_pairs = []
    total_meals_matched = 0

    for d in donations:
        recs = ai_engine.recommend_for_donation(d, ngos)
        if recs:
            top_rec = recs[0]
            matched_pairs.append({
                "donation_id": d["id"],
                "food_name": d["food_name"],
                "quantity": d["quantity"],
                "unit": d["unit"],
                "quality": d["quality"],
                "location": f"{d['city']} → {d['area']} → {d['colony']}",
                "recommended_ngo": top_rec["ngo_name"],
                "ngo_location": top_rec["ngo_location"],
                "match_score": top_rec["match_score"],
                "reasons": top_rec["reasons"],
                "estimated_pickup_minutes": top_rec["estimated_pickup_minutes"]
            })
            total_meals_matched += d["quantity"]

    avg_score = round(sum(p["match_score"] for p in matched_pairs) / len(matched_pairs), 1) if matched_pairs else 0

    return jsonify({
        "success": True,
        "total_matched": len(matched_pairs),
        "total_meals_matched": total_meals_matched,
        "average_match_score": avg_score,
        "matches": matched_pairs
    })


@ai_bp.route("/quality-predictor", methods=["POST"])
def predict_quality():
    """
    AI Food Quality Assessment based on preparation time, storage condition, and category.
    """
    data = request.get_json() or {}
    category = data.get("category", "Cooked Meals")
    prep_hours_ago = float(data.get("prep_hours_ago", 2.0))
    storage = data.get("storage", "ambient").lower()  # ambient, heated, refrigerated

    # Base decay rates per hour depending on storage
    decay_rates = {
        "ambient": 8.5,
        "heated": 3.0,
        "refrigerated": 1.5
    }
    rate = decay_rates.get(storage, 6.0)

    # Initial score
    freshness_index = max(10.0, min(100.0, 100.0 - (prep_hours_ago * rate)))

    if freshness_index >= 85:
        tier = "Excellent"
        color = "emerald"
        safe_hours = max(2, int(8 - prep_hours_ago))
        recommendation = "Safe for immediate and standard redistribution."
    elif freshness_index >= 70:
        tier = "Good"
        color = "amber"
        safe_hours = max(1, int(6 - prep_hours_ago))
        recommendation = "Suitable for rapid distribution within recommended time window."
    elif freshness_index >= 50:
        tier = "Average"
        color = "orange"
        safe_hours = max(1, int(3 - prep_hours_ago))
        recommendation = "Requires urgent consumption; prioritize nearest shelter."
    else:
        tier = "Poor"
        color = "red"
        safe_hours = 0
        recommendation = "Do not distribute. Recommend organic composting."

    return jsonify({
        "success": True,
        "freshness_index": round(freshness_index, 1),
        "quality_tier": tier,
        "badge_color": color,
        "safe_window_hours": safe_hours,
        "recommendation": recommendation
    })
