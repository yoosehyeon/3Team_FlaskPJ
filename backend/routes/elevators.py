import random
import uuid
import structlog
from flask import Blueprint, jsonify
from sqlalchemy import text
from db import engine

log = structlog.get_logger()
elevators_bp = Blueprint("elevators", __name__)

# 1. 수원시 주요 역사별 대표 거점 좌표 정의 (PRD 2.2 가이드 준수)
STATION_COORDS = {
    "수원시청": [37.2618, 127.0307],
    "수원": [37.2661, 126.9999],
    "화서": [37.2843, 126.9898],
    "광교중앙": [37.2886, 127.0514],
    "광교": [37.3021, 127.0468],
    "망포": [37.2452, 127.0573],
    "영통": [37.2515, 127.0713],
    "청명": [37.2594, 127.0789],
    "성균관대": [37.3001, 126.9712],
    "고색": [37.2478, 126.9818],
    "매교": [37.2644, 127.0163],
    "매탄권선": [37.2526, 127.0405],
    "오목천": [37.2443, 126.9675]
}

@elevators_bp.route("/api/elevators", methods=["GET"])
def get_elevators():
    """
    수원시 관내 엘리베이터 실시간 편의시설 정보 조회
    [Update]: 실제 DB 스키마(station_name, line_name)와 필드 매핑 정규화
    """
    try:
        table_name = "elevators"
        query = text(f"SELECT * FROM {table_name}")

        with engine.connect() as conn:
            result = conn.execute(query)
            rows = result.mappings().all()

        elevators_list = []
        sorted_stations = sorted(STATION_COORDS.keys(), key=len, reverse=True)

        for row in rows:
            data = dict(row)
            # [필드 정규화]: DB의 station_name 또는 name 사용
            st_name = data.get("station_name") or data.get("name", "수원역")
            base_coord = None

            # [역사명 기반 좌표 매핑]
            for station in sorted_stations:
                if station in st_name:
                    base_coord = STATION_COORDS[station]
                    break
            
            if not base_coord:
                continue

            # [지터링]: 동일 위치 마커 중첩 방지
            jitter_lat = base_coord[0] + random.uniform(-0.0003, 0.0003)
            jitter_lng = base_coord[1] + random.uniform(-0.0003, 0.0003)

            elevators_list.append({
                "id": str(data.get('id', uuid.uuid4())),
                "station_name": st_name,
                "location": data.get("location", "상세 위치 정보 없음"),
                "line": data.get("line_name") or data.get("line", ""),
                "status": data.get("status", "정상"),
                "coordinates": [jitter_lat, jitter_lng]
            })

        return jsonify({
            "status": "success",
            "count": len(elevators_list),
            "elevators": elevators_list
        })

    except Exception as e:
        log.error("Elevator API Error", error=str(e))
        return jsonify({"error": "Failed to fetch elevator data", "details": str(e)}), 500