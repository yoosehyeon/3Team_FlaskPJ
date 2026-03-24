import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

# Cloudtype에 배포하거나 Supabase Local을 사용 중인 서로 다른 팀원 환경을 위해 환경변수 세팅
# 기본값은 팀원들의 local 세팅용
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54322/postgres")

# [핵심] 이기종 DB 환경에서의 호환성 해결
# Supabase Local 환경과 Cloudtype 프로덕션 환경에서 발생할 수 있는 Timeout/Dead 연결 등을 방지하기 위한 SQLAlchemy 2.0 포맷 설정
engine = create_engine(
    DATABASE_URL,
    echo=False,           # 프로덕션에서는 False로 두어 불필요한 IO 제거
    pool_size=10,         # 연결 풀 유지 개수: 10
    max_overflow=20,      # 풀이 가득 찼을 때 허용되는 추가 연결: 20
    pool_timeout=30,      # 연결을 가져오기 위한 최대 대기 시간: 30초 (PostGIS 쿼리가 무거울 수 있음)
    pool_recycle=1800,    # 연결 재사용 방지를 위해 30분 마다 연결 갱신 (Cloud DB Idle timeout 방지용)
    pool_pre_ping=True    # 유효하지 않은 'Dead Connection(소켓이 끊어진)'을 선제적으로 끊기
)

# 세션 생성기. autocommit과 autoflush를 끄고, 트랜잭션 관리를 직접 하도록 설정. 멀티스레드 대비용 scoped_session 사용.
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

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
