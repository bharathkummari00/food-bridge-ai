import os
import sqlite3
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(__file__), "foodbridge.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")


def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    db_exists = os.path.exists(DB_PATH)
    conn = get_db()
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())
    conn.commit()

    # Check if demo users exist; if not, seed data
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_demo_data(conn)

    conn.close()


def seed_demo_data(conn):
    cursor = conn.cursor()
    now = datetime.now()

    # 1. Locations Master (Hierarchy: City -> Area -> Colony)
    # Warangal & Hyderabad centroids for realistic calculations
    locations = [
        # Warangal
        ("Warangal", "Hanamkonda", "Subedari", 17.9824, 79.5881, "506001", "Near Kakatiya University"),
        ("Warangal", "Hanamkonda", "Nakkalagutta", 17.9851, 79.5992, "506001", "Near Public Gardens"),
        ("Warangal", "Hanamkonda", "Waddepally", 17.9912, 79.5744, "506370", "Near Waddepally Lake"),
        ("Warangal", "Hanamkonda", "Kishanpura", 17.9890, 79.5920, "506001", "Near Thousand Pillar Temple"),
        ("Warangal", "Kazipet", "Station Road", 17.9734, 79.5218, "506003", "Opposite Railway Junction"),
        ("Warangal", "Kazipet", "Fathimanagar", 17.9691, 79.5290, "506003", "Near St. Ann Church"),
        ("Warangal", "Kazipet", "Bapuji Nagar", 17.9760, 79.5180, "506003", "Near Railway Quarters"),
        ("Warangal", "Warangal City", "Mandi Bazar", 17.9610, 79.6015, "506002", "Near Grain Market"),
        ("Warangal", "Warangal City", "Girmajipet", 17.9675, 79.6050, "506002", "Near Fort Road"),
        ("Warangal", "Warangal City", "Hunter Road", 17.9702, 79.5850, "506001", "Near Arts College Ground"),
        # Hyderabad
        ("Hyderabad", "Madhapur", "Hitech City", 17.4474, 78.3762, "500081", "Near Cyber Towers"),
        ("Hyderabad", "Madhapur", "Ayyappa Society", 17.4520, 78.3840, "500081", "Near 100 Feet Road"),
        ("Hyderabad", "Gachibowli", "Telecom Nagar", 17.4360, 78.3610, "500032", "Near Stadium"),
        ("Hyderabad", "Banjara Hills", "Road No 12", 17.4150, 78.4350, "500034", "Near Cancer Hospital"),
        ("Hyderabad", "Kukatpally", "KPHB Phase 1", 17.4930, 78.4010, "500072", "Near Metro Station")
    ]
    cursor.executemany(
        "INSERT INTO locations_master (city, area, colony, latitude, longitude, pincode, landmark) VALUES (?, ?, ?, ?, ?, ?, ?)",
        locations
    )

    # 2. Users (Admin, Donors, NGOs)
    # Passwords hashed with werkzeug
    admin_pw = generate_password_hash("admin123")
    donor_pw = generate_password_hash("donor123")
    ngo_pw = generate_password_hash("ngo123")

    users = [
        # Admin
        ("Admin Director", "admin@foodbridge.ai", admin_pw, "+91 98480 12345", "admin", "Food Bridge Central Command", "Warangal", "Hanamkonda", "Subedari", "Administrative Block, KU Campus", 17.9824, 79.5881, 0, 1),
        # Donors
        ("Rajesh Sharma", "donor@foodbridge.ai", donor_pw, "+91 98480 23456", "donor", "Royal Grand Banquet Hall", "Warangal", "Hanamkonda", "Subedari", "Opposite Kakatiya University Gate 2", 17.9824, 79.5881, 0, 1),
        ("Priya Verma", "hotel@foodbridge.ai", donor_pw, "+91 98480 34567", "donor", "Spice Garden Catering Hub", "Warangal", "Kazipet", "Station Road", "Shop 12, Opposite Railway Junction", 17.9734, 79.5218, 0, 1),
        ("Kavita Reddy", "kavita@foodbridge.ai", donor_pw, "+91 98480 45678", "donor", "Golden Crust Artisan Bakery", "Warangal", "Hanamkonda", "Nakkalagutta", "Main Road, Sector 2", 17.9851, 79.5992, 0, 1),
        # NGOs / Receivers
        ("Sister Teresa Mary", "ngo@foodbridge.ai", ngo_pw, "+91 98480 56789", "ngo", "Hope Foundation Shelter", "Warangal", "Hanamkonda", "Subedari", "Plot 14, Behind District Govt Hospital", 17.9810, 79.5870, 50, 1),
        ("Venkatesh Rao", "annapurna@foodbridge.ai", ngo_pw, "+91 98480 67890", "ngo", "Annapurna Seva Trust", "Warangal", "Hanamkonda", "Nakkalagutta", "Community Hall, Sector 3", 17.9860, 79.6010, 120, 1),
        ("Dr. Anjali Deshmukh", "orphanage@foodbridge.ai", ngo_pw, "+91 98480 78901", "ngo", "Little Angels Orphan Home", "Warangal", "Kazipet", "Fathimanagar", "St. Ann Road, Near Holy Cross", 17.9695, 79.5305, 40, 1),
        ("Mohammed Aslam", "citycare@foodbridge.ai", ngo_pw, "+91 98480 89012", "ngo", "City Care Night Shelter", "Warangal", "Warangal City", "Hunter Road", "Building 4, Near Arts College", 17.9710, 79.5865, 80, 1)
    ]

    cursor.executemany(
        """INSERT INTO users 
        (name, email, password_hash, phone, role, organization_name, city, area, colony, address, latitude, longitude, capacity, is_verified) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        users
    )

    # 3. Active and Completed Food Donations
    # Time helpers
    t_minus_2 = (now - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
    t_minus_3 = (now - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M")
    t_minus_1 = (now - timedelta(hours=1)).strftime("%Y-%m-%d %H:%M")
    t_plus_5 = (now + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M")
    t_plus_6 = (now + timedelta(hours=6)).strftime("%Y-%m-%d %H:%M")
    t_plus_18 = (now + timedelta(hours=18)).strftime("%Y-%m-%d %H:%M")
    t_plus_4 = (now + timedelta(hours=4)).strftime("%Y-%m-%d %H:%M")
    t_plus_48 = (now + timedelta(hours=48)).strftime("%Y-%m-%d %H:%M")
    t_plus_8 = (now + timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")

    # Image placeholders with food-themed high-res Unsplash links & local fallbacks
    donations = [
        (2, "Royal Grand Banquet Hall", "Steaming Vegetable Biryani & Cucumber Raita", "Cooked Meals", 35, "Meals", 
         t_minus_2, t_plus_6, "Excellent", 
         "Freshly prepared Hyderabadi vegetable biryani packed in hygienic food-grade containers with sealed lids. Perfect condition.",
         "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&auto=format&fit=crop&q=80",
         "Warangal", "Hanamkonda", "Subedari", "Royal Grand Banquet Hall, Opp KU Gate 2", 17.9824, 79.5881, "Available",
         5, "Recommended for Hope Foundation Shelter (0.2 km away, capacity 50 matches 35 meals, safe pickup window 5h)", 96.5),
        
        (3, "Spice Garden Catering Hub", "Paneer Butter Masala & 80 Wheat Phulkas", "Cooked Meals", 45, "Meals", 
         t_minus_3, t_plus_5, "Good", 
         "Rich paneer curry with whole wheat phulkas prepared for a corporate luncheon. Maintained in hot insulated catering containers.",
         "https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=800&auto=format&fit=crop&q=80",
         "Warangal", "Kazipet", "Station Road", "Shop 12, Opposite Railway Junction", 17.9734, 79.5218, "Available",
         7, "Recommended for Little Angels Orphan Home (0.9 km away, capacity 40 matches 45 meals)", 92.0),
        
        (4, "Golden Crust Artisan Bakery", "Assorted Fresh Milk Breads & Fruit Buns", "Bakery & Bread", 25, "kg", 
         t_minus_1, t_plus_18, "Excellent", 
         "Surplus day-fresh bakery items, sweet buns, and whole grain sandwich bread loaves. Individually wrapped.",
         "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&auto=format&fit=crop&q=80",
         "Warangal", "Hanamkonda", "Nakkalagutta", "Golden Crust Bakery, Main Road Sector 2", 17.9851, 79.5992, "Available",
         6, "Recommended for Annapurna Seva Trust (0.3 km away, high capacity)", 94.8),

        (2, "Royal Grand Banquet Hall", "Traditional South Indian Sambar Rice & Curd Rice", "Cooked Meals", 40, "Meals", 
         t_minus_2, t_plus_4, "Good", 
         "Hot and nutritious sambar rice paired with tempered curd rice from wedding feast.",
         "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=800&auto=format&fit=crop&q=80",
         "Warangal", "Hanamkonda", "Subedari", "Srinivasa Kalyana Mandapam, University Road", 17.9802, 79.5855, "Reserved",
         5, "Reserved by Hope Foundation Shelter", 95.0),

        (3, "Spice Garden Catering Hub", "Farm Fresh Crisp Apples & Cavendish Bananas", "Fruits & Vegetables", 30, "kg", 
         t_minus_1, t_plus_48, "Excellent", 
         "Crates of ripe, clean fruit from morning breakfast buffet supply. Ready for direct distribution.",
         "https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=800&auto=format&fit=crop&q=80",
         "Warangal", "Hanamkonda", "Waddepally", "Green Grocers Hub, Lake View Road", 17.9912, 79.5744, "Available",
         6, "Recommended for Annapurna Seva Trust", 91.2),

        (4, "Golden Crust Artisan Bakery", "Nutritious Hot Lentil Broth & Steamed Idlis", "Cooked Meals", 30, "Meals", 
         t_minus_2, t_plus_8, "Good", 
         "Soft steamed rice cakes with piping hot vegetable dal, kept heated.",
         "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800&auto=format&fit=crop&q=80",
         "Warangal", "Kazipet", "Fathimanagar", "Wellness Kitchen, Church Compound", 17.9691, 79.5290, "Available",
         7, "Recommended for Little Angels Orphan Home (0.2 km away)", 98.2),

        (2, "Royal Grand Banquet Hall", "Mixed Vegetable Fried Rice & Manchurian", "Cooked Meals", 60, "Meals", 
         (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M"), (now - timedelta(days=1, hours=-5)).strftime("%Y-%m-%d %H:%M"), "Good", 
         "Evening reception surplus cleanly packed.",
         "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=800&auto=format&fit=crop&q=80",
         "Warangal", "Hanamkonda", "Subedari", "Royal Grand Banquet Hall", 17.9824, 79.5881, "Completed",
         5, "Completed pickup by Hope Foundation", 97.0)
    ]

    cursor.executemany(
        """INSERT INTO donations 
        (donor_id, donor_name, food_name, category, quantity, unit, prep_time, expiry_time, quality, description, image_url, city, area, colony, address, latitude, longitude, status, ai_recommended_ngo_id, ai_recommendation_reason, ai_match_score) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        donations
    )

    # 4. Food Requests
    requests = [
        (4, 5, "Hope Foundation Shelter", 40, "Our volunteers are equipped with thermal bags and can collect within 30 minutes.", "Approved", (now + timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M")),
        (1, 5, "Hope Foundation Shelter", 35, "Can collect for evening dinner session for our 45 shelter residents.", "Pending", None),
        (7, 5, "Hope Foundation Shelter", 60, "Successfully served 60 homeless individuals at railway overbridge shelter.", "Completed", (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")),
        (2, 7, "Little Angels Orphan Home", 40, "Children dinner meal request. We have vehicle ready.", "Pending", None)
    ]
    cursor.executemany(
        """INSERT INTO food_requests 
        (donation_id, ngo_id, ngo_name, quantity_requested, notes, status, pickup_time) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        requests
    )

    # 5. Notifications
    notifications = [
        (5, "New Surplus Food Match Available!", "Steaming Vegetable Biryani (35 Meals) is available just 0.2 km away in Hanamkonda – Subedari.", "donation"),
        (5, "Request Approved!", "Your request for 40 meals of Sambar Rice & Curd Rice has been approved by Royal Grand Banquet Hall.", "request"),
        (2, "New Request Received", "Hope Foundation Shelter requested 35 meals of Vegetable Biryani.", "request"),
        (7, "Donation Nearby In Your Locality", "Assorted Fresh Milk Breads available at Golden Crust Bakery (0.3 km away).", "donation"),
        (1, "System Security Check", "All NGO licenses verified for Hanamkonda and Kazipet zones.", "system")
    ]
    cursor.executemany(
        "INSERT INTO notifications (user_id, title, message, type) VALUES (?, ?, ?, ?)",
        notifications
    )

    # 6. System Log
    cursor.execute(
        "INSERT INTO system_logs (event_type, description, user_id) VALUES (?, ?, ?)",
        ("SEED", "Initial demonstration database populated with users, donations, requests, and locations.", 1)
    )

    conn.commit()


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
