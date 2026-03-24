import structlog
import logging
import sys


def configure_logging():
    # 1. 표준 logging 포맷 초기화 (stdout으로 출력)
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    # 2. structlog 로거 구성 (JSON 형식으로 구성하여 디버깅 용이하게 함)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,            # 레벨 필터링
            structlog.stdlib.add_logger_name,            # 모듈 이름 추가
            structlog.stdlib.add_log_level,              # 에러 레벨 명시
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),  # 발생 시점 (ISO 8601)
            structlog.processors.StackInfoRenderer(),    # 스택 트레이스
            structlog.processors.format_exc_info,        # 예외 정보 포맷팅
            structlog.processors.JSONRenderer()          # JSON 기록
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    return structlog.get_logger()
