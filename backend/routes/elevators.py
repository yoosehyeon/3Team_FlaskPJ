import random
import uuid
from flask import Blueprint, jsonify
from sqlalchemy import text
from db import engine

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
    try:
        # 1. 테이블 존재 여부에 따른 동적 쿼리 (elevator vs elevators)
        table_name = "elevator"
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1 FROM elevator LIMIT 1"))
        except:
            table_name = "elevators"

        query = text(f"SELECT * FROM {table_name}")

        with engine.connect() as conn:
            result = conn.execute(query)
            rows = result.mappings().all()

        elevators_list = []
        sorted_stations = sorted(STATION_COORDS.keys(), key=len, reverse=True)

        for row in rows:
            data = dict(row) # 딕셔너리 변환으로 안전하게 접근
            st_name = data.get("station_name") or data.get("name", "")
            base_coord = None

            # 역사명 매핑 로직
            for station in sorted_stations:
                if station in st_name:
                    base_coord = STATION_COORDS[station]
                    break
            
            # 매칭되는 역 좌표가 없는 경우 건너뜁니다 (지도 중앙에 뭉치지 않게)
            if not base_coord:
                continue

            # 지터링 적용 (동일 역 마커 분산)
            jitter_lat = base_coord[0] + random.uniform(-0.00015, 0.00015)
            jitter_lng = base_coord[1] + random.uniform(-0.00015, 0.00015)

            elevators_list.append({
                "id": str(data.get('id', uuid.uuid4())),
                "station_name": st_name,
                "location": data.get("location", "상세 위치 정보 없음"),
                "line": data.get("line", ""),
                "status": data.get("status", "정상"),
                "coordinates": [jitter_lat, jitter_lng]
            })

        return jsonify({
            "status": "success",
            "count": len(elevators_list),
            "elevators": elevators_list
        })

    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"!!! Elevator API Error !!!\n{err_msg}")
        return jsonify({
            "error": "Database query failed",
            "details": str(e)
        }), 500

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Database query failed: {str(e)}"}), 500