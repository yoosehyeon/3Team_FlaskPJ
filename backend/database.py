import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from sqlalchemy.pool import NullPool

# 환경변수에서 DB 연결 URL 로드
# Supabase 프로덕션은 포트 6543 (PgBouncer Transaction Mode)
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres"
)

# [F5 핵심 설정] NullPool 적용 — PRD v3.0 필수
# Supabase는 내부적으로 PgBouncer(Transaction Mode)를 사용하기 때문에
# SQLAlchemy 기본 커넥션 풀과 충돌이 발생한다.
# NullPool은 매 요청마다 새 연결을 열고 즉시 반환하므로 충돌을 방지한다.
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,       # PgBouncer Transaction Mode 필수 설정
    pool_pre_ping=True,       # 유효하지 않은 Dead Connection 선제 차단
    echo=False,               # 프로덕션에서는 False (불필요한 SQL 로그 제거)
)

# 세션 생성기
# scoped_session: 멀티스레드 환경에서 스레드별로 독립된 세션 보장
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

# ORM Base 클래스 — 모든 모델은 이 클래스를 상속받아야 한다
Base = declarative_base()


def get_db():
    """
    Flask 요청 컨텍스트용 DB 세션 제공 함수.
    with 문 없이도 세션을 안전하게 열고 닫을 수 있다.
    NullPool 적용으로 각 요청마다 새 연결을 사용하고 즉시 반환한다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
