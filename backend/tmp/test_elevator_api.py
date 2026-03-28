import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

def test_seoul_elevator_api():
    key = os.getenv("PUBLIC_DATA_API_KEY")
    # 서울시 열린데이터 광장 승강기 실시간 상태 API 엔드포인트
    url = f"http://openapi.seoul.go.kr:8088/{key}/json/subwayElevatorStatus/1/5/"
    
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
    test_seoul_elevator_api()
