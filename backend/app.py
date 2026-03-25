import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import structlog
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Sentry 초기화
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.1,
    )

app = Flask(__name__)
log = structlog.get_logger()

def create_cors_origins() -> list[str]:
    flask_env = os.getenv("FLASK_ENV", "development")
    if flask_env == "production":
        vite_domain = os.getenv("VITE_DOMAIN")
        if not vite_domain:
            raise EnvironmentError(
                "FLASK_ENV=production 이지만 VITE_DOMAIN이 설정되지 않았습니다."
            )
        return [vite_domain]
    return ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]

CORS(app, origins=create_cors_origins(), supports_credentials=True)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=os.getenv("REDIS_URL", "memory://"),
)

# 전역 에러 핸들러
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    log.error("internal_server_error", error=str(e))
    return jsonify({"error": "Internal server error"}), 500

# 라우트 등록 (미리 임포트)
from routes.route import route_bp
from routes.transit import transit_bp
from routes.elevators import elevators_bp
from routes.places import places_bp
from routes.reports import reports_bp
from routes.health import health_bp

for bp in [route_bp, transit_bp, elevators_bp, places_bp, reports_bp, health_bp]:
    app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
