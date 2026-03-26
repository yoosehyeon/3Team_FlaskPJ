import os
import requests
from flask import Blueprint, request, jsonify
from extensions import limiter
from middleware.auth import require_auth
from markupsafe import escape

route_bp = Blueprint("route", __name__)

@route_bp.route("/api/route", methods=["POST"])
@limiter.limit("30 per minute")
def get_route():
    data = request.get_json()
    if not data or 'start' not in data or 'end' not in data:
        return jsonify({"error": "Invalid request parameters. 'start' and 'end' coordinates are required."}), 400
    
    start_lat = data['start'].get('lat')
    start_lng = data['start'].get('lng')
    end_lat = data['end'].get('lat')
    end_lng = data['end'].get('lng')

    if None in [start_lat, start_lng, end_lat, end_lng]:
        return jsonify({"error": "Missing latitude or longitude in 'start' or 'end'."}), 400

    # Tmap API Key (환경변수에서 로드, 클라이언트 노출 금지)
    tmap_api_key = os.getenv("TMAP_API_KEY")
    if not tmap_api_key:
        return jsonify({"error": "Tmap API Key not configured on the server."}), 500

    # Tmap 보행자 경로 탐색 API 연동
    url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&format=json&callback=result"
    
    headers = {
        "appKey": tmap_api_key,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "startX": str(start_lng),
        "startY": str(start_lat),
        "endX": str(end_lng),
        "endY": str(end_lat),
        "reqCoordType": "WGS84GEO",
        "resCoordType": "WGS84GEO",
        "startName": "출발지",
        "endName": "도착지",
        # 휠체어 전용을 위해 계단 제외 옵션이나, TMAP 보행자 API는 추가 필터링이 필요할 수 있음
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        
        # 계단, 경사 필터링 (간단 예시: feature.properties.facilityType 가 11(계단)이나 12(경사로)인 경우 판별)
        # Tmap API에서 facilityType 11: 계단, 12: 육교, 15: 지하보도 등
        filtered_features = []
        features = result.get('features', [])
        
        has_obstacle = False
        for feature in features:
            properties = feature.get('properties', {})
            # 계단 제어 (11번: 계단, 15번: 횡단보도, 지하보도 등)
            # 휠체어 주행 중 안전을 위해 계단(11)을 포함하는 경로는 위험도 추가
            facility_type = properties.get('facilityType')
            if facility_type == "11" or facility_type == 11:
                has_obstacle = True
            
            filtered_features.append(feature)
        
        # 클라이언트에서는 features 좌표 배열을 순회하여 Map에 표시함
        return jsonify({
            "status": "success",
            "type": "FeatureCollection",
            "features": filtered_features,
            "has_obstacle": has_obstacle,
            "message": "경로 탐색이 완료되었습니다. 계단이나 급경사가 있는지 유의하세요." if has_obstacle else "안전 경로입니다."
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to fetch route from Tmap API: {str(e)}"}), 502