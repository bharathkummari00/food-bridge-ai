from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session
from database.db import get_db

request_bp = Blueprint("request_bp", __name__)


@request_bp.route("", methods=["GET"])
def get_requests():
    ngo_id = request.args.get("ngo_id")
    donor_id = request.args.get("donor_id")
    donation_id = request.args.get("donation_id")
    status = request.args.get("status")

    user_id = session.get("user_id")
    user_role = session.get("role")

    conn = get_db()
    cursor = conn.cursor()

    query = """
        SELECT r.*, 
               d.food_name, d.category, d.quantity AS total_quantity, d.unit, 
               d.quality, d.city, d.area, d.colony, d.address AS pickup_address,
               d.donor_id, d.donor_name, d.expiry_time, d.image_url,
               u.phone AS ngo_phone, u.organization_name AS ngo_org
        FROM food_requests r
        JOIN donations d ON r.donation_id = d.id
        JOIN users u ON r.ngo_id = u.id
        WHERE 1=1
    """
    params = []

    if ngo_id:
        query += " AND r.ngo_id = ?"
        params.append(ngo_id)
    elif user_role == "ngo" and user_id:
        query += " AND r.ngo_id = ?"
        params.append(user_id)

    if donor_id:
        query += " AND d.donor_id = ?"
        params.append(donor_id)
    elif user_role == "donor" and user_id:
        query += " AND d.donor_id = ?"
        params.append(user_id)

    if donation_id:
        query += " AND r.donation_id = ?"
        params.append(donation_id)

    if status and status.lower() != "all":
        query += " AND LOWER(r.status) = LOWER(?)"
        params.append(status)

    query += " ORDER BY r.id DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        item = dict(row)
        item["readable_pickup_location"] = f"{item['city']} → {item['area']} → {item['colony']} ({item['pickup_address']})"
        results.append(item)

    return jsonify({"success": True, "count": len(results), "requests": results})


@request_bp.route("", methods=["POST"])
def create_request():
    data = request.get_json() or {}
    donation_id = data.get("donation_id")
    quantity_req = data.get("quantity_requested")
    notes = data.get("notes", "Our volunteers will pick up promptly.")

    if not donation_id:
        return jsonify({"success": False, "error": "donation_id is required"}), 400

    conn = get_db()
    cursor = conn.cursor()

    # Verify donation
    cursor.execute("SELECT * FROM donations WHERE id = ?", (donation_id,))
    donation = cursor.fetchone()
    if not donation:
        conn.close()
        return jsonify({"success": False, "error": "Donation not found"}), 404

    if donation["status"] not in ("Available", "Reserved"):
        conn.close()
        return jsonify({"success": False, "error": f"Food is no longer available (Status: {donation['status']})"}), 400

    # Determine NGO details
    user_id = session.get("user_id")
    if user_id:
        cursor.execute("SELECT id, name, organization_name FROM users WHERE id = ?", (user_id,))
        u = cursor.fetchone()
        ngo_id = u["id"]
        ngo_name = u["organization_name"] or u["name"]
    else:
        # Default demo NGO (Hope Foundation)
        cursor.execute("SELECT id, name, organization_name FROM users WHERE role = 'ngo' LIMIT 1")
        u = cursor.fetchone()
        ngo_id = u["id"] if u else 5
        ngo_name = (u["organization_name"] or u["name"]) if u else "Hope Foundation Shelter"

    qty = int(quantity_req) if quantity_req else donation["quantity"]

    # Insert request
    cursor.execute(
        """INSERT INTO food_requests (donation_id, ngo_id, ngo_name, quantity_requested, notes, status)
           VALUES (?, ?, ?, ?, ?, 'Pending')""",
        (donation_id, ngo_id, ngo_name, qty, notes)
    )
    request_id = cursor.lastrowid

    # Update donation status to Reserved
    cursor.execute("UPDATE donations SET status = 'Reserved' WHERE id = ?", (donation_id,))

    # Notify donor
    cursor.execute(
        """INSERT INTO notifications (user_id, title, message, type)
           VALUES (?, ?, ?, 'request')""",
        (donation["donor_id"], "New Food Request Received!", f"{ngo_name} has requested {qty} {donation['unit']} of {donation['food_name']}.")
    )

    # Notify NGO
    cursor.execute(
        """INSERT INTO notifications (user_id, title, message, type)
           VALUES (?, ?, ?, 'request')""",
        (ngo_id, "Food Request Submitted", f"Your request for {donation['food_name']} is submitted and pending donor confirmation.")
    )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Food request submitted for {donation['food_name']}!",
        "request_id": request_id
    }), 201


@request_bp.route("/<int:req_id>/status", methods=["PATCH"])
def update_request_status(req_id):
    data = request.get_json() or {}
    new_status = data.get("status")  # 'Approved', 'Picked Up', 'Completed', 'Rejected'
    pickup_time = data.get("pickup_time")

    valid_statuses = ("Pending", "Approved", "Picked Up", "Completed", "Rejected")
    if new_status not in valid_statuses:
        return jsonify({"success": False, "error": f"Invalid status. Choose from: {valid_statuses}"}), 400

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT r.*, d.food_name, d.donor_id, d.quantity, d.unit, d.city, d.area, d.colony, d.address
        FROM food_requests r
        JOIN donations d ON r.donation_id = d.id
        WHERE r.id = ?
    """, (req_id,))
    req_item = cursor.fetchone()

    if not req_item:
        conn.close()
        return jsonify({"success": False, "error": "Request not found"}), 404

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    if not pickup_time and new_status == "Approved":
        pickup_time = (datetime.now() + timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M")

    cursor.execute(
        "UPDATE food_requests SET status = ?, pickup_time = COALESCE(?, pickup_time), updated_at = ? WHERE id = ?",
        (new_status, pickup_time, now_str, req_id)
    )

    # Update donation status accordingly
    if new_status == "Completed":
        cursor.execute("UPDATE donations SET status = 'Completed' WHERE id = ?", (req_item["donation_id"],))
        # Celebration notification to both
        cursor.execute(
            """INSERT INTO notifications (user_id, title, message, type)
               VALUES (?, 'Donation Successfully Completed! 🎉', ?, 'system')""",
            (req_item["donor_id"], f"Your donation of {req_item['food_name']} was successfully distributed to people in need. Thank you for making a difference!")
        )
        cursor.execute(
            """INSERT INTO notifications (user_id, title, message, type)
               VALUES (?, 'Food Received & Distributed! 🌟', ?, 'system')""",
            (req_item["ngo_id"], f"Successfully distributed {req_item['quantity_requested']} meals of {req_item['food_name']}.")
        )
    elif new_status == "Rejected":
        # Release donation back to available
        cursor.execute("UPDATE donations SET status = 'Available' WHERE id = ?", (req_item["donation_id"],))
        cursor.execute(
            """INSERT INTO notifications (user_id, title, message, type)
               VALUES (?, 'Request Update', ?, 'alert')""",
            (req_item["ngo_id"], f"Your request for {req_item['food_name']} could not be accommodated at this time.")
        )
    elif new_status == "Approved":
        readable_loc = f"{req_item['city']} → {req_item['area']} → {req_item['colony']} ({req_item['address']})"
        cursor.execute(
            """INSERT INTO notifications (user_id, title, message, type)
               VALUES (?, 'Request Approved! 🚀', ?, 'request')""",
            (req_item["ngo_id"], f"Donor confirmed! Pickup location: {readable_loc}. Estimated pickup time: {pickup_time}")
        )

    conn.commit()
    conn.close()

    return jsonify({
        "success": True,
        "message": f"Request status updated to '{new_status}'."
    })
