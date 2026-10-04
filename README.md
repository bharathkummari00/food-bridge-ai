# Food Bridge AI – Food Redistribution System

> **A Complete AI-Powered Full-Stack Web Platform Connecting Surplus Food Donors with Verified NGOs, Shelters, and Communities in Need.**

---

## 🌟 Executive Summary & Project Purpose

**Food Bridge AI** is an intelligent web application designed to bridge the gap between food abundance and severe hunger. In India and across the world, thousands of kilograms of perfectly edible, hygienic surplus food from banquet halls, corporate events, restaurants, and bakeries are discarded daily, while orphanages, night shelters, and marginalized communities struggle for daily nutrition.

**Food Bridge AI** automates and streamlines this redistribution process through:
1. **Surplus Food Publishing**: Quick, intuitive donation creation with food grade assessment.
2. **Strictly Human-Readable Locality Navigation**: Eliminating raw latitude/longitude numbers in user interfaces and adopting **City → Area → Colony → Landmark** hierarchies.
3. **AI Multi-Criteria Redistribution Engine**: Calculating food freshness decay, intake capacity matching, transit feasibility, and urgency scoring.
4. **Live Interactive Food Map**: OpenStreetMap & Leaflet mapping with readable badges and instant meal request modals.
5. **Real-Time Role Dashboards & Visual Analytics**: Complete transparency for Donors, NGOs, and Central Administrators with Chart.js analytics.

---

## 📁 Complete Folder Structure

```
FoodBridgeAI/
│
├── frontend/
│   ├── components/
│   │   ├── navbar.js             # Shared dynamic navigation bar, notifications & demo role switcher
│   │   └── footer.js             # Shared footer with active hubs, mission & UN SDG badges
│   ├── pages/
│   │   ├── available-food.html   # Surplus food catalogue with multi-tier locality filters
│   │   ├── donate.html           # Food donation form with "Use My Current Location" & AI preview
│   │   ├── map-view.html         # Leaflet live food map displaying readable locality pins
│   │   ├── dashboard.html        # Role dashboards (Donor, NGO, Admin) + 4 Chart.js analytics
│   │   ├── ai-recommendations.html # AI redistribution center & interactive freshness simulator
│   │   └── auth.html             # Login, registration, & 1-click demo role switcher
│   ├── assets/
│   │   └── app.js                # Core frontend utilities, toast notifications, auth & modal handlers
│   └── styles/
│       └── main.css              # Custom styling, design tokens (emerald green, amber, coral)
│   └── index.html                # High-impact landing page (Hero, live stats, 5-step flow)
│
├── backend/
│   ├── routes/
│   │   ├── auth_routes.py        # Authentication, 1-click demo logins, profile sessions
│   │   ├── donation_routes.py    # Donations CRUD, locality filtering, map markers endpoint
│   │   ├── request_routes.py     # Meal requests lifecycle (Pending, Approved, Completed)
│   │   ├── location_routes.py    # Hierarchical cascading data & reverse geocoding
│   │   ├── notification_routes.py # Real-time alerts & unread counters
│   │   ├── ai_routes.py          # AI recommendation endpoints & freshness predictor
│   │   └── admin_routes.py       # Platform statistics, KPI analytics, & NGO verification
│   ├── services/
│   │   └── location_service.py   # Hierarchical location resolvers & internal coordinate mappers
│   └── app.py                    # Central Flask application, CORS setup, blueprint registration
│
├── database/
│   ├── schema.sql                # Relational SQLite schema definition
│   ├── db.py                     # Connection manager & automatic demo data seeder
│   └── foodbridge.db             # Pre-seeded SQLite database file
│
├── ai/
│   └── recommendation.py         # Multi-factor AI redistribution algorithm & standalone CLI tester
│
├── uploads/                      # Storage directory for uploaded food images
│
├── run.py                        # One-click application launcher
├── requirements.txt              # Python package dependencies
└── .env.example                  # Environment configuration template
```

---

## 🚀 Quick Start Guide (Run in Visual Studio Code)

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14
- Visual Studio Code

### 1. Open the Project Folder
Open Visual Studio Code, click **File → Open Folder...**, and select:
`c:\Users\kadud\OneDrive\Desktop\Food_bridge_final` (or `FoodBridgeAI`)

### 2. Install Required Dependencies
Open the built-in terminal in VS Code (`Ctrl + ~` or **Terminal → New Terminal**) and run:
```bash
python -m pip install -r requirements.txt
```

*(Core dependencies: `flask`, `flask-cors`, `werkzeug`, `requests`)*

### 3. Start the Web Server
In the VS Code terminal, simply execute:
```bash
python run.py
```

### 4. Open in Your Web Browser
Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## ☁️ Deploy to Render

The repository includes a Render Blueprint (`render.yaml`) that runs the Flask
application with Gunicorn, configures a generated `SECRET_KEY`, and checks
`/api/health`.

1. Push this repository to GitHub.
2. Sign in to [Render](https://render.com/) with GitHub and authorize access to
   this repository.
3. In the Render dashboard, select **New → Blueprint**, choose this repository,
   and apply the `render.yaml` configuration.
4. Open the deployed `onrender.com` URL after the first deploy finishes.

The service uses SQLite and the local uploads directory. On Render's free
instance, both are ephemeral and can be reset when the service restarts or
redeploys; use persistent storage before relying on it for real donations.

---

## 🔑 Pre-Seeded Demo Login Credentials

For quick evaluation during project reviews and viva demonstrations, the top navigation bar features a **1-Click Quick Switcher** ribbon that allows you to instantly switch between roles without typing! You can also sign in manually with these accounts:

| Role | Name & Entity | Email Address | Password |
|---|---|---|---|
| **Donor** | Rajesh Sharma (*Royal Grand Banquet Hall*) | `donor@foodbridge.ai` | `donor123` |
| **Donor (Bakery)** | Kavita Reddy (*Golden Crust Bakery*) | `kavita@foodbridge.ai` | `donor123` |
| **NGO / Shelter** | Sister Teresa Mary (*Hope Foundation Shelter*) | `ngo@foodbridge.ai` | `ngo123` |
| **NGO / Trust** | Venkatesh Rao (*Annapurna Seva Trust*) | `annapurna@foodbridge.ai` | `ngo123` |
| **Admin** | Admin Director (*Central Governance*) | `admin@foodbridge.ai` | `admin123` |

---

## 🗺️ How the Location and Map System Works

### Strict Zero Raw Coordinates Policy
In conventional computer science projects, developers mistakenly expose raw coordinates like `Latitude: 17.9824, Longitude: 79.5881` on screen. In a real-world humanitarian app, donors and delivery volunteers think in terms of **localities, colonies, and familiar landmarks**.

**Food Bridge AI** implements a **4-tier Locality Hierarchy**:
$$\text{City} \longrightarrow \text{Area} \longrightarrow \text{Colony / Locality} \longrightarrow \text{Street / Landmark}$$

*Example displayed to users:*
> 📍 **Warangal** | Area: **Hanamkonda** | Colony: **Subedari** | Address: **Opposite Kakatiya University Gate 2**

### Technical Location Implementation:
1. **Hierarchical Master Database (`locations_master`)**:
   Contains pre-mapped localities for key urban clusters (Warangal, Hanamkonda, Kazipet, Hyderabad, Madhapur, Gachibowli) mapped internally to geographical centroids.
2. **Cascading Dropdowns**:
   Selecting `City` (e.g. Warangal) dynamically populates `Area` (Hanamkonda, Kazipet, Warangal City). Selecting `Area` instantly updates `Colony` (Subedari, Nakkalagutta, Waddepally, etc.).
3. **"Use My Current Location" Internal Reverse-Geocoding**:
   When the user taps "Use My Current Location", the browser's HTML5 Geolocation API retrieves device coordinates. These coordinates are posted to `/api/locations/reverse-geocode`. The server computes the closest locality centroid using Haversine distance, and **automatically selects the matching City, Area, and Colony dropdowns** on the form—**completely shielding the user from raw latitude/longitude numbers**.
4. **Leaflet + OpenStreetMap Integration**:
   Map markers use coordinates strictly for placing pins on the graphical map. Every popup marker and tooltip displays human-readable information:
   - 🍱 **35 Meals Available**
   - 📍 **Hanamkonda – Subedari**
   - 🟢 **Excellent Quality**
   - ⏰ **Expires Today, 8:00 PM**
   - `[Request Food]` button

---

## 🧠 How the AI Recommendation Engine Works

The AI module in `ai/recommendation.py` implements a **Multi-Criteria Spatial Quality Optimization (MCSQO)** engine designed specifically for perishable food logistics.

### 1. Multi-Factor Formula
The algorithm computes an aggregate **Match Score (0% – 100%)** between any surplus food batch and candidate verified NGOs:

$$\text{Match Score} = (w_d \cdot S_{\text{dist}}) + (w_c \cdot S_{\text{cap}}) + (w_q \cdot S_{\text{qual}}) + (w_u \cdot S_{\text{urg}})$$

Where:
- $w_d = 0.35$ (Distance & Transit Proximity)
- $w_c = 0.25$ (NGO Intake Capacity Match)
- $w_q = 0.25$ (Food Freshness Decay Index)
- $w_u = 0.15$ (Expiry Urgency Window)

### 2. Breakdown of Components:
- **Food Freshness Decay Curve ($S_{\text{qual}}$)**:
  Takes the food category and preparation timestamp, applying an hourly decay rate based on thermal packaging (Hot Insulated vs. Ambient vs. Refrigerated).
- **Proximity Ranking ($S_{\text{dist}}$)**:
  Computes great-circle road distance in kilometers using the Haversine formula internally. Scores remain near 100% for $< 2\text{ km}$, gently decaying as distance increases.
- **Intake Capacity Match Ratio ($S_{\text{cap}}$)**:
  Compares batch quantity to the NGO's daily meal capacity:
  $$\text{Ratio} = \frac{\text{Donation Quantity}}{\text{NGO Daily Capacity}}$$
  Ratios between $0.5$ and $1.2$ achieve maximum points, preventing small batches from overwhelming large kitchens or large batches from expiring in small orphanages.
- **Urgency Override ($S_{\text{urg}}$)**:
  If a cooked meal expires in $< 2\text{ hours}$, the engine triggers an emergency rescue status, prioritizing the closest shelter capable of collection within 25 minutes.

### 3. Human-Readable Explanation Output
Rather than presenting an uninterpretable score, the AI provides plain-language reasons:
> **Recommended NGO: Hope Foundation Shelter** (96.5% Match)
> - 📍 Approximately 0.2 km away in Hanamkonda (Subedari)
> - 👥 Beneficiary intake (50 meals) matches donation volume (35 Meals)
> - 🟢 Food freshness is rated 'Excellent' with 6.0h safe consumption window
> - ⏱️ Pickup possible within ~16 minutes

You can run the engine standalone in the terminal anytime:
```bash
python ai/recommendation.py
```

---

## 🗄️ Database Architecture & Relational Schema

The application uses a persistent SQLite relational database (`database/foodbridge.db`) with full foreign key constraints and auto-seeding.

### Key Tables:
1. `users`:
   - User identity, role (`donor`, `ngo`, `admin`), hashed password (`werkzeug.security`), organization name, contact number, verified status, and readable locality (`city`, `area`, `colony`, `address`).
2. `donations`:
   - Food name, category, quantity, unit, preparation time, expiry time, quality rating (`Excellent`, `Good`, `Average`, `Poor`), description, image URL, readable pickup location, status (`Available`, `Reserved`, `Completed`), and AI match recommendation attributes.
3. `food_requests`:
   - Request lifecycle tracking, foreign keys to donation and NGO, requested quantity, volunteer pickup notes, status (`Pending`, `Approved`, `Picked Up`, `Completed`, `Rejected`), and scheduled pickup arrival time.
4. `locations_master`:
   - Curated hierarchical repository of cities, areas, colonies, landmarks, and internal geographic centroids.
5. `notifications`:
   - User notification inbox for real-time status updates, approval alerts, and safe pickup reminders.
6. `system_logs`:
   - Audit trail of platform activities.

---

## 🖥️ Detailed Explanation of Each Web Module

1. **Landing Page (`/` or `index.html`)**:
   - Modern, friendly hero section with responsive CTA buttons.
   - Live ticker cards pulling real stats from the database (Food Donated, Meals Served, Active Donors, Partner NGOs).
   - "How It Works" 5-step visual roadmap.
   - Real-time surplus food spotlight cards with 1-click modal requests.
2. **Available Food Page (`/available-food`)**:
   - Complete catalog of current surplus food with multi-criteria filtering by City, Area, Category, and Quality.
   - Distance indicators (e.g. `1.8 km away`) and expiry countdowns.
   - "Request Food" modal with quantity input and volunteer arrival notes.
3. **Live Food Map (`/map-view`)**:
   - Interactive Leaflet map with custom food badges and NGO pins.
   - Human-readable popup markers (no raw coordinates).
   - Filter by City and Area with automatic smooth camera panning.
4. **Food Donation Form (`/donate`)**:
   - 4-step structured form for Donors.
   - Quality selection with visual indicators (🟢 Excellent, 🟡 Good, 🟠 Average, 🔴 Poor).
   - Cascading City → Area → Colony dropdowns.
   - "Use My Current Location" button.
   - Preset realistic food photography picker.
5. **Dashboard & Analytics (`/dashboard`)**:
   - Role-based tabs (Donor View, NGO View, Admin View).
   - Incoming request approval pipeline for Donors.
   - Meal collection tracker for NGOs.
   - NGO license verification tool for Admins.
   - 4 Interactive Chart.js graphs: Weekly Donations Trend, Food Category Distribution, Locality Distribution, and Monthly Food Saved.
6. **AI Redistribution Center (`/ai-recommendations`)**:
   - Global network optimization visualizer showing matched donor-receiver pairs.
   - Interactive Viva simulator allowing examiners to test food decay rates by adjusting prep hours and storage conditions.
7. **Authentication Hub (`/auth`)**:
   - Secure login and registration with role separation.
   - 1-Click Instant Demo Login buttons.

---

## 🛡️ Demonstration Tips for B.Tech Viva & Review

1. **1-Click Role Demonstrations**: Use the top banner or Auth page to jump between Donor, NGO, and Admin views without repeatedly re-typing passwords.
2. **Interactive Map Highlight**: Point out to the examiner that **all markers and cards display locality names (City → Area → Colony)** and that raw coordinates are strictly hidden.
3. **AI Simulator Demonstration**: Open `/ai-recommendations`, move the Preparation Time slider, toggle between *Ambient* and *Hot Insulated*, and demonstrate how the AI automatically adjusts the freshness index and quality tier.
4. **Live Request Workflow**:
   - In Donor View, view or add a donation.
   - Switch to NGO View, browse `/available-food`, and click **Request Food**.
   - Switch back to Donor View on the `/dashboard` to approve the incoming request.
   - Show how the donation status updates from `Available` → `Reserved` → `Approved` with live notifications!

---

*Food Bridge AI – Built with passion for Sustainable Communities and Zero Hunger.*
