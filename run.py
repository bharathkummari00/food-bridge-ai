"""
Food Bridge AI Launcher
Runs the complete full-stack web application.
"""

import sys
import os
from pathlib import Path

# Add project root to Python module search path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import app

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("  FOOD BRIDGE AI - FOOD REDISTRIBUTION SYSTEM")
    print("  Status: ONLINE")
    print("  Open in your browser: http://127.0.0.1:5000")
    print("=" * 65 + "\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
