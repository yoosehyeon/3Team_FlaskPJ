-- 배포 및 로컬 환경 관계없이, 공간 쿼리(위치 거리 계산) 익스텐션 자동 활성화
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
