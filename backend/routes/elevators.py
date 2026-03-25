import os
import requests
from flask import Blueprint, jsonify
from app import limiter

elevators_bp = Blueprint("elevators", __name__)

@elevators_bp.route("/api/elevators", methods=["GET"])
@limiter.limit("60 per minute")
def get_elevators():
    api_key = os.getenv("PUBLIC_DATA_API_KEY")
    if not api_key:
        return jsonify({"error": "PUBLIC_DATA API key is missing"}), 500

    # 예시: 공공데이터 수원시 엘리베이터 API
    # url = "https://api.odcloud.kr/api/..." 
    # 실제 수원시 API 명세에 맞춰 호출 (임시 응답 작성)
    
    # DB (elevators 테이블)에서 캐시된 데이터를 조회하거나 상태를 반환하는 로직 포함 가능
    
    return jsonify({
        "status": "success",
        "data": [] # 프록시 또는 DB에서 가져온 엘리베이터 데이터
    })
