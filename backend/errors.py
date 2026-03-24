from flask import jsonify
from werkzeug.exceptions import HTTPException
import structlog
import traceback

# 초기화된 로거를 가져옵니다.
logger = structlog.get_logger()

def register_error_handlers(app):
    """
    플라스크 전역에서 발생하는 예외를 모두 캐치하고, 일정 규격에 맞추어 클라이언트에 JSON 포맷으로 전달합니다.
    (모든 백엔드 팀원이 통일된 에러 규격을 사용하도록 돕는 역할)
    """
    @app.errorhandler(Exception)
    def handle_exception(e):
        # 기본 에러 응답 규격 정의
        response = {
            "error": "Internal Server Error",
            "message": "서버 내부에서 오류가 발생했습니다. (팀원 A가 설계한 Global Handler)"
        }
        status_code = 500

        # HTTP 표준 에러 처리 (400, 401, 403, 404, 등)
        if isinstance(e, HTTPException):
            response["error"] = e.name
            response["message"] = e.description
            status_code = e.code
            logger.warning("http_exception_handled", status_code=status_code, error=e.name, message=e.description)
        else:
            # 예측되지 않은 에러 발생 시, 상세 스택 트레이스와 함께 structlog로 수집
            logger.error("unhandled_exception", 
                         error_type=type(e).__name__,
                         error=str(e), 
                         traceback=traceback.format_exc())

        return jsonify(response), status_code
