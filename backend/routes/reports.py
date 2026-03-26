import os
import uuid
import mimetypes
from flask import Blueprint, request, jsonify
from middleware.auth import require_auth, supabase
from db import engine
from sqlalchemy import text

reports_bp = Blueprint("reports", __name__)

@reports_bp.route("/api/report", methods=["POST"])
@require_auth
def create_report():
    if not supabase:
        return jsonify({"error": "Supabase client unconfigured"}), 500

    user_id = request.user.user.id if request.user and request.user.user else None
    if not user_id:
        return jsonify({"error": "Failed to get user details from token"}), 401
    
    # Form data 파싱
    type_ = request.form.get("type")
    description = request.form.get("description", "")
    lat = request.form.get("lat")
    lng = request.form.get("lng")

    if not type_ or not lat or not lng:
        return jsonify({"error": "Missing required fields: type, lat, lng"}), 400

    image_path = None
    file = request.files.get("image")
    if file and file.filename: # 이미지가 있을 때만 업로드
        filename = f"{uuid.uuid4()}_{file.filename}"
        mime_type, _ = mimetypes.guess_type(file.filename)
        mime_type = mime_type or "application/octet-stream"

        file_bytes = file.read()
        res = supabase.storage.from_("reports-images").upload(
            path=filename,
            file=file_bytes,
            file_options={"content-type": mime_type}
        )

        image_path = f"reports-images/{filename}"

    try:
        query = text("""
            INSERT INTO reports (user_id, location, type, description, image_path, status)
            VALUES (:user_id, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :type, :description, :image_path, 'pending')
            RETURNING id
        """)

        with engine.connect() as conn:
            result = conn.execute(query, {
                "user_id": user_id,
                "lng": float(lng),
                "lat": float(lat),
                "type": type_,
                "description": description,
                "image_path": image_path
            })
            conn.commit()
            new_id = result.fetchone()[0]

        return jsonify({"status": "success", "id": str(new_id)})

    except Exception as e:
        return jsonify({"error": f"Failed to insert report: {str(e)}"}), 500
