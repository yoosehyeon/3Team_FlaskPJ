from flask import Blueprint, jsonify
from sqlalchemy import text
from db import engine

elevators_bp = Blueprint("elevators", __name__)

@elevators_bp.route("/api/elevators", methods=["GET"])
def get_elevators():
    try:
        # 도대체 테이블에 뭐가 있는지 일단 다 가져와 봅니다.
        query = text("SELECT * FROM elevators")

        with engine.connect() as conn:
            result = conn.execute(query)
            rows = result.mappings().all()

        # 🚨 [중요] 터미널에 첫 번째 데이터의 진짜 모습을 출력합니다!
        if rows:
            print("\n================ [DB 데이터 구조 확인] ================")
            print(dict(rows[0]))
            print("========================================================\n")

        elevators_list = []
        for row in rows:
            lng, lat = 0.0, 0.0
            
            # 1. 만약 lat, lng 이라는 칸이 따로 있다면 그걸 씁니다.
            if 'lat' in row and 'lng' in row:
                try:
                    lat = float(row['lat'])
                    lng = float(row['lng'])
                except: pass
            
            # 2. latitude, longitude 라는 칸이 있다면 그걸 씁니다.
            elif 'latitude' in row and 'longitude' in row:
                try:
                    lat = float(row['latitude'])
                    lng = float(row['longitude'])
                except: pass
            
            # 3. location 칸을 파싱해봅니다 (단, '2F' 같은 글자가 나오면 무시하고 안 뻗게 만듭니다!)
            else:
                loc = row.get('location')
                if loc and isinstance(loc, str):
                    try:
                        cleaned = loc.replace('(', '').replace(')', '').replace('POINT', '').replace(',', ' ')
                        parts = cleaned.split()
                        if len(parts) >= 2:
                            lng = float(parts[0])
                            lat = float(parts[1])
                    except ValueError:
                        pass # '2F' 같은 글자가 나와도 그냥 패스! (0.0, 0.0으로 처리)

            elevators_list.append({
                "id": str(row['id']),
                "coordinates": [lng, lat]
            })

        return jsonify({
            "status": "success",
            "elevators": elevators_list
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Database query failed: {str(e)}"}), 500