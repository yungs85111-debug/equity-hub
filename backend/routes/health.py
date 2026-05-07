from flask import Blueprint, jsonify
import sqlite3

from backend.config import DATA_MODE, DB_PATH

health_bp = Blueprint("health", __name__)


@health_bp.get("/api/health")
def health():
    price_date = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        row = conn.execute("SELECT MAX(price_date) FROM prices").fetchone()
        if row:
            price_date = row[0]
        conn.close()
    except Exception:
        pass
    return jsonify({"status": "ok", "data_mode": DATA_MODE, "price_date": price_date})
