import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()

def test_seoul_elevator_api_v3():
    key = os.getenv("PUBLIC_DATA_API_KEY")
    # 마지막에 역 명칭(수원)을 포함한 경로
    url = f"http://openapi.seoul.go.kr:8088/{key}/json/TbSgcStatus/1/5/수원"
    
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
    test_seoul_elevator_api_v3()
