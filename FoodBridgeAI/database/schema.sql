-- Food Bridge AI Database Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    phone TEXT,
    role TEXT NOT NULL CHECK(role IN ('donor', 'ngo', 'admin')),
    organization_name TEXT,
    city TEXT DEFAULT 'Warangal',
    area TEXT DEFAULT 'Hanamkonda',
    colony TEXT DEFAULT 'Subedari',
    address TEXT,
    latitude REAL DEFAULT 17.9784,
    longitude REAL DEFAULT 79.5941,
    capacity INTEGER DEFAULT 50, -- For NGOs: typical meal intake capacity
    is_verified INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER NOT NULL,
    donor_name TEXT,
    food_name TEXT NOT NULL,
    category TEXT NOT NULL, -- Cooked Meals, Bakery & Bread, Fruits & Vegetables, Packaged Food, Dairy & Beverages
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL DEFAULT 'Meals',
    prep_time TEXT NOT NULL,
    expiry_time TEXT NOT NULL,
    quality TEXT NOT NULL CHECK(quality IN ('Excellent', 'Good', 'Average', 'Poor')),
    description TEXT,
    image_url TEXT,
    city TEXT NOT NULL,
    area TEXT NOT NULL,
    colony TEXT NOT NULL,
    address TEXT NOT NULL,
    latitude REAL,
    longitude REAL,
    status TEXT NOT NULL DEFAULT 'Available', -- Available, Reserved, Picked Up, Completed, Cancelled, Expired
    ai_recommended_ngo_id INTEGER,
    ai_recommendation_reason TEXT,
    ai_match_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(donor_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS food_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donation_id INTEGER NOT NULL,
    ngo_id INTEGER NOT NULL,
    ngo_name TEXT,
    quantity_requested INTEGER NOT NULL,
    notes TEXT,
    status TEXT NOT NULL DEFAULT 'Pending', -- Pending, Approved, Picked Up, Completed, Rejected
    pickup_time TEXT,
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(donation_id) REFERENCES donations(id),
    FOREIGN KEY(ngo_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'system', -- donation, request, alert, expiry, system
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS locations_master (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    area TEXT NOT NULL,
    colony TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    pincode TEXT,
    landmark TEXT
);

CREATE TABLE IF NOT EXISTS system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    description TEXT NOT NULL,
    user_id INTEGER,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
