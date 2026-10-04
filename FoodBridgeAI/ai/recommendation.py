"""
Food Bridge AI - Food Redistribution & Quality Recommendation Engine
=====================================================================
Analyzes surplus food donations using a multi-factor decision engine:
- Food Quality & Freshness Decay Curve
- Proximity & Haversine Distance (without exposing raw coordinates to UI)
- NGO Intake Capacity vs. Donation Volume
- Expiry Time Urgency Window
- Safe Transit Feasibility Score
"""

import math
from datetime import datetime
from typing import Dict, List, Any, Optional


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates great-circle distance between two points in kilometers.
    Used strictly internally for ranking without exposing raw coords to users.
    """
    if None in (lat1, lon1, lat2, lon2):
        return 5.0  # Default reasonable estimation if coords missing

    R = 6371.0  # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


class FoodRedistributionAI:
    def __init__(self):
        # Weights for multi-criteria optimization
        self.WEIGHT_DISTANCE = 0.35
        self.WEIGHT_CAPACITY = 0.25
        self.WEIGHT_QUALITY = 0.25
        self.WEIGHT_URGENCY = 0.15

        self.QUALITY_SCORES = {
            "Excellent": 100.0,
            "Good": 82.0,
            "Average": 55.0,
            "Poor": 10.0
        }

    def evaluate_match(self, donation: Dict[str, Any], ngo: Dict[str, Any], now: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Evaluates a single pair of (Donation, NGO) and calculates match score + reasons.
        """
        if now is None:
            now = datetime.now()

        # 1. Parse dates & Urgency
        expiry_str = donation.get("expiry_time", "")
        hours_left = 6.0  # default
        try:
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"):
                try:
                    expiry_dt = datetime.strptime(expiry_str[:16], fmt[:16])
                    diff = (expiry_dt - now).total_seconds() / 3600.0
                    hours_left = max(0.0, round(diff, 1))
                    break
                except ValueError:
                    continue
        except Exception:
            hours_left = 4.0

        if hours_left <= 0:
            return {
                "ngo_id": ngo.get("id"),
                "ngo_name": ngo.get("organization_name") or ngo.get("name"),
                "match_score": 0.0,
                "is_expired": True,
                "reasons": ["⚠️ Food has reached or exceeded its expiry threshold."],
                "distance_km": 0.0
            }

        # 2. Quality Score
        quality = donation.get("quality", "Good")
        quality_score = self.QUALITY_SCORES.get(quality, 75.0)

        # 3. Distance Calculation
        d_lat = donation.get("latitude")
        d_lng = donation.get("longitude")
        n_lat = ngo.get("latitude")
        n_lng = ngo.get("longitude")
        distance_km = haversine_distance(d_lat, d_lng, n_lat, n_lng)

        # Proximity score (100 for < 1km, 90 for 2km, 70 for 5km, falls off after 15km)
        if distance_km <= 1.0:
            dist_score = 100.0
        elif distance_km <= 3.0:
            dist_score = 90.0 - (distance_km - 1.0) * 5.0
        elif distance_km <= 8.0:
            dist_score = 80.0 - (distance_km - 3.0) * 6.0
        elif distance_km <= 15.0:
            dist_score = 50.0 - (distance_km - 8.0) * 4.0
        else:
            dist_score = max(10.0, 30.0 - (distance_km - 15.0) * 1.5)

        # 4. Capacity Match
        quantity = float(donation.get("quantity", 25))
        ngo_cap = float(ngo.get("capacity", 50))
        ratio = quantity / ngo_cap if ngo_cap > 0 else 1.0

        if 0.5 <= ratio <= 1.2:
            capacity_score = 100.0  # Perfect fit for single batch distribution
        elif ratio < 0.5:
            capacity_score = 80.0   # NGO has excess capacity, easily handles batch
        elif ratio <= 1.8:
            capacity_score = 70.0   # Slightly exceeds regular capacity
        else:
            capacity_score = 45.0   # Batch is much larger than capacity

        # 5. Urgency vs Distance Feasibility
        # If food expires in 2 hours, pickup must be nearby (< 4 km)
        urgency_score = 85.0
        feasible = True
        estimated_pickup_minutes = int(15 + distance_km * 7)  # prep time + travel at 25-30 km/h city avg

        if hours_left < 2.0:
            if distance_km > 5.0:
                feasible = False
                urgency_score = 30.0
            else:
                urgency_score = 95.0  # Prioritize immediate rescue
        elif hours_left < 4.0:
            urgency_score = 90.0

        # Weighted final score (0 - 100 scale)
        composite = (
            (self.WEIGHT_DISTANCE * dist_score) +
            (self.WEIGHT_CAPACITY * capacity_score) +
            (self.WEIGHT_QUALITY * quality_score) +
            (self.WEIGHT_URGENCY * urgency_score)
        )
        match_score = round(min(99.4, max(15.0, composite)), 1)

        # Generate human-readable reasons (NO lat/long)
        reasons = []
        
        # Readable location description
        ngo_area = ngo.get("area") or "Local Area"
        ngo_colony = ngo.get("colony") or ""
        loc_display = f"{ngo_area}" + (f" ({ngo_colony})" if ngo_colony else "")
        
        reasons.append(f"📍 Approximately {distance_km} km away in {loc_display}")
        
        if 0.6 <= ratio <= 1.2:
            reasons.append(f"👥 Beneficiary intake ({int(ngo_cap)} meals) matches donation volume ({int(quantity)} {donation.get('unit', 'meals')})")
        else:
            reasons.append(f"👥 NGO intake capacity: {int(ngo_cap)} beneficiaries")

        reasons.append(f"🟢 Food freshness is rated '{quality}' with {hours_left}h safe consumption window")
        reasons.append(f"⏱️ Pickup possible within ~{estimated_pickup_minutes} minutes")

        return {
            "ngo_id": ngo.get("id"),
            "ngo_name": ngo.get("organization_name") or ngo.get("name"),
            "ngo_phone": ngo.get("phone", "Contact via platform"),
            "ngo_location": f"{ngo.get('city', '')} → {ngo.get('area', '')} → {ngo.get('colony', '')}",
            "distance_km": distance_km,
            "match_score": match_score,
            "reasons": reasons,
            "feasible": feasible,
            "estimated_pickup_minutes": estimated_pickup_minutes,
            "hours_left": hours_left
        }

    def recommend_for_donation(self, donation: Dict[str, Any], ngos_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ranks all verified NGOs for a given donation and returns top matches.
        """
        results = []
        for ngo in ngos_list:
            evaluation = self.evaluate_match(donation, ngo)
            if not evaluation.get("is_expired", False):
                results.append(evaluation)

        # Sort descending by match score
        results.sort(key=lambda x: x["match_score"], reverse=True)
        return results


# Standalone demonstration helper for B.Tech Viva / testing
if __name__ == "__main__":
    print("=" * 65)
    print("  FOOD BRIDGE AI - REDISTRIBUTION & QUALITY ENGINE")
    print("=" * 65)

    ai = FoodRedistributionAI()

    sample_donation = {
        "food_name": "Vegetable Biryani & Raita",
        "quantity": 30,
        "unit": "Meals",
        "quality": "Good",
        "expiry_time": (datetime.now()).strftime("%Y-%m-%d 20:00"),
        "city": "Warangal",
        "area": "Hanamkonda",
        "colony": "Subedari",
        "latitude": 17.9824,
        "longitude": 79.5881
    }

    sample_ngos = [
        {
            "id": 1,
            "organization_name": "Hope Foundation Shelter",
            "name": "Sister Teresa",
            "city": "Warangal",
            "area": "Hanamkonda",
            "colony": "Subedari",
            "capacity": 50,
            "latitude": 17.9810,
            "longitude": 79.5870,
            "phone": "+91 98480 56789"
        },
        {
            "id": 2,
            "organization_name": "Annapurna Seva Trust",
            "name": "Venkatesh Rao",
            "city": "Warangal",
            "area": "Hanamkonda",
            "colony": "Nakkalagutta",
            "capacity": 100,
            "latitude": 17.9860,
            "longitude": 79.6010,
            "phone": "+91 98480 67890"
        },
        {
            "id": 3,
            "organization_name": "Little Angels Orphan Home",
            "name": "Dr. Anjali Deshmukh",
            "city": "Warangal",
            "area": "Kazipet",
            "colony": "Fathimanagar",
            "capacity": 40,
            "latitude": 17.9695,
            "longitude": 79.5305,
            "phone": "+91 98480 78901"
        }
    ]

    recommendations = ai.recommend_for_donation(sample_donation, sample_ngos)
    print(f"\nDonation: {sample_donation['food_name']} ({sample_donation['quantity']} {sample_donation['unit']})")
    # Safe print for Windows consoles
    loc_text = f"{sample_donation['city']} -> {sample_donation['area']} -> {sample_donation['colony']}"
    print(f"Location: {loc_text}\n")

    for idx, rec in enumerate(recommendations, 1):
        print(f"#{idx} [{rec['match_score']}% Match] {rec['ngo_name']}")
        for r in rec["reasons"]:
            # remove emojis for basic cmd/powershell safety
            clean_r = r.encode('ascii', errors='replace').decode('ascii')
            print(f"    {clean_r}")
        print()
