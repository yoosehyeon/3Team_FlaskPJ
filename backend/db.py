from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
import os

database_url = os.getenv("DATABASE_URL")
if not database_url:
    # 기본값 설정 또는 에러 발생
    database_url = "postgresql://postgres:password@localhost:5432/postgres"

engine = create_engine(
    database_url,
    poolclass=NullPool,          # PgBouncer Transaction mode 필수
    pool_pre_ping=True,          # 연결 유효성 사전 확인
)
