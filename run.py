"""EQUITY HUB backend entry point. Run from project root: python run.py"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.app import app

if __name__ == "__main__":
    app.run(debug=True, port=5000)
