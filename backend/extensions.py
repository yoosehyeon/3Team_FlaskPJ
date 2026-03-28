import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    # 지도 이동/드래그 시 Radius Search 등이 빈번하게 발생하므로 기본 한도를 상향합니다.
    default_limits=["2000 per day", "200 per minute"],
    storage_uri=os.getenv("REDIS_URL", "memory://"),
)
