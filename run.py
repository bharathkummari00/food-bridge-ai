"""
Food Bridge AI Root Launcher
Runs the complete full-stack web application from the workspace root.
"""

import sys
import os
from pathlib import Path

# Add FoodBridgeAI directory to sys.path
PROJECT_DIR = Path(__file__).resolve().parent / "FoodBridgeAI"
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# Switch working directory to FoodBridgeAI for correct relative paths
os.chdir(PROJECT_DIR)

from backend.app import app

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  FOOD BRIDGE AI - FOOD REDISTRIBUTION SYSTEM")
    print("  Status: ONLINE")
    print("  Open in your browser: http://127.0.0.1:5000")
    print("=" * 65 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
