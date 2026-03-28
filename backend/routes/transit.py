import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import unquote
from flask import Blueprint, request, jsonify
from extensions import limiter
import structlog

transit_bp = Blueprint("transit", __name__)
log = structlog.get_logger()

# 환경 변수 로드
ODSAY_KEY = os.getenv("ODSAY_API_KEY")
TMAP_KEY = os.getenv("TMAP_API_KEY")
# [주의]: 버스 정보 API 키는 이미 인코딩된 상태로 넘어오므로 unquote하지 않고 그대로 유지
BUS_KEY = os.getenv("BUS_DATA_API_KEY", "") 
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
    Tmap 보행자(안전경로) + ODsay 대중교통 + 실시간 저상버스 정보를 통합한 응답 반환
    """
    try:
        data = request.get_json()
        
        # [호환성 처리]: PRD 규격({start: {lat, lng}}) 또는 기존 규격(startX, startY) 모두 수용
        start = data.get("start")
        end = data.get("end")
        
        if start and end:
            s_lat, s_lng = float(start.get('lat')), float(start.get('lng'))
            e_lat, e_lng = float(end.get('lat')), float(end.get('lng'))
        else:
            s_lat = data.get("startY") or data.get("sy")
            s_lng = data.get("startX") or data.get("sx")
            e_lat = data.get("endY") or data.get("ey")
            e_lng = data.get("endX") or data.get("ex")
            
            if None in [s_lat, s_lng, e_lat, e_lng]:
                return jsonify({"error": "출발지 및 목적지 좌표가 필요합니다. (startX/Y 또는 start {lat, lng})"}), 400
            
            s_lat, s_lng, e_lat, e_lng = float(s_lat), float(s_lng), float(e_lat), float(e_lng)

        # 1. ODsay 대중교통 경로 조회
        odsay_url = "https://api.odsay.com/v1/api/searchPubTransPathT"
        od_params = {
            "apiKey": ODSAY_KEY, "SX": s_lng, "SY": s_lat, "EX": e_lng, "EY": e_lat, "SearchPathType": 0
        }
        headers = {"Referer": "https://test1234112.netlify.app"}
        od_res = requests.get(odsay_url, params=od_params, headers=headers, timeout=10)
        od_data = od_res.json()

        if "result" not in od_data:
            transit_mock_env = os.getenv("TRANSIT_MOCK", "false").lower() == "true"
            if transit_mock_env:
                return jsonify(generate_mock_transit(s_lng, s_lat, e_lng, e_lat)), 200
            
            return jsonify({
                "status": "error",
                "message": "이용 가능한 대중교통 경로가 없습니다.",
                "totalTime": 0, "totalDistance": 0, "steps": []
            }), 200

        path = od_data["result"]["path"][0]
        sub_paths = path.get("subPath", [])
        
        steps = [] # 프론트 Schema 호환을 위해 timeline 대신 steps 사용
        num_subs = len(sub_paths)

        for i, sub in enumerate(sub_paths):
            traffic_type = sub.get("trafficType") # 1: 지하철, 2: 버스, 3: 도보
            
            step_data = {
                "type": traffic_type,
                "distance": sub.get("distance", 0),
                "sectionTime": sub.get("sectionTime", 0),
            }

            if traffic_type == 3: # 도보
                curr_s = {"lat": s_lat, "lng": s_lng} if i == 0 else \
                         {"lat": float(sub_paths[i-1].get("endY")), "lng": float(sub_paths[i-1].get("endX"))}
                curr_e = {"lat": e_lat, "lng": e_lng} if i == num_subs - 1 else \
                         {"lat": float(sub_paths[i+1].get("startY")), "lng": float(sub_paths[i+1].get("startX"))}
                
                step_data.update({
                    "category": "walking",
                    "color": "#FF9800",
                    "summary": "라스트마일 1" if i == 0 else ("라스트마일 2" if i == num_subs-1 else "환승 이동"),
                    "path": get_tmap_pedestrian(curr_s['lng'], curr_s['lat'], curr_e['lng'], curr_e['lat'])
                })
            
            elif traffic_type in [1, 2]: # 대중교통
                is_bus = (traffic_type == 2)
                lane = sub.get("lane", [{}])[0]
                bus_no = lane.get("busNo") if is_bus else lane.get("name")
                
                step_data.update({
                    "category": "transit",
                    "color": "#2196F3",
                    "startName": sub.get("startName"),
                    "endName": sub.get("endName"),
                    "busNo": bus_no,
                    "summary": f"{bus_no} 탑승 ({sub.get('sectionTime')}분)",
                    "path": extract_odsay_coords(sub),
                })
                
                # 버스인 경우 실시간 저상 여부 + 도착 예정 시간 체크
                if is_bus:
                    is_low, p_time = check_bus_arrival_info(sub.get("startLocalStationID"), bus_no)
                    step_data["isLowFloor"] = is_low
                    step_data["predictTime"] = p_time # 도착 예정 시간 (분)
                else:
                    step_data["isLowFloor"] = False
                    step_data["predictTime"] = None

            steps.append(step_data)

        # 프론트엔드 TransitResponseSchema 규격에 맞춰 필드 구성
        return jsonify({
            "status": "success",
            "totalTime": path["info"].get("totalTime"),
            "totalDistance": path["info"].get("totalDistance"),
            "steps": steps
        })

    except Exception as e:
        log.error("transit_integration_failed", error=str(e))
        return jsonify({"error": "통합 경로 조회 중 오류가 발생했습니다.", "details": str(e)}), 500

def extract_odsay_coords(sub):
    """ ODsay subPath에서 정류장 좌표를 {lat, lng} 배열로 추출 """
    coords = [{"lat": float(sub.get("startY")), "lng": float(sub.get("startX"))}]
    stations = sub.get("passStopList", {}).get("stations", [])
    for st in stations:
        coords.append({"lat": float(st.get("y")), "lng": float(st.get("x"))})
    coords.append({"lat": float(sub.get("endY")), "lng": float(sub.get("endX"))})
    return coords

def get_tmap_pedestrian(sx, sy, ex, ey):
    """ Tmap 계단 회피 보행자 경로 (lat, lng 통일 규격) """
    if sx == ex and sy == ey: return []
    url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&format=json"
    headers = {"appKey": TMAP_KEY}
    payload = {
        "startX": sx, "startY": sy,
        "endX": ex, "endY": ey,
        "startName": "출발", "endName": "도착",
        "searchOption": "30" # 계단 회피 옵션
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

def check_bus_arrival_info(station_id, bus_no):
    """
    공공데이터포털 경기도 버스도착정보 조회 (JSON 규격 맞춤 수정)
    [Update]: 실제 응답 구조(msgHeader, msgBody, busArrivalList) 반영
    """
    if not station_id or not bus_no:
        return False, None

    url = "https://apis.data.go.kr/6410000/busarrivalservice/v2/getBusArrivalListv2"
    
    try:
        full_url = f"{url}?serviceKey={BUS_KEY}&stationId={station_id}&format=json"
        
        res = requests.get(full_url, timeout=10)
        
        if res.status_code != 200:
            log.error("GBIS API Connection failed", status=res.status_code)
            return False, None

        data = res.json()
        
        # [데이터 구조 매핑]: response -> msgHeader -> resultCode
        response_obj = data.get("response", {})
        msg_header = response_obj.get("msgHeader", {})
        result_code = msg_header.get("resultCode")
        
        if str(result_code) != "0":
            # log.warning("GBIS API Error response", 
            #             code=result_code, 
            #             msg=msg_header.get("resultMessage", "No message"))
            return False, None

        # [아이템 목록 탐색]: response -> msgBody -> busArrivalList
        msg_body = response_obj.get("msgBody", {})
        arrival_list = msg_body.get("busArrivalList", [])
        
        for item in arrival_list:
            if item is None: continue
            
            # 버스 번호 매칭
            if str(item.get("routeName")).strip() == str(bus_no).strip() or \
               str(item.get("busNo")).strip() == str(bus_no).strip():
                
                l1 = str(item.get("lowPlate1", "0"))
                l2 = str(item.get("lowPlate2", "0"))
                is_low_floor = (l1 == "1" or l2 == "1")
                predict_time = item.get("predictTime1")
                
                # log.info("Bus mapping success", 
                #          bus_no=bus_no, 
                #          is_low=is_low_floor, 
                #          predict=predict_time)
                return is_low_floor, str(predict_time) if predict_time is not None else None

        # log.info("No matching bus found in arrival list", bus_no=bus_no)
        return False, None

    except Exception as e:
        log.error("GBIS API processing error", error=str(e))
        return False, None
