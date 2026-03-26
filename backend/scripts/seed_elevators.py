import os
from pathlib import Path
import requests
import xml.etree.ElementTree as ET
from supabase import create_client, Client
from dotenv import load_dotenv

# .env 로드 (backend/.env 기준)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)


def seed_elevators():
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    API_KEY = os.getenv("PUBLIC_DATA_API_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY or not API_KEY:
        raise Exception("환경변수 설정 안됨 (.env 확인)")

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    url = f"https://openapi.gg.go.kr/TBGGSTATNELVM?Key={API_KEY}&Type=xml&pIndex=1&pSize=1000"

    print(f"📡 API 호출 중: {url}")

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("❌ API 호출 실패:", e)
        return

    root = ET.fromstring(response.text)

    print("===== 수원 엘리베이터 DB 저장 시작 =====")

    inserted = 0
    skipped = 0

    for row in root.findall("row"):
        station_el = row.find("STATN_NM")
        station = station_el.text.strip() if station_el is not None and station_el.text else None

        if not station or "수원" not in station:
            continue

        # 중복 체크
        existing = (
            supabase.table("elevators")
            .select("id")
            .eq("station_name", station)
            .execute()
        )

        if existing.data:
            skipped += 1
            continue

        location_el = row.find("LOC")
        line_el = row.find("OPR_ROUTE_NM")
        operator_el = row.find("RAILROAD_OPR_INST_NM")

        location = location_el.text.strip() if location_el is not None and location_el.text else None
        line = line_el.text.strip() if line_el is not None and line_el.text else None
        operator = operator_el.text.strip() if operator_el is not None and operator_el.text else None

        data = {
            "station_name": station,
            "line_name": line,
            "location": location,
            "start_floor": None,
            "end_floor": None,
            "status": "normal",
            "operator": operator,
        }

        supabase.table("elevators").insert(data).execute()
        inserted += 1

    print("===== 저장 완료 =====")
    print(f"✅ 추가: {inserted}")
    print(f"⏭️ 스킵: {skipped}")


if __name__ == "__main__":
    seed_elevators()