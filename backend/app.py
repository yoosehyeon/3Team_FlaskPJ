import os
import structlog
from dotenv import load_dotenv
from flask import Flask, jsonify

# .env 파일 로드
load_dotenv()
from flask_cors import CORS
from extensions import limiter

app = Flask(__name__)
log = structlog.get_logger()

# 배포/로컬 도메인 분기
def create_cors_origins() -> list[str]:
    flask_env = os.getenv("FLASK_ENV", "development")
    vite_domain = os.getenv("VITE_DOMAIN", "").rstrip("/")
    
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000"
    ]
    
    if vite_domain:
        # 슬래시 유무와 상관없이 허용 도메인 추가
        origins.append(vite_domain)
        origins.append(f"{vite_domain}/")
    elif flask_env == "production":
        # 운영 환경인데 도메인이 명시되지 않은 경우 로그 출력 후 임시 허용
        log.warning("VITE_DOMAIN not set in production. Using permissive CORS.")
        return ["*"]
        
    return origins

# Netlify ↔ Cloudtype CORS 세팅 
CORS(app, origins=create_cors_origins(), supports_credentials=True)

# Limiter app 등록
limiter.init_app(app)

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

# 라우트 블루프린트 등록
from routes.health import health_bp
from routes.route import route_bp
from routes.places import places_bp
from routes.reports import reports_bp
from routes.transit import transit_bp
from routes.elevators import elevators_bp

app.register_blueprint(health_bp)
app.register_blueprint(route_bp)
app.register_blueprint(places_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(transit_bp)
app.register_blueprint(elevators_bp)

if __name__ == "__main__":
    app.run(debug=True)