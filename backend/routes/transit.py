import os
import requests
from flask import Blueprint, request, jsonify
from app import limiter

transit_bp = Blueprint("transit", __name__)

@transit_bp.route("/api/transit", methods=["GET"])
@limiter.limit("60 per minute")
def get_transit():
    start_lat = request.args.get("start_lat")
    start_lng = request.args.get("start_lng")
    end_lat = request.args.get("end_lat")
    end_lng = request.args.get("end_lng")

    if not all([start_lat, start_lng, end_lat, end_lng]):
         return jsonify({"error": "Missing required coordinates parameters"}), 400

    odsay_api_key = os.getenv("ODSAY_API_KEY")
    if not odsay_api_key:
        return jsonify({"error": "ODSAY API key is missing"}), 500

    url = "https://api.odsay.com/v1/api/searchPubTransPathT"
    params = {
        "apiKey": odsay_api_key,
        "SX": start_lng,
        "SY": start_lat,
        "EX": end_lng,
        "EY": end_lat,
        "SearchPathType": 0 # 전체(지하철+버스)
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if 'error' in data:
             if 'msg' in data['error']:
                 return jsonify({"error": data['error']['msg']}), 404
             return jsonify({"error": "ODsay API error"}), 400

        paths = data.get('result', {}).get('path', [])
        wheelchair_accessible_paths = []
        
        for path in paths:
            is_accessible = True
            for sub_path in path.get('subPath', []):
                traffic_type = sub_path.get('trafficType')
                if traffic_type == 2: # 버스
                    pass # 저상버스 식별 로직 (추가 API 확장 가능)
                    
            if is_accessible:
                wheelchair_accessible_paths.append(path)

        return jsonify({
            "message": "Transit route processed",
            "paths": wheelchair_accessible_paths if wheelchair_accessible_paths else paths
        })

    except requests.exceptions.RequestException as e:
         return jsonify({"error": "ODsay API Request Failed", "details": str(e)}), 502
