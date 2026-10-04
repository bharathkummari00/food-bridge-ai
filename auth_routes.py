from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash, generate_password_hash
from database.db import get_db
from backend.services.location_service import get_coords_for_location

auth_bp = Blueprint("auth_bp", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(email) = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"success": False, "error": "Invalid email or password"}), 401

    user_dict = dict(user)
    user_dict.pop("password_hash", None)
    # Never expose raw coordinates in auth payload
    user_dict.pop("latitude", None)
    user_dict.pop("longitude", None)

    session["user_id"] = user_dict["id"]
    session["role"] = user_dict["role"]

    return jsonify({
        "success": True,
        "message": f"Welcome back, {user_dict['name']}!",
        "user": user_dict
    })


@auth_bp.route("/demo-login", methods=["POST"])
def demo_login():
    """
    Allows 1-click login as Demo Donor, Demo NGO, or Demo Admin
    Essential for rapid B.Tech viva demo and grading without typing!
    """
    data = request.get_json() or {}
    target_role = data.get("role", "donor").lower()

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE role = ? ORDER BY id ASC LIMIT 1", (target_role,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"success": False, "error": f"No demo user found for role: {target_role}"}), 404

    user_dict = dict(user)
    user_dict.pop("password_hash", None)
    user_dict.pop("latitude", None)
    user_dict.pop("longitude", None)

    session["user_id"] = user_dict["id"]
    session["role"] = user_dict["role"]

    return jsonify({
        "success": True,
        "message": f"Logged in as Demo {target_role.upper()}: {user_dict['name']}",
        "user": user_dict
    })


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    phone = data.get("phone", "").strip()
    role = data.get("role", "donor").lower()
    organization = data.get("organization_name", "").strip() or name
    city = data.get("city", "Warangal").strip()
    area = data.get("area", "Hanamkonda").strip()
    colony = data.get("colony", "Subedari").strip()
    address = data.get("address", "").strip()
    capacity = int(data.get("capacity", 50) if role == "ngo" else 0)

    if not name or not email or not password:
        return jsonify({"success": False, "error": "Name, email, and password are required"}), 400

    if role not in ("donor", "ngo", "admin"):
        role = "donor"

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM users WHERE LOWER(email) = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({"success": False, "error": "An account with this email already exists"}), 409

    # Internal coordinates for distance ranking (never shown to user)
    lat, lng = get_coords_for_location(city, area, colony)
    hashed = generate_password_hash(password)

    cursor.execute(
        """INSERT INTO users 
        (name, email, password_hash, phone, role, organization_name, city, area, colony, address, latitude, longitude, capacity, is_verified) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""",
        (name, email, hashed, phone, role, organization, city, area, colony, address, lat, lng, capacity)
    )
    user_id = cursor.lastrowid

    # Create welcome notification
    cursor.execute(
        "INSERT INTO notifications (user_id, title, message, type) VALUES (?, ?, ?, ?)",
        (user_id, "Welcome to Food Bridge AI!", f"Account created successfully as {role.upper()}. Together, let's stop hunger and food waste.", "system")
    )

    conn.commit()
    conn.close()

    session["user_id"] = user_id
    session["role"] = role

    return jsonify({
        "success": True,
        "message": "Registration successful! Welcome to Food Bridge AI.",
        "user": {
            "id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "organization_name": organization,
            "city": city,
            "area": area,
            "colony": colony,
            "address": address
        }
    }), 201


@auth_bp.route("/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"authenticated": False}), 200

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, phone, role, organization_name, city, area, colony, address, capacity, is_verified FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        session.clear()
        return jsonify({"authenticated": False}), 200

    return jsonify({
        "authenticated": True,
        "user": dict(user)
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "message": "Successfully logged out."})
