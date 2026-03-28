import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

def test_kric_elevator_api():
    key = os.getenv("PUBLIC_DATA_API_KEY")
    # KRIC 역별 승강설비 운영 정보 조회
    # stationName은 '수원' (시 단위가 아닌 역 명)
    url = f"https://openapi.kric.go.kr/openapi/convenienceInfo/stationElevatorStatus?serviceKey={key}&format=json&stationName=수원"
    
    try:
        res = requests.get(url, timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Raw Response: {res.text[:500]}")
        if res.status_code == 200:
            data = res.json()
            print("Successfully parsed JSON")
            print(json.dumps(data, ensure_ascii=False, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_kric_elevator_api()
