import os
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

db_url = os.getenv("DATABASE_URL")
if not db_url:
    # 빈 값으로 create_engine을 시도하며 발생하는 런타임 Crash 방어
    raise EnvironmentError("[오류] DATABASE_URL 환경변수가 누락되었습니다. Cloudtype Secrets에 Supabase URL(포트 6543)을 등록해야 합니다.")

engine = create_engine(
    db_url,
    poolclass=NullPool,
    pool_pre_ping=True,
)
