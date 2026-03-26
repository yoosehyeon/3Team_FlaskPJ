from flask import Blueprint, jsonify
from sqlalchemy import text
from db import engine

health_bp = Blueprint("health", __name__)

@health_bp.route("/api/health")
def health():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return jsonify({"status": "ok", "db": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "db": f"Supabase Error: {str(e)}"}), 500
