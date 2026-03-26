-- 0005_reports.sql
CREATE TABLE IF NOT EXISTS reports (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID        REFERENCES auth.users(id),
    location    geometry(Point, 4326) NOT NULL,
    type        TEXT        NOT NULL,  -- 'obstacle' | 'elevator_broken' | 'ramp_damaged'
    description TEXT,
    image_path  TEXT,  -- Supabase Storage path
    status      TEXT        DEFAULT 'pending',
    created_at  TIMESTAMPTZ DEFAULT now()
);

-- RLS 필수
ALTER TABLE reports ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'reports_select' AND tablename = 'reports') THEN
        CREATE POLICY reports_select ON reports FOR SELECT USING (true);
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_policies WHERE policyname = 'reports_insert' AND tablename = 'reports') THEN
        CREATE POLICY reports_insert ON reports FOR INSERT TO authenticated WITH CHECK (auth.uid() = user_id);
    END IF;
END $$;
