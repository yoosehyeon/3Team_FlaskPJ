-- 0003_places.sql
CREATE TABLE places (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT        NOT NULL,
    category    TEXT,
    address     TEXT,
    location    geometry(Point, 4326) NOT NULL,  -- PostGIS
    image_url   TEXT,
    meta        JSONB,
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- 인덱스 (300m 반경 검색 최적화)
CREATE INDEX idx_places_location ON places USING GIST(location);

-- RLS 정책 (v3.0: 테이블 생성 직후 적용)
ALTER TABLE places ENABLE ROW LEVEL SECURITY;

CREATE POLICY places_select ON places
    FOR SELECT USING (true);  -- 모든 사용자 읽기 허용

CREATE POLICY places_insert ON places
    FOR INSERT TO authenticated
    WITH CHECK (true);  -- 인증 사용자만 삽입 가능
