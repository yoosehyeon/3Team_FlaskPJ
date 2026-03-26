import os
import structlog
from dotenv import load_dotenv
from flask import Flask, jsonify

# .env 파일 로드
load_dotenv()
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
log = structlog.get_logger()

# 배포/로컬 도메인 분기
def create_cors_origins() -> list[str]:
    flask_env = os.getenv("FLASK_ENV", "development")
    
    if flask_env == "production":
        vite_domain = os.getenv("VITE_DOMAIN")
        if not vite_domain:
            raise EnvironmentError(
                "FLASK_ENV=production 이지만 VITE_DOMAIN이 설정되지 않았습니다. "
                "Cloudtype Secrets에 VITE_DOMAIN을 등록하세요."
            )
        return [vite_domain]
    
    return [
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://127.0.0.1:5173"
    ]

# Netlify ↔ Cloudtype CORS 세팅 
CORS(app, origins=create_cors_origins(), supports_credentials=True)

# 무차별 접속 방어 (Redis 제외, 메모리 단독 모드)
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

# ----------------------------
# 전역 에러 핸들러
# ----------------------------
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    log.error("internal_server_error", error=str(e))
    return jsonify({"error": "Internal server error"}), 500

# 헬스체크 진입 라우트 블루프린트 등록
from routes.health import health_bp
# from routes.route import route_bp 등은 향후 추가로 여기에 작성

app.register_blueprint(health_bp)

if __name__ == "__main__":
    app.run()
