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

    # 2. structlog 로거 구성 (프로덕션 환경과 동일하게 JSON 형식으로 구성하여 디버깅/에러 추적을 용이하게 함)
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,            # 레벨에 따른 필터링 (INFO, DEBUG 등)
            structlog.stdlib.add_logger_name,            # 로그를 발생시킨 모듈 이름 추가
            structlog.stdlib.add_log_level,              # 에러 레벨 명시
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"), # 발생 시점 (ISO 8601)
            structlog.processors.StackInfoRenderer(),    # 스택 트레이스 (추가 시)
            structlog.processors.format_exc_info,        # 예외(Exception)가 있을 경우 함께 포맷팅
            structlog.processors.JSONRenderer()          # Cloudtype/DevOps 로그 통합 분석을 위한 JSON 기록
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()
