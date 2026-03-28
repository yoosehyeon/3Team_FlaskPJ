import requests
import json

url = "http://127.0.0.1:5000/api/transit"
payload = {
    "startX": "127.0016",
    "startY": "37.2655", # 수원역 부근
    "endX": "127.0286",
    "endY": "37.2635" # 수원시청 부근
}

try:
    res = requests.post(url, json=payload, timeout=15)
    if res.status_code == 200:
        data = res.json()
        
        # 보기 편하도록 거대한 좌표 배열(path)은 길이를 표시하고 생략합니다.
        for step in data.get("steps", []):
            if "path" in step and isinstance(step["path"], list):
                step["path"] = f"... [총 {len(step['path'])} 개의 경위도 좌표 데이터 배열] ..."
                
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        print("Error:", res.status_code, res.text)
except Exception as e:
    print("Exception:", e)
