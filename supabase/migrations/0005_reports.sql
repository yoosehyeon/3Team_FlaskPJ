-- F5 실시간 위험 신고 엔진: reports 테이블 생성 + RLS 정책
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS reports (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    location    geometry(Point, 4326) NOT NULL,
    type        TEXT NOT NULL CHECK (type IN ('stairs','construction','steep_slope','elevator_broken')),
    severity    INTEGER NOT NULL DEFAULT 3 CHECK (severity BETWEEN 1 AND 5),
    image_url   TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_reports_location ON reports USING gist (location);

ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY reports_insert ON reports
    FOR INSERT TO authenticated
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY reports_select ON reports
    FOR SELECT USING (true);

ALTER PUBLICATION supabase_realtime ADD TABLE reports;
-- Storage bucket: reports-images
INSERT INTO storage.buckets (id, name, public)
VALUES ('reports-images', 'reports-images', true)
ON CONFLICT (id) DO NOTHING;

-- 공개 읽기 정책 (누구나 이미지 조회 가능)
CREATE POLICY "reports images public read"
ON storage.objects FOR SELECT
USING (bucket_id = 'reports-images');

-- 인증 사용자만 업로드 가능
CREATE POLICY "reports images auth upload"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (bucket_id = 'reports-images');
