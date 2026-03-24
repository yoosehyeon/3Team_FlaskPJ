import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

# Cloudtype 또는 Supabase Local 환경변수 세팅
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres"
)

# [핵심] 이기종 DB 환경에서의 호환성 해결
# SQLAlchemy 2.0 포맷 설정 (Timeout/Dead 연결 방지용)
engine = create_engine(
    DATABASE_URL,
    echo=False,           # 프로덕션에서는 False로 두어 불필요한 IO 제거
    pool_size=10,         # 연결 풀 유지 개수: 10
    max_overflow=20,      # 풀이 가득 찼을 때 허용되는 추가 연결: 20
    pool_timeout=30,      # 최대 대기 시간: 30초 (PostGIS 쿼리 대비)
    pool_recycle=1800,    # 30분 마다 연결 갱신 (Idle timeout 방지)
    pool_pre_ping=True    # 유효하지 않은 'Dead Connection' 선제 차단
)

# 세션 생성기. 트랜잭션 직접 관리 및 멀티스레드 대비 scoped_session 사용.
SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine)
)

Base = declarative_base()


def get_db():
    """
    모든 팀원이 이 제너레이터를 사용하여 안전하게 DB 세션을 열고/닫을 수 있습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()