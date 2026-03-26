-- 수원 엘리베이터 정보를 저장하기 위한 테이블 스키마
CREATE TABLE IF NOT EXISTS public.elevators (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    station_name TEXT NOT NULL,
    line_name TEXT,
    location TEXT,
    start_floor TEXT,
    end_floor TEXT,
    status TEXT DEFAULT '정상',
    operator TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- RLS (Row Level Security) 설정 - 인증된 사용자만 삽입 가능하게 하거나, 익명(anon) 삽입 허용 시 아래 주석 해제
-- ALTER TABLE public.elevators ENABLE ROW LEVEL SECURITY;
-- CREATE POLICY "Allow all public insertion" ON public.elevators FOR INSERT WITH CHECK (true);
-- CREATE POLICY "Allow public read" ON public.elevators FOR SELECT USING (true);
