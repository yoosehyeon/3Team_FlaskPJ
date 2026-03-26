-- 0004_elevators.sql
CREATE TABLE IF NOT EXISTS elevators (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT        NOT NULL,
    location    geometry(Point, 4326) NOT NULL,
    status      TEXT        DEFAULT 'normal',  -- 'normal' | 'broken' | 'maintenance'
    building    TEXT,
    floor       TEXT,
    external_id TEXT        UNIQUE,  -- 공공데이터 API 원본 ID
    updated_at  TIMESTAMPTZ DEFAULT now(),
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_elevators_location ON elevators USING GIST(location);

-- RLS 정책 (v3.0: 테이블 생성 직후 적용)
ALTER TABLE elevators ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'elevators_select' AND tablename = 'elevators') THEN
        CREATE POLICY elevators_select ON elevators FOR SELECT USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'elevators_update' AND tablename = 'elevators') THEN
        CREATE POLICY elevators_update ON elevators FOR UPDATE TO service_role USING (true);
    END IF;
END $$;
