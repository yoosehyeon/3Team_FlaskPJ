import os
from dotenv import load_dotenv
from sqlalchemy import text
import json

load_dotenv()
from db import engine

def check_schema():
    try:
        with engine.connect() as conn:
            query = text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'elevators'")
            result = conn.execute(query)
            columns = [dict(row) for row in result.mappings()]
            print("--- Actual Columns in 'elevators' table ---")
            print(json.dumps(columns, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Schema check failed: {e}")

if __name__ == "__main__":
    check_schema()
