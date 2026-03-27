import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from flask import Blueprint, request, jsonify
from extensions import limiter
import structlog

transit_bp = Blueprint("transit", __name__)
log = structlog.get_logger()

# 환경 변수 로드 (공공데이터 키는 unquote 처리하여 더블 인코딩 방지)
ODSAY_KEY = os.getenv("ODSAY_API_KEY")
TMAP_KEY = os.getenv("TMAP_API_KEY")
PUBLIC_KEY = unquote(os.getenv("PUBLIC_DATA_API_KEY", ""))
TRANSIT_MOCK = os.getenv("TRANSIT_MOCK", "false").lower() == "true"


def generate_mock_transit(start_x, start_y, end_x, end_y):
    """
    수원시 실제 저상버스 노선 기반 Mock 데이터 생성.
    Tmap API를 호출하여 실제 도로를 따라가는 정밀 경로(곡선)를 생성함.
    """
    import math
    dx = float(end_x) - float(start_x)
    dy = float(end_y) - float(start_y)
    total_dist = math.sqrt(dx**2 + dy**2) * 111000
    total_time = max(10, int(total_dist / 400))

    suwon_low_floor_routes = [
        {"busNo": "13-1", "startName": "수원남부공영차고지", "endName": "망포역", "isLowFloor": True},
        {"busNo": "19",   "startName": "수원역",           "endName": "영통구청",  "isLowFloor": True},
        {"busNo": "30",   "startName": "수원남부공영차고지", "endName": "구운동삼환아파트", "isLowFloor": True},
        {"busNo": "7780", "startName": "수원시청",          "endName": "강남역",   "isLowFloor": True},
    ]

    import random
    random.seed(int(float(start_x) * 1000))
    route = random.choice(suwon_low_floor_routes)

    # 실제 곡선 경로 확보를 위해 Tmap 호출 (Mock 상황에서도 길은 제대로 보여주기 위함)
    real_path = get_tmap_pedestrian(start_x, start_y, end_x, end_y)
    
    # 경로를 3등분하여 도보-버스-도보 시뮬레이션
    path_len = len(real_path)
    steps = []
    
    if path_len > 10:
        p1, p2 = path_len // 4, (path_len * 3) // 4
        # 1. 도보
        steps.append({
            "type": 3, "distance": 400, "sectionTime": 6, 
            "path": real_path[:p1], "instruction": "출발지에서 승차 정류장까지 이동"
        })
        # 2. 버스
        steps.append({
            "type": 2, "distance": int(total_dist * 0.7), "sectionTime": int(total_time * 0.6),
            "isLowFloor": route["isLowFloor"], "busNo": route["busNo"],
            "startName": route["startName"], "endName": route["endName"],
            "path": real_path[p1:p2]
        })
        # 3. 도보
        steps.append({
            "type": 3, "distance": 300, "sectionTime": 4, 
            "path": real_path[p2:], "instruction": "하차 후 목적지까지 이동"
        })
    else:
        # 경로가 너무 짧으면 그냥 전체 도보 처리
        steps.append({"type": 3, "distance": int(total_dist), "sectionTime": total_time, "path": real_path})

    return {
        "status": "success",
        "message": "[Mock Mode] 수원시 실제 저상버스 노선 기반 정밀 경로 안내",
        "totalTime": total_time,
        "totalDistance": int(total_dist),
        "steps": steps
    }

@transit_bp.route("/api/transit", methods=["POST"])
@limiter.limit("60 per minute")
def get_integrated_transit():
    """
    Tmap 보행자 + ODsay 대중교통 + 저상버스 실시간 매시업 라우트
    """
    # 환경 변수 체크를 함수 안에서 수행 (HMR/Reload 대응)
    transit_mock_env = os.getenv("TRANSIT_MOCK", "false").lower() == "true"
    
    try:
        data = request.get_json()
        start_x = data.get("startX") # lng
        start_y = data.get("startY") # lat
        end_x = data.get("endX")     # lng
        end_y = data.get("endY")     # lat

        if not all([start_x, start_y, end_x, end_y]):
            return jsonify({"error": "Missing coordinates (startX, startY, endX, endY)."}), 400

        # 1. ODsay 대중교통 경로 조회
        odsay_url = "https://api.odsay.com/v1/api/searchPubTransPathT"
        odsay_params = {
            "apiKey": ODSAY_KEY,
            "SX": start_x, "SY": start_y,
            "EX": end_x, "EY": end_y,
            "SearchPathType": 0
        }
        
        od_res = requests.get(odsay_url, params=odsay_params, timeout=10)
        od_data = od_res.json()

        if "result" not in od_data:
            # Mock 모드가 켜져 있으면 실제 수원시 노선 기반 가상 데이터 반환
            if transit_mock_env:
                log.info("transit_mock_mode", reason="ODsay returned no result, using mock data")
                return jsonify(generate_mock_transit(start_x, start_y, end_x, end_y)), 200

            # Mock 모드 OFF: 심야 시간대 안내 메시지
            return jsonify({
                "status": "success",
                "message": "현재 시간대(심야 등)에는 운행 중인 대중교통 노선이 없거나, 검색 가능한 경로가 없습니다.",
                "totalTime": 0,
                "totalDistance": 0,
                "steps": []
            }), 200

        # 최적 경로 (첫 번째) 분석
        path = od_data["result"]["path"][0]
        sub_paths = path.get("subPath", [])

        integrated_steps = []
        for sub in sub_paths:
            traffic_type = sub.get("trafficType") # 1: 지하철, 2: 버스, 3: 도보
            
            step_data = {
                "type": traffic_type,
                "distance": sub.get("distance", 0),
                "sectionTime": sub.get("sectionTime", 0),
            }

            if traffic_type == 3: # 도보 구간 ➔ Tmap 보행자 경로 정밀화
                step_data["path"] = get_tmap_pedestrian(
                    sub.get("startX", start_x), sub.get("startY", start_y),
                    sub.get("endX", end_x), sub.get("endY", end_y)
                )
            
            elif traffic_type == 2: # 버스 구간 ➔ 저상버스 실시간 검증
                bus_info = sub.get("lane", [{}])[0]
                station_id = sub.get("startLocalStationID")
                bus_no = bus_info.get("busNo")
                
                step_data["isLowFloor"] = check_low_floor_bus(station_id, bus_no)
                step_data["busNo"] = bus_no
                step_data["startName"] = sub.get("startName")
                step_data["endName"] = sub.get("endName")

            integrated_steps.append(step_data)

        return jsonify({
            "status": "success",
            "totalTime": path["info"].get("totalTime"),
            "totalDistance": path["info"].get("totalDistance"),
            "steps": integrated_steps
        })

    except Exception as e:
        log.error("transit_mashup_failed", error=str(e))
        return jsonify({"error": "Integrated Transit Error", "details": str(e)}), 500

def get_tmap_pedestrian(sx, sy, ex, ey):
    """ Tmap 계단 회피 보행자 경로 """
    url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&format=json"
    headers = {"appKey": TMAP_KEY}
    payload = {
        "startX": sx, "startY": sy,
        "endX": ex, "endY": ey,
        "startName": "start", "endName": "end",
        "searchOption": "30"
    }
    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        tmap_data = res.json()
        coords = []
        for feature in tmap_data.get("features", []):
            if feature["geometry"]["type"] == "LineString":
                for c in feature["geometry"]["coordinates"]:
                    coords.append({"lat": c[1], "lng": c[0]})
        return coords
    except:
        return []

def check_low_floor_bus(station_id, bus_no):
    """ 경기도 공공데이터 실시간 저상버스 체크 """
    if not station_id or not bus_no: return False
    url = "http://openapi.gbis.go.kr/ws/rest/busarrivalservice/station"
    params = {"serviceKey": PUBLIC_KEY, "stationId": station_id}
    try:
        res = requests.get(url, params=params, timeout=5)
        root = ET.fromstring(res.text)
        for arrival in root.findall(".//busArrivalList"):
            if arrival.find("busNo").text == bus_no:
                # lowPlate: 1 (저상), 0 (일반)
                l1 = arrival.find("lowPlate1").text if arrival.find("lowPlate1") is not None else "0"
                l2 = arrival.find("lowPlate2").text if arrival.find("lowPlate2") is not None else "0"
                return l1 == "1" or l2 == "1"
        return False
    except:
        return False
