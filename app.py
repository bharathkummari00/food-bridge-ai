import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Ensure root directory of FoodBridgeAI is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from database.db import init_db
from backend.routes.auth_routes import auth_bp
from backend.routes.donation_routes import donation_bp
from backend.routes.request_routes import request_bp
from backend.routes.location_routes import location_bp
from backend.routes.notification_routes import notification_bp
from backend.routes.ai_routes import ai_bp
from backend.routes.admin_routes import admin_bp

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)


def create_app():
    app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")
    app.secret_key = os.environ.get("SECRET_KEY", "food-bridge-ai-super-secret-key-2026")

    # Enable CORS for local development
    CORS(app, supports_credentials=True)

    # Initialize Database with pre-seeded demo records
    with app.app_context():
        init_db()

    # Register API Blueprints
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(donation_bp, url_prefix="/api/donations")
    app.register_blueprint(request_bp, url_prefix="/api/requests")
    app.register_blueprint(location_bp, url_prefix="/api/locations")
    app.register_blueprint(notification_bp, url_prefix="/api/notifications")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    # API Health Check
    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({
            "status": "healthy",
            "app": "Food Bridge AI",
            "version": "2.0.0",
            "ai_engine": "Multi-Criteria Spatial Quality Redistribution",
            "mode": "Demonstration & Production Ready"
        })

    # Image Upload Route
    @app.route("/api/upload", methods=["POST"])
    def upload_file():
        if "file" not in request.files:
            return jsonify({"success": False, "error": "No file uploaded"}), 400
        file = request.files["file"]
        if file.filename == "":
            return jsonify({"success": False, "error": "Empty filename"}), 400

        filename = secure_filename(file.filename)
        # Prefix timestamp to avoid collisions
        unique_name = f"{int(os.times().system * 1000)}_{filename}"
        filepath = os.path.join(UPLOADS_DIR, unique_name)
        file.save(filepath)

        return jsonify({
            "success": True,
            "url": f"/uploads/{unique_name}",
            "filename": unique_name
        })

    # Serve Uploaded Media
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(UPLOADS_DIR, filename)

    # Serve Frontend HTML Pages
    @app.route("/")
    def index():
        return send_from_directory(FRONTEND_DIR, "index.html")

    @app.route("/available-food")
    def available_food_page():
        return send_from_directory(os.path.join(FRONTEND_DIR, "pages"), "available-food.html")

    @app.route("/donate")
    def donate_page():
        return send_from_directory(os.path.join(FRONTEND_DIR, "pages"), "donate.html")

    @app.route("/map-view")
    def map_page():
        return send_from_directory(os.path.join(FRONTEND_DIR, "pages"), "map-view.html")

    @app.route("/dashboard")
    def dashboard_page():
        return send_from_directory(os.path.join(FRONTEND_DIR, "pages"), "dashboard.html")

    @app.route("/ai-recommendations")
    def ai_page():
        return send_from_directory(os.path.join(FRONTEND_DIR, "pages"), "ai-recommendations.html")

    @app.route("/auth")
    def auth_page():
        return send_from_directory(os.path.join(FRONTEND_DIR, "pages"), "auth.html")

    # Static Assets Handler (CSS, JS, Images, Components)
    @app.route("/<path:path>")
    def static_proxy(path):
        target = os.path.join(FRONTEND_DIR, path)
        if os.path.exists(target):
            return send_from_directory(FRONTEND_DIR, path)
        return send_from_directory(FRONTEND_DIR, "index.html")

    return app


app = create_app()

if __name__ == "__main__":
    print("=" * 65)
    print("  FOOD BRIDGE AI - WEB SERVER STARTING")
    print("  Access Platform: http://127.0.0.1:5000")
    print("=" * 65)
    app.run(host="127.0.0.1", port=5000, debug=True)
