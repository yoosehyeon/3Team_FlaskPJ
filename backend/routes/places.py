import json
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
        return jsonify({"error": "Query parameters 'lat' and 'lng' are required."}), 400

    try:
        # DB 연결 및 ST_DWithin 조회
        # PostGIS에서는 지리 데이터(geography/geometry WGS 84 기반)를 기반으로 거리 검사.
        query = text("""
            SELECT id, name, category, address, image_url, meta,
                   ST_X(location::geometry) as lng, 
                   ST_Y(location::geometry) as lat
            FROM places
            WHERE ST_DWithin(
                location::geography, 
                ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, 
                :radius
            )
        """)

        with engine.connect() as conn:
            result = conn.execute(query, {"lng": lng, "lat": lat, "radius": radius})
            rows = result.mappings().all()

        features = []
        for row in rows:
            # meta 필드가 문자열인 경우 dict로 파싱
            meta_data = row['meta']
            if isinstance(meta_data, str):
                try:
                    meta_data = json.loads(meta_data)
                except json.JSONDecodeError:
                    meta_data = {}

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [row['lng'], row['lat']]
                },
                "properties": {
                    "id": str(row['id']),
                    "name": row['name'],
                    "category": row['category'],
                    "address": row['address'],
                    "image_url": row['image_url'],
                    "meta": meta_data
                }
            })

        return jsonify({
            "type": "FeatureCollection",
            "features": features
        })

    except Exception as e:
        return jsonify({"error": f"Database query failed: {str(e)}"}), 500
