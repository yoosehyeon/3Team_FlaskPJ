import requests
import xml.etree.ElementTree as ET
from supabase import create_client, Client

# Supabase 연결
SUPABASE_URL = "http://127.0.0.1:54321"
SUPABASE_KEY = "sb_publishable_ACJWlzQHlZjBrEguHvfOxg_3BJgxAaH"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 공공 API
API_KEY = "b1d6920525b14c029524e3530284b8b0"
url = f"https://openapi.gg.go.kr/TBGGSTATNELVM?KEY={API_KEY}&Type=xml&pIndex=1&pSize=1000"

response = requests.get(url)
root = ET.fromstring(response.text)

print("===== 수원 엘리베이터 DB 저장 시작 =====")

for row in root.findall("row"):
    station = row.find("STATN_NM").text if row.find("STATN_NM") is not None else None

    if station and "수원" in station:
        location = row.find("LOC").text if row.find("LOC") is not None else None
        line = row.find("OPR_ROUTE_NM").text if row.find("OPR_ROUTE_NM") is not None else None
        operator = row.find("RAILROAD_OPR_INST_NM").text if row.find("RAILROAD_OPR_INST_NM") is not None else None

        data = {
            "station_name": station,
            "line_name": line,
            "location": location,
            "start_floor": None,
            "end_floor": None,
            "status": "정상",
            "operator": operator
        }

        result = supabase.table("elevators").insert(data).execute()
        print(result)

print("===== 저장 완료 =====")
