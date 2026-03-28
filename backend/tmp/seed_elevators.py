import os
from dotenv import load_dotenv
from sqlalchemy import text
import random

load_dotenv()
from db import engine

STATION_DATA = [
    {"name": "수원시청", "lat": 37.2618, "lng": 127.0307, "line": "수인분당선"},
    {"name": "수원", "lat": 37.2661, "lng": 126.9999, "line": "1호선/수인분당선"},
    {"name": "화서", "lat": 37.2843, "lng": 126.9898, "line": "1호선"},
    {"name": "광교중앙", "lat": 37.2886, "lng": 127.0514, "line": "신분당선"},
    {"name": "광교", "lat": 37.3021, "lng": 127.0468, "line": "신분당선"},
    {"name": "망포", "lat": 37.2452, "lng": 127.0573, "line": "수인분당선"},
    {"name": "영통", "lat": 37.2515, "lng": 127.0713, "line": "수인분당선"},
    {"name": "청명", "lat": 37.2594, "lng": 127.0789, "line": "수인분당선"},
    {"name": "성균관대", "lat": 37.3001, "lng": 126.9712, "line": "1호선"},
    {"name": "고색", "lat": 37.2478, "lng": 126.9818, "line": "수인분당선"},
    {"name": "매교", "lat": 37.2644, "lng": 127.0163, "line": "수인분당선"},
    {"name": "매탄권선", "lat": 37.2526, "lng": 127.0405, "line": "수인분당선"},
    {"name": "오목천", "lat": 37.2443, "lng": 126.9675, "line": "수인분당선"}
]

def seed_elevators():
    try:
        with engine.connect() as conn:
            # 기존 데이터 삭제 (중복 방지)
            conn.execute(text("DELETE FROM elevators"))
            
            for st in STATION_DATA:
                # 역당 1~2개의 가상 엘리베이터 마커 생성
                for i in range(1, random.randint(2, 4)):
                    lat = st["lat"] + random.uniform(-0.0002, 0.0002)
                    lng = st["lng"] + random.uniform(-0.0002, 0.0002)
                    
                    query = text("""
                        INSERT INTO elevators (name, location, status, building, floor)
                        VALUES (:name, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :status, :building, :floor)
                    """)
                    
                    conn.execute(query, {
                        "name": st["name"],
                        "lat": lat,
                        "lng": lng,
                        "status": "normal" if random.random() > 0.1 else "maintenance",
                        "building": st["line"],
                        "floor": f"{i}번 출구 쪽"
                    })
            conn.commit()
            print("Successfully seeded elevator data for Suwon area.")
    except Exception as e:
        print(f"Seeding failed: {e}")

if __name__ == "__main__":
    seed_elevators()
