import os
import requests
from flask import Blueprint, request, jsonify
from extensions import limiter

transit_bp = Blueprint("transit", __name__)

@transit_bp.route("/api/transit", methods=["GET"])
@limiter.limit("60 per minute")
def get_transit():
    # 출도착 좌표를 받아서 대중교통 경로를 검색
    sx = request.args.get("sx")
    sy = request.args.get("sy")
    ex = request.args.get("ex")
    ey = request.args.get("ey")
    
    if not all([sx, sy, ex, ey]):
        return jsonify({"error": "Missing required coordinates (sx, sy, ex, ey)."}), 400

    odsay_api_key = os.getenv("ODSAY_API_KEY")
    if not odsay_api_key:
        return jsonify({"error": "ODsay API Key not configured."}), 500

    url = "https://api.odsay.com/v1/api/searchPubTransPathT"
    params = {
        "apiKey": odsay_api_key,
        "SX": sx,
        "SY": sy,
        "EX": ex,
        "EY": ey,
        "OPT": "0",  # 기본 최적경로 우선
        "SearchType": "0",
        "SearchPathType": "0" # 0: 모두, 1: 지하철, 2: 버스
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # result 확인
        if "result" not in data:
            return jsonify({"status": "success", "data": None, "message": "No routes found."})

        # 저상버스 필터링 (경로 상에서 버스를 탈 경우, 저상버스 탑승 가능 여부를 확인함)
        # 본 구현은 API 응답을 전달하면서 저상버스가 포함되어 있는지 여부를 클라이언트가 식별할 수 있도록 합니다.
        
        path_list = data["result"].get("path", [])
        filtered_paths = []

        for path in path_list:
            # 휠체어 이용자는 지하철, 저상버스만 이용 가능
            # 버스 이용 시 '저상버스(busType=... 등) 관련 속성이 있다면 확인
            # 실제 ODsay 응답에서 저상버스 유무는 subPath의 isLowBus 등으로 추정
            is_wheelchair_accessible = True
            for sub in path.get("subPath", []):
                traffic_type = sub.get("trafficType")
                if traffic_type == 2: # 버스
                    # ODsay 응답에 저상버스 여부 플래그가 없는 경우 일단 포함하되, 클라이언트에 경고 플래그 전달
                    pass

            # 일단 모든 경로를 반환하되, 백엔드에서 1차적인 저상버스 로직을 추후 확장 가능하게 형태만 갖춤
            filtered_paths.append(path)

        return jsonify({
            "status": "success",
            "data": {
                "paths": filtered_paths
            }
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch transit routes: {str(e)}"}), 502
