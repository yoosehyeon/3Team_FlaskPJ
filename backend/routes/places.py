import json
from flask import Blueprint, request, jsonify
from sqlalchemy import text
from db import engine
from pydantic import BaseModel, Field, ValidationError

places_bp = Blueprint("places", __name__)

# [백엔드 검증]: Request 쿼리 파라미터 유효성 검사 스키마
class PlaceQueryParams(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="위도")
    lng: float = Field(..., ge=-180, le=180, description="경도")
    radius: int = Field(default=300, ge=10, le=5000, description="검색 반경(m)")

@places_bp.route("/api/places", methods=["GET"])
def get_places():
    try:
        # Pydantic 파싱 (실패 시 400 에러 및 구체적인 사유 반환)
        params = PlaceQueryParams(
            lat=request.args.get("lat"),
            lng=request.args.get("lng"),
            radius=request.args.get("radius", 300)
        )
    except ValidationError as e:
        return jsonify({
            "error": "잘못된 요청 파라미터입니다. (위경도 또는 반경 값 확인)",
            "details": e.errors()
        }), 400

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
            result = conn.execute(query, {"lng": params.lng, "lat": params.lat, "radius": params.radius})
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
