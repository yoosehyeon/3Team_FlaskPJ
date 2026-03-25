import os
from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from supabase import create_client
from db import engine
from sqlalchemy import text

reports_bp = Blueprint("reports", __name__)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(supabase_url, supabase_key) if supabase_url else None

@reports_bp.route("/api/report", methods=["POST"])
@require_auth
def create_report():
    user = request.user
    
    lat = request.form.get("lat", type=float)
    lng = request.form.get("lng", type=float)
    report_type = request.form.get("type")
    description = request.form.get("description", "")
    image_file = request.files.get("image")

    if not all([lat, lng, report_type]):
        return jsonify({"error": "Missing required fields"}), 400

    image_path = None
    if image_file and supabase:
        try:
            # images 버킷에 업로드
            file_name = f"reports/{user.user.id}_{image_file.filename}"
            res = supabase.storage.from_("reports-images").upload(file_name, image_file.read())
            image_path = file_name
        except Exception as e:
            return jsonify({"error": "Image upload failed", "details": str(e)}), 500

    try:
        with engine.connect() as conn:
            query = text("""
                INSERT INTO reports (user_id, location, type, description, image_path)
                VALUES (:user_id, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :type, :description, :image_path)
                RETURNING id
            """)
            result = conn.execute(query, {
                "user_id": user.user.id,
                "lat": lat,
                "lng": lng,
                "type": report_type,
                "description": description,
                "image_path": image_path
            })
            conn.commit()
            new_id = result.scalar()

        return jsonify({"status": "success", "report_id": new_id})

    except Exception as e:
        return jsonify({"error": "Database query failed", "details": str(e)}), 500
