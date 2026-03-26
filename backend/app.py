from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from backend.routes.reports import reports_bp

app = Flask(__name__)
CORS(app)

# Rate Limiting (PRD 9.2 - 외부 API 쿼터 보호)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# F5 실시간 위험 신고 엔진 (PRD v3.0 / 김성익 PL)
app.register_blueprint(reports_bp)


@app.route("/")
def home():
    return "백엔드 서버가 정상 동작 중입니다. (포트: 5000)"

# 승연님이 route.py에 카카오맵 Directions API 실제 로직을 작성하고 Blueprint로 등록 하시면 아래 임시함수는 제거
@app.route("/api/route", methods=["POST"])
@limiter.limit("30 per minute")
def get_route():
    data = request.get_json()
    print(f"경로 검색 요청: {data}")

    mock_path = [
        [37.2664, 127.0002],
        [37.2675, 127.0015],
        [37.2685, 127.0025]
    ]

    return jsonify({"status": "success", "path": mock_path})


if __name__ == "__main__":
    app.run(debug=True, port=5000)