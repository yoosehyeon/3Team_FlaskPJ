import os
import sys
from flask import Flask
from dotenv import load_dotenv
from flask_apscheduler import APScheduler

# [팀원 A: 유세현 PM 보완] 실행 환경에 관계없이 패키지를 인식하도록 경로 주입
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.logger import configure_logging            # noqa: E402
from backend.errors import register_error_handlers       # noqa: E402
from backend.database import engine, Base               # noqa: E402

# .env 환경 변수 로드
load_dotenv()

# 팀원 A의 인프라 세팅: 전역 structlog 초기화
logger = configure_logging()


def create_app():
    # Flask 앱 생성
    app = Flask(__name__)

    # 1. [팀원 A 보완] F3 실시간 시설 상태 추적 알림을 위한 스케줄러 초기화
    # 이 설정이 활성화되어 있어야 팀원 C(권우영) 님이 API 폴링 기능을 즉시 작업할 수 있습니다.
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()
    logger.info("scheduler_init", message="F3 추적용 스케줄러가 엔진에 장착되었습니다.")

    # 2. 전역 에러 핸들러 플러그인 연동 (팀원 모두에게 일관된 에러 포맷 제공)
    register_error_handlers(app)

    logger.info("app_start", message="모두의 길(Modu-Gil) 어플리케이션을 시작합니다.")

    # 3. 로컬 실행을 위해 DB 테이블 초기화
    try:
        from backend import database, models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("db_init", message="DB 릴레이션(Table) 생성을 완료 하였습니다.")
    except Exception as e:
        logger.error("db_init_err", error=str(e), msg="DB 연결에 실패하였습니다.")

    # 4. Health Check 라우트 (클라우드타입 배포 및 CI 파이프라인 무중단 상태 점검용)
    @app.route('/health', methods=['GET'])
    def health_check():
        logger.info("health_check_called", status="healthy")
        return {"status": "healthy", "message": "API Server is running ok."}, 200

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
