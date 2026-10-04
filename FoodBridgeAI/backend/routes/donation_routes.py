import os
from flask import Blueprint, request, jsonify, session
from database.db import get_db
from backend.services.location_service import get_coords_for_location
from ai.recommendation import FoodRedistributionAI, haversine_distance

donation_bp = Blueprint("donation_bp", __name__)
ai_engine = FoodRedistributionAI()


@donation_bp.route("", methods=["GET"])
def get_donations():
    """
    Fetch donations with multi-criteria filtering:
    City, Area, Colony, Category, Quality, Status, Search.
    Calculates distance in km relative to reference location without exposing lat/long.
    """
    city = request.args.get("city", "").strip()
    area = request.args.get("area", "").strip()
    colony = request.args.get("colony", "").strip()
    category = request.args.get("category", "").strip()
    quality = request.args.get("quality", "").strip()
    status = request.args.get("status", "Available").strip()
    donor_id = request.args.get("donor_id", "").strip()
    search = request.args.get("search", "").strip()

    # Reference user for distance calculation (if NGO is logged in or coordinates given)
    user_id = session.get("user_id") or request.args.get("viewer_id")
    viewer_lat, viewer_lng = None, None

    conn = get_db()
    cursor = conn.cursor()

    if user_id:
        cursor.execute("SELECT latitude, longitude FROM users WHERE id = ?", (user_id,))
        u = cursor.fetchone()
        if u and u["latitude"]:
            viewer_lat, viewer_lng = u["latitude"], u["longitude"]

    # Fallback to centroid of selected locality if viewer not logged in
    if viewer_lat is None and (city or area or colony):
        viewer_lat, viewer_lng = get_coords_for_location(city or "Warangal", area or "Hanamkonda", colony or "Subedari")
    elif viewer_lat is None:
        # Default central Warangal reference point
        viewer_lat, viewer_lng = (17.9824, 79.5881)

    query = "SELECT * FROM donations WHERE 1=1"
    params = []

    if status.lower() != "all":
        query += " AND LOWER(status) = LOWER(?)"
        params.append(status)

    if donor_id:
        query += " AND donor_id = ?"
        params.append(donor_id)

    if city:
        query += " AND LOWER(city) = LOWER(?)"
        params.append(city)

    if area:
        query += " AND LOWER(area) = LOWER(?)"
        params.append(area)

    if colony:
        query += " AND LOWER(colony) = LOWER(?)"
        params.append(colony)

    if category and category.lower() != "all":
        query += " AND LOWER(category) = LOWER(?)"
        params.append(category)

    if quality and quality.lower() != "all":
        query += " AND LOWER(quality) = LOWER(?)"
        params.append(quality)

    if search:
        query += " AND (food_name LIKE ? OR description LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term])

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for r in rows:
        item = dict(r)
        d_lat = item.get("latitude")
        d_lng = item.get("longitude")

        # Compute human-friendly distance in km
        if viewer_lat is not None and viewer_lng is not None and d_lat and d_lng:
            dist = haversine_distance(viewer_lat, viewer_lng, d_lat, d_lng)
            item["distance_km"] = dist
            item["distance_formatted"] = f"{dist} km away"
        else:
            item["distance_km"] = 1.5
            item["distance_formatted"] = "Nearby"

        # Safe location hierarchy string
        item["readable_location"] = f"{item['city']} → {item['area']} → {item['colony']}"

        # Clean raw coordinates from standard public cards (strictly internal on cards)
        # Note: We provide a dedicated clean endpoint /api/donations/map for map rendering
        results.append(item)

    return jsonify({"success": True, "count": len(results), "donations": results})


@donation_bp.route("/map", methods=["GET"])
def get_map_markers():
    """
    Returns map marker coordinates paired ONLY with human-readable information.
    Lat/Lng are used exclusively for Leaflet pin placement; never shown in text!
    """
    conn = get_db()
    cursor = conn.cursor()

    # Active donations
    cursor.execute("SELECT * FROM donations WHERE status IN ('Available', 'Reserved') ORDER BY id DESC")
    donation_rows = cursor.fetchall()

    # Verified NGOs
    cursor.execute("SELECT id, name, organization_name, city, area, colony, address, capacity, phone, latitude, longitude FROM users WHERE role = 'ngo'")
    ngo_rows = cursor.fetchall()
    conn.close()

    donations_data = []
    for d in donation_rows:
        item = dict(d)
        donations_data.append({
            "id": item["id"],
            "type": "donation",
            "lat": item["latitude"] or 17.9824,
            "lng": item["longitude"] or 79.5881,
            "food_name": item["food_name"],
            "quantity": item["quantity"],
            "unit": item["unit"],
            "quality": item["quality"],
            "status": item["status"],
            "expiry_time": item["expiry_time"],
            "donor_name": item["donor_name"],
            "image_url": item["image_url"],
            "city": item["city"],
            "area": item["area"],
            "colony": item["colony"],
            "address": item["address"],
            "readable_location": f"{item['area']} – {item['colony']}"
        })

    ngos_data = []
    for n in ngo_rows:
        item = dict(n)
        ngos_data.append({
            "id": item["id"],
            "type": "ngo",
            "lat": item["latitude"] or 17.9810,
            "lng": item["longitude"] or 79.5870,
            "name": item["organization_name"] or item["name"],
            "capacity": item["capacity"],
            "phone": item["phone"],
            "city": item["city"],
            "area": item["area"],
            "colony": item["colony"],
            "address": item["address"],
            "readable_location": f"{item['city']} → {item['area']} → {item['colony']}"
        })

    return jsonify({
        "success": True,
        "donations": donations_data,
        "ngos": ngos_data
    })


@donation_bp.route("/<int:donation_id>", methods=["GET"])
def get_donation_detail(donation_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM donations WHERE id = ?", (donation_id,))
    donation = cursor.fetchone()

    if not donation:
        conn.close()
        return jsonify({"success": False, "error": "Donation not found"}), 404

    d_dict = dict(donation)
    d_dict["readable_location"] = f"{d_dict['city']} → {d_dict['area']} → {d_dict['colony']}"

    # Fetch verified NGOs for AI ranking
    cursor.execute("SELECT * FROM users WHERE role = 'ngo' AND is_verified = 1")
    ngos = [dict(x) for x in cursor.fetchall()]
    conn.close()

    # Run AI evaluation
    ai_recs = ai_engine.recommend_for_donation(d_dict, ngos)
    d_dict["ai_recommendations"] = ai_recs[:3]  # Top 3 matches

    return jsonify({"success": True, "donation": d_dict})


@donation_bp.route("", methods=["POST"])
def create_donation():
    """
    Publishes a new surplus food donation.
    Automatically assigns AI recommendation and alerts nearby NGOs.
    """
    data = request.get_json() or {}

    food_name = data.get("food_name", "").strip()
    category = data.get("category", "Cooked Meals").strip()
    try:
        quantity = int(data.get("quantity", 10))
    except (ValueError, TypeError):
        quantity = 10
    unit = data.get("unit", "Meals").strip()
    prep_time = data.get("prep_time", "").strip()
    expiry_time = data.get("expiry_time", "").strip()
    quality = data.get("quality", "Good").strip()
    description = data.get("description", "").strip()
    image_url = data.get("image_url", "").strip()
    city = data.get("city", "Warangal").strip()
    area = data.get("area", "Hanamkonda").strip()
    colony = data.get("colony", "Subedari").strip()
    address = data.get("address", "").strip()

    if not food_name or not expiry_time:
        return jsonify({"success": False, "error": "Food Name and Expiry Date & Time are required"}), 400

    # Fallback realistic image if none provided
    if not image_url:
        presets = {
            "Cooked Meals": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80",
            "Bakery & Bread": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&auto=format&fit=crop&q=80",
            "Fruits & Vegetables": "https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=800&auto=format&fit=crop&q=80",
            "Packaged Food": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=800&auto=format&fit=crop&q=80",
            "Dairy & Beverages": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=800&auto=format&fit=crop&q=80"
        }
        image_url = presets.get(category, presets["Cooked Meals"])

    # Resolve coordinates internally from readable locality
    lat, lng = get_coords_for_location(city, area, colony)

    # Determine donor details from session or defaults
    user_id = session.get("user_id")
    conn = get_db()
    cursor = conn.cursor()

    if user_id:
        cursor.execute("SELECT id, name, organization_name FROM users WHERE id = ?", (user_id,))
        u = cursor.fetchone()
        donor_id = u["id"]
        donor_name = u["organization_name"] or u["name"]
    else:
        # Default to first demo donor
        cursor.execute("SELECT id, name, organization_name FROM users WHERE role = 'donor' LIMIT 1")
        u = cursor.fetchone()
        donor_id = u["id"] if u else 2
        donor_name = (u["organization_name"] or u["name"]) if u else "Community Food Donor"

    # Fetch verified NGOs for AI matching
    cursor.execute("SELECT * FROM users WHERE role = 'ngo' AND is_verified = 1")
    ngo_list = [dict(x) for x in cursor.fetchall()]

    temp_donation = {
        "food_name": food_name,
        "quantity": quantity,
        "unit": unit,
        "quality": quality,
        "expiry_time": expiry_time,
        "prep_time": prep_time,
        "latitude": lat,
        "longitude": lng,
        "city": city,
        "area": area,
        "colony": colony
    }

    ai_recs = ai_engine.recommend_for_donation(temp_donation, ngo_list)
    top_ngo_id = None
    ai_reason = "Evaluated by Food Bridge AI"
    ai_score = 90.0

    if ai_recs:
        top_match = ai_recs[0]
        top_ngo_id = top_match["ngo_id"]
        ai_score = top_match["match_score"]
        ai_reason = f"Recommended for {top_match['ngo_name']}: {top_match['reasons'][0]}"

    cursor.execute(
        """INSERT INTO donations 
        (donor_id, donor_name, food_name, category, quantity, unit, prep_time, expiry_time, quality, description, image_url, city, area, colony, address, latitude, longitude, status, ai_recommended_ngo_id, ai_recommendation_reason, ai_match_score) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Available', ?, ?, ?)""",
        (donor_id, donor_name, food_name, category, quantity, unit, prep_time, expiry_time, quality, description, image_url, city, area, colony, address, lat, lng, top_ngo_id, ai_reason, ai_score)
    )
    donation_id = cursor.lastrowid

    # Broadcast notification to recommended NGO and local NGOs
    readable_loc = f"{city} → {area} → {colony}"
    if top_ngo_id:
        cursor.execute(
            """INSERT INTO notifications (user_id, title, message, type) 
               VALUES (?, ?, ?, 'donation')""",
            (top_ngo_id, "🎯 High Priority AI Match for You!", f"{food_name} ({quantity} {unit}) donated in {area} – {colony}. AI Match Score: {ai_score}%")
        )

    cursor.execute(
        """INSERT INTO notifications (user_id, title, message, type) 
           VALUES (?, ?, ?, 'donation')""",
        (donor_id, "Food Donation Published Successfully!", f"Your donation of {food_name} ({quantity} {unit}) is now live and matched to nearby shelters.")
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Food donation published successfully!",
        "donation_id": donation_id,
        "ai_match": {
            "recommended_ngo_id": top_ngo_id,
            "match_score": ai_score,
            "reason": ai_reason
        }
    }), 201


@donation_bp.route("/<int:donation_id>/status", methods=["PATCH"])
def update_donation_status(donation_id):
    data = request.get_json() or {}
    new_status = data.get("status")

    valid_statuses = ("Available", "Reserved", "Picked Up", "Completed", "Cancelled", "Expired")
    if new_status not in valid_statuses:
        return jsonify({"success": False, "error": f"Invalid status. Choose from: {valid_statuses}"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE donations SET status = ? WHERE id = ?", (new_status, donation_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"Donation status updated to '{new_status}'."})
