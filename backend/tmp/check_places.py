import os
from dotenv import load_dotenv
import json
from sqlalchemy import text

# .env 로드
load_dotenv()

from db import engine

def check_places_for_elevators():
    try:
        with engine.connect() as conn:
            # 엘리베이터 키워드 검색
            query = text("SELECT * FROM places WHERE category LIKE '%엘리베이터%' OR name LIKE '%엘리베이터%' LIMIT 10")
            result = conn.execute(query)
            rows = [dict(row) for row in result.mappings()]
            
            if rows:
                print(f"--- Found {len(rows)} elevator related places ---")
                print(json.dumps(rows, ensure_ascii=False, indent=2))
            else:
                print("No elevator related places in 'places' table.")
                
            # 전체 카테고리 분포 확인
            query_cat = text("SELECT category, count(*) FROM places GROUP BY category")
            result_cat = conn.execute(query_cat)
            cats = [dict(row) for row in result_cat.mappings()]
            print("--- Category Distribution ---")
            print(json.dumps(cats, ensure_ascii=False, indent=2))
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_places_for_elevators()
