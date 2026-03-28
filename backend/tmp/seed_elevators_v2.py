import os
from dotenv import load_dotenv
from sqlalchemy import text
import random

load_dotenv()
from db import engine

STATION_DATA = [
    {"name": "수원시청", "line": "수인분당선"},
    {"name": "수원", "line": "1호선/수인분당선"},
    {"name": "화서", "line": "1호선"},
    {"name": "광교중앙", "line": "신분당선"},
    {"name": "광교", "line": "신분당선"},
    {"name": "망포", "line": "수인분당선"},
    {"name": "영통", "line": "수인분당선"},
    {"name": "청명", "line": "수인분당선"},
    {"name": "성균관대", "line": "1호선"},
    {"name": "고색", "line": "수인분당선"},
    {"name": "매교", "line": "수인분당선"},
    {"name": "매탄권선", "line": "수인분당선"},
    {"name": "오목천", "line": "수인분당선"}
]

def seed_elevators_actual():
    try:
        with engine.connect() as conn:
            # 기존 데이터 삭제
            conn.execute(text("DELETE FROM elevators"))
            
            for st in STATION_DATA:
                for i in range(1, random.randint(3, 5)):
                    query = text("""
                        INSERT INTO elevators (station_name, line_name, location, start_floor, end_floor, status, operator)
                        VALUES (:station_name, :line_name, :location, :start_floor, :end_floor, :status, :operator)
                    """)
                    
                    conn.execute(query, {
                        "station_name": st["name"],
                        "line_name": st["line"],
                        "location": f"{i}번 출구 쪽 연결",
                        "start_floor": "B1",
                        "end_floor": "1F",
                        "status": "정상" if random.random() > 0.1 else "점검",
                        "operator": "KORAIL"
                    })
            conn.commit()
            print("Successfully seeded elevators with ACTUAL schema.")
    except Exception as e:
        print(f"Seeding failed: {e}")

if __name__ == "__main__":
    seed_elevators_actual()
