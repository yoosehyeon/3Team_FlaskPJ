import multiprocessing

# gunicorn.conf.py (Gunicorn 설정 파일)
# 역할: Cloudtype 서버 배포 시 사용하는 WSGI HTTP 서버 세팅

bind = "0.0.0.0:5000"

# 워커 클래스: SSE (Server-Sent Events) 등 비동기 스트리밍이 필수적이므로 gthread 또는 gevent 활용.
# F5 (실시간 위험 신고)의 broadcast가 블로킹되지 않도록 구성합니다.
worker_class = "gthread"

# 워커 및 쓰레드 최적화 (CPU 코어 수에 맞추기)
workers = multiprocessing.cpu_count() * 2 + 1
threads = 4

# 타임아웃
# Turf.js나 PostGIS의 공간 쿼리 등 무거운 연산이 있을 경우를 위해 약간 넉넉하게 세팅하되 (기본은 30초)
timeout = 30
keepalive = 2

# 로깅 (팀원 A가 세팅한 structlog로 출력되도록 구성)
loglevel = "info"
accesslog = "-"  # 표준 출력(stdout)으로 연동
errorlog = "-"   # 표준 에러(stderr)로 연동

# Reverse Proxy (Cloudtype LB) 뒷단에 위치할 경우 허용 IP 설정
forwarded_allow_ips = "*"
