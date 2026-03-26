import os
import traceback
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, ".env")
load_dotenv(dotenv_path)

from sqlalchemy import text
from db import engine

def inspect_elevators():
    print("--- Elevators Table Inspection ---")
    try:
        with engine.connect() as conn:
            # 1. 컬럼명 확인
            res_cols = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'elevator' OR table_name = 'elevators';"))
            print("Columns found:")
            cols = [r[0] for r in res_cols]
            for c in cols:
                print(f" - {c}")
            
            # 2. 첫 3개 데이터 샘플
            table_name = 'elevator' if 'elevator' in [t[0] for t in conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))] else 'elevators'
            print(f"Sampling data from '{table_name}':")
            res_data = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 3"))
            for r in res_data.mappings():
                print(dict(r))
                
    except Exception:
        traceback.print_exc()

if __name__ == "__main__":
    inspect_elevators()
