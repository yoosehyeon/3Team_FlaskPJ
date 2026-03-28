import os
from dotenv import load_dotenv
import json
import sqlalchemy
from sqlalchemy import text

# .env 로드
load_dotenv()

from db import engine

def get_elevator_data():
    tables = ["elevator", "elevators"]
    for table_name in tables:
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 5"))
                rows = [dict(row) for row in result.mappings()]
                print(f"--- Data from {table_name} ---")
                print(json.dumps(rows, ensure_ascii=False, indent=2))
                return
        except Exception as e:
            print(f"Table {table_name} check failed: {e}")
            continue

if __name__ == "__main__":
    get_elevator_data()
