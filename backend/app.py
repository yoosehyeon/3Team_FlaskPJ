import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import structlog
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

# Blueprint imports
from routes.route import route_bp
from routes.transit import transit_bp
from routes.elevators import elevators_bp
from routes.places import places_bp
from routes.reports import reports_bp
from routes.health import health_bp
from routes.barrier_places import barrier_bp

load_dotenv()

# Sentry 초기화
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        integrations=[FlaskIntegration()],
        traces_sample_rate=0.1,
    )

log = structlog.get_logger()

def create_app():
    """
    App Factory for Modu-Gil (수원시 휠체어 통합 내비게이션)
    """
    app = Flask(__name__)
    
    # CORS Configuration - PRD v3.0 Rule 2
    def create_cors_origins() -> list[str]:
        flask_env = os.getenv("FLASK_ENV", "development")
        if flask_env == "production":
            vite_domain = os.getenv("VITE_DOMAIN")
            if not vite_domain:
                return ["*"]
            return [vite_domain]
        return ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "http://localhost:5000"]

    CORS(app, origins=create_cors_origins(), supports_credentials=True)

    # Rate Limiting
    limiter = Limiter(
        app,
        key_func=get_remote_address,
        default_limits=["1000 per day", "200 per hour"],
        storage_uri=os.getenv("REDIS_URL", "memory://"),
    )

    # Register Blueprints
    for bp in [route_bp, transit_bp, elevators_bp, places_bp, reports_bp, health_bp, barrier_bp]:
        app.register_blueprint(bp)

    @app.route('/')
    def home():
        return "Modu-Gil Backend Is Running! (Port 5000)"

    # 전역 에러 핸들러
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        log.error("internal_server_error", error=str(e))
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    # Deployment Port (Cloudtype typically 6543, Local 5000)
    port = int(os.getenv("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
