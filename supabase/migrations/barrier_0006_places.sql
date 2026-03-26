-- Create barrier_places table for accessibility data in Suwon
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS barrier_places (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    esntl_id TEXT UNIQUE,
    fclty_nm TEXT NOT NULL,
    lclas_nm TEXT,
    mlsfc_nm TEXT,
    fclty_road_nm_addr TEXT,
    fclty_la DOUBLE PRECISION,
    fclty_lo DOUBLE PRECISION,
    geom GEOMETRY(Point, 4326),
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_barrier_places_geom ON barrier_places USING GIST (geom);

-- Seed data for Suwon facilities
INSERT INTO barrier_places (esntl_id, fclty_nm, lclas_nm, mlsfc_nm, fclty_road_nm_addr, fclty_la, fclty_lo, geom)
VALUES 
('KCDCIO23N000000639', '수원시립장애인주간보호시설', '무장애장소', '무장애장소_실내', '경기도 수원시 권선구 호매실로 211', 37.2641476, 126.9458957, ST_SetSRID(ST_MakePoint(126.9458957, 37.2641476), 4326)),
('KCDCIO23N000000641', '수원시장애인종합복지관', '무장애장소', '무장애장소_실내', '경기도 수원시 영통구 창룡대로 256', 37.288924, 127.0435161, ST_SetSRID(ST_MakePoint(127.0435161, 37.288924), 4326)),
('KCDCIO23N000002016', '수원시 장안구민회관', '문화시설', '공연장', '경기도 수원시 장안구 수성로 382', 37.29953941, 127.0094709, ST_SetSRID(ST_MakePoint(127.0094709, 37.29953941), 4326)),
('KCDCIO23N000002131', '수원제2야외음악당', '문화시설', '공연장', '경기도 수원시장안구 수성로 382', 37.29953941, 127.0094709, ST_SetSRID(ST_MakePoint(127.0094709, 37.29953941), 4326)),
('KCDCIO23N000002342', '서수원주민편익시설', '문화시설', '문화지원시설', '경기도 수원시 권선구 수인로 126', 37.27961019, 126.9749506, ST_SetSRID(ST_MakePoint(126.9749506, 37.27961019), 4326)),
('KCDCIO23N000002364', '수원시청소년문화공원', '문화시설', '문화지원시설', '경기도 수원시 팔달구 권광로 293', 37.26578007, 127.0401825, ST_SetSRID(ST_MakePoint(127.0401825, 37.26578007), 4326)),
('KCDCIO23N000002826', '수원박물관', '문화시설', '박물관/미술관', '경기도 수원시 영통구 창룡대로 265', 37.29170363, 127.0427011, ST_SetSRID(ST_MakePoint(127.0427011, 37.29170363), 4326)),
('KCDCIO23N000002832', '수원광교박물관', '문화시설', '박물관/미술관', '경기도 수원시 영통구 광교로 182', 37.29792037, 127.0505191, ST_SetSRID(ST_MakePoint(127.0505191, 37.29792037), 4326)),
('KCDCIO23N000002951', '수원시 가족여성회관', '문화시설', '지역문화복지시설', '경기도 수원시 팔달구 매산로 119', 37.2687593, 127.0051185, ST_SetSRID(ST_MakePoint(127.0051185, 37.2687593), 4326)),
('KCDCOPO23N000001859', '수원화성', '관광지', '역사관광지', '경기도 수원시 팔달구 정조로 825', 37.282578, 127.012423, ST_SetSRID(ST_MakePoint(127.012423, 37.282578), 4326)),
('KCDCOPO23N000001860', '화성행궁', '관광지', '역사관광지', '경기도 수원시 팔달구 정조로 825', 37.282578, 127.012423, ST_SetSRID(ST_MakePoint(127.012423, 37.282578), 4326)),
('KCDCOPO23N000001861', '수원궁도장(연무대)', '관광지', '역사관광지', '경기도 수원시 팔달구 창룡대로 103', 37.287232, 127.023292, ST_SetSRID(ST_MakePoint(127.023292, 37.287232), 4326)),
('KCDCOPO23N000002014', '수원월드컵경기장', '관광지', '휴양관광지', '경기도 수원시 팔달구 월드컵로 310', 37.286241, 127.036666, ST_SetSRID(ST_MakePoint(127.036666, 37.286241), 4326)),
('KCDCOPO23N000002015', '서수원체육공원', '관광지', '휴양관광지', '경기도 수원시 권선구 수인로 126', 37.279607, 126.974945, ST_SetSRID(ST_MakePoint(126.974945, 37.279607), 4326)),
('KCDCOPO23N000002167', '광교호수공원', '관광지', '자연관광지', '경기도 수원시 영통구 광교호수공원로 102', 37.279584, 127.062024, ST_SetSRID(ST_MakePoint(127.062024, 37.279584), 4326)),
('KCDCOPO23N000002425', '효원공원 월화원', '관광지', '건축/조형물', '경기도 수원시 팔달구 효원로307번길 26', 37.264627, 127.037134, ST_SetSRID(ST_MakePoint(127.037134, 37.264627), 4326))
ON CONFLICT (esntl_id) DO NOTHING;
