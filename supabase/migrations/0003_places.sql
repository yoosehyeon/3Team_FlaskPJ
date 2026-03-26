-- 0003_places.sql
CREATE TABLE IF NOT EXISTS places (
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
CREATE INDEX IF NOT EXISTS idx_places_location ON places USING GIST(location);

-- RLS 정책 (v3.0: 테이블 생성 직후 적용)
ALTER TABLE places ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'places_select' AND tablename = 'places') THEN
        CREATE POLICY places_select ON places FOR SELECT USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'places_insert' AND tablename = 'places') THEN
        CREATE POLICY places_insert ON places FOR INSERT TO authenticated WITH CHECK (true);
    END IF;
END $$;
