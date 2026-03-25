from flask import Blueprint, request, jsonify
from sqlalchemy import text
from db import engine

places_bp = Blueprint("places", __name__)

@places_bp.route("/api/places", methods=["GET"])
def get_places():
    lat = request.args.get("lat", type=float)
    lng = request.args.get("lng", type=float)
    radius = request.args.get("radius", default=300, type=int)

    if lat is None or lng is None:
        return jsonify({"error": "lat and lng are required"}), 400

    try:
        with engine.connect() as conn:
            # PostGIS ST_DWithin 이용 반경 검색
            query = text("""
                SELECT id, name, category, address, ST_AsGeoJSON(location) as location_json, image_url, meta, created_at
                FROM places
                WHERE ST_DWithin(
                    location::geography,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
                    :radius
                )
            """)
            
            result = conn.execute(query, {"lat": lat, "lng": lng, "radius": radius})
            
            places = []
            for row in result:
                places.append({
                    "id": str(row.id),
                    "name": row.name,
                    "category": row.category,
                    "address": row.address,
                    "location": row.location_json,
                    "image_url": row.image_url,
                    "meta": row.meta,
                    "created_at": row.created_at.isoformat() if row.created_at else None
                })

            return jsonify({"status": "success", "data": places})

    except Exception as e:
        return jsonify({"error": "Database query failed", "details": str(e)}), 500
