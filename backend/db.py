<<<<<<< Updated upstream
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
=======
import os
from sqlalchemy import create_all_engines, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv

load_dotenv()

# PRD Rule: Use poolclass=NullPool and pool_pre_ping=True
# Default port 6543 for PgBouncer (Cloudtype/Supabase)
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:54321/postgres")

engine = create_engine(
    DB_URL,
    poolclass=NullPool,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
>>>>>>> Stashed changes
