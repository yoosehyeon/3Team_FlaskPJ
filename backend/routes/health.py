from flask import Blueprint, jsonify
from db import engine
from sqlalchemy import text

health_bp = Blueprint("health", __name__)

@health_bp.route("/api/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({"status": "ok", "db": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "db": str(e)}), 500
