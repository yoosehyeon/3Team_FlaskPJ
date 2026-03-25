import os
import requests
from flask import Blueprint, request, jsonify
from middleware.auth import require_auth
from app import limiter

route_bp = Blueprint("route", __name__)

@route_bp.route("/api/route", methods=["POST"])
@limiter.limit("30 per minute")
@require_auth
def get_route():
    data = request.get_json()
    if not data or 'start' not in data or 'end' not in data:
        return jsonify({"error": "Invalid request parameters"}), 400

    start = data['start']
    end = data['end']

    tmap_api_key = os.getenv("TMAP_API_KEY")
    if not tmap_api_key:
        return jsonify({"error": "TMAP API key is missing"}), 500

    url = "https://apis.openapi.sk.com/tmap/routes/pedestrian?version=1&format=json"
    
    headers = {
        "appKey": tmap_api_key,
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    payload = {
        "startX": str(start['lng']),
        "startY": str(start['lat']),
        "endX": str(end['lng']),
        "endY": str(end['lat']),
        "reqCoordType": "WGS84GEO",
        "resCoordType": "WGS84GEO",
        "startName": "출발지",
        "endName": "도착지",
        "searchOption": 30 # 최적경로 우선 (휠체어 특화 옵션 없으므로 후처리 필터링)
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        tmap_data = response.json()
        
        # 휠체어 안전 경로를 위해 계단(STEP) 또는 급경사(SLOPE)가 있는 경로 배제
        safe_features = []
        is_safe_route = True
        
        for feature in tmap_data.get('features', []):
            properties = feature.get('properties', {})
            facility_type = properties.get('facilityType', '')
            
            # 11: 계단, 12: 경사로(급경사 위험), 14: 횡단보도(계단형)
            # Tmap 문서 기준 11(계단), 12(경사로), 14(징검다리), 15(지하보도), 16(육교) 등을 회피지표로 삼음. 상세 로직은 프로젝트 기준.
            # PRD: 응답에서 계단(STEP)·경사(SLOPE) 구간을 필터링
            if facility_type in ('11', '12', '14', '15', '16'):
                is_safe_route = False
                break
            
            safe_features.append(feature)
            
        if not is_safe_route:
            return jsonify({"error": "안전한 휠체어 경로를 찾을 수 없습니다. (계단 또는 급경사 구간 포함)"}), 404
            
        return jsonify({
            "type": "FeatureCollection",
            "features": safe_features
        })

    except requests.exceptions.RequestException as e:
         return jsonify({"error": "TMAP API Request Failed", "details": str(e)}), 502
    except Exception as e:
         return jsonify({"error": "Internal server error", "details": str(e)}), 500
