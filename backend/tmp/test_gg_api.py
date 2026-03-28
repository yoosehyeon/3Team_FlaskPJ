import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

def test_gg_elevator_api():
    key = os.getenv("PUBLIC_DATA_API_KEY")
    # 경기데이터드림 지하철역 편의시설 정보 API
    url = f"https://openapi.gg.go.kr/SubwayElevationInfo?KEY={key}&Type=json&pIndex=1&pSize=5"
    
    try:
        res = requests.get(url, timeout=10)
        print(f"Status: {res.status_code}")
        print(f"Raw Response: {res.text[:500]}")
        if res.status_code == 200:
            try:
                data = res.json()
                print("Successfully parsed JSON")
                print(json.dumps(data, ensure_ascii=False, indent=2))
            except:
                print("Response is not JSON")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_gg_elevator_api()
