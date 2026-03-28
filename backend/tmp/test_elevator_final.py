import os
import requests
from dotenv import load_dotenv
import json
from urllib.parse import unquote

load_dotenv()

def test_public_data_elevator_api():
    # 버스 연동 시 성공했던 인코딩된 키(Base64) 사용 시도
    key = os.getenv("BUS_DATA_API_KEY")
    # 국토교통부(TAGO)_지하철정보 - 역 편의시설 정보
    # stationName은 인코딩 필요할 수 있음
    url = f"http://apis.data.go.kr/1613000/SubwayInfoService/getStationConvenienceList?serviceKey={key}&stationName=수원&format=json&pSize=5"
    
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
                print("Response is not JSON (might be XML error)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_public_data_elevator_api()
