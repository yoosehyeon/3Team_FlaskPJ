import os
from flask import Flask
import os
import sys

# 실행 환경(Gunicorn vs Python app.py 직접 실행)에 관계없이 폴더 구조를 패키지로 인식하도록 상위 디렉터리 경로 주입
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.logger import configure_logging
from backend.errors import register_error_handlers
from backend.database import engine, Base
from dotenv import load_dotenv

# .env 환경 변수 로드
load_dotenv()

# 팀원 A의 인프라 세팅: structlog 구동
logger = configure_logging()

def create_app():
    # Flask 앱 생성
    app = Flask(__name__)
    
    # 1. 전역 에러 핸들러 플러그인 연동 (팀원 모두에게 일관된 에러 포맷 제공)
    register_error_handlers(app)
    
    logger.info("app_start", message="모두의 길(Modu-Gil) 어플리케이션을 시작합니다.")

    # 2. 로컬 실행을 위해 DB 테이블 초기화
    try:
        from backend import database
        from backend import models # ✨ 백엔드 팀원들이 정의한 모델을 자동으로 불러와 DB 엔진과 연동시킵니다.
        Base.metadata.create_all(bind=engine)
        logger.info("db_init", message="데이터베이스 엔진과 연결되어 릴레이션을 생성완료 하였습니다.")
    except Exception as e:
        logger.error("db_init_error", error=str(e), message="데이터베이스 연결에 실패하였습니다.")

    # 3. Health Check 라우트 (클라우드타입 배포 및 CI 파이프라인 무중단 상태 점검용)
    @app.route('/health', methods=['GET'])
    def health_check():
        logger.info("health_check_called", status="healthy")
        return {"status": "healthy", "message": "API Server is running ok."}, 200

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
