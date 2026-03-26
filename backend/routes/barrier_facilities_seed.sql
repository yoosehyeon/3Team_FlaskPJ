-- 실내시설 PostGIS 저장 쿼리
INSERT INTO places (name, category, address, location, meta)
VALUES
('수원시립장애인주간보호시설', '무장애장소', '경기도 수원시 권선구 호매실로 211', ST_SetSRID(ST_MakePoint(126.9458957, 37.2641476), 4326), '{"esntl_id": "KCDCIO23N000000639", "type": "indoor", "mlsfc": "무장애장소_실내"}'),
('수원시장애인종합복지관', '무장애장소', '경기도 수원시 영통구 창룡대로 256', ST_SetSRID(ST_MakePoint(127.0435161, 37.288924), 4326), '{"esntl_id": "KCDCIO23N000000641", "type": "indoor", "mlsfc": "무장애장소_실내"}'),
('수원시 장안구민회관', '문화시설', '경기도 수원시 장안구 수성로 382', ST_SetSRID(ST_MakePoint(127.0094709, 37.29953941), 4326), '{"esntl_id": "KCDCIO23N000002016", "type": "indoor", "mlsfc": "공연장"}'),
('수원제2야외음악당', '문화시설', '경기도 수원시 장안구 수성로 382', ST_SetSRID(ST_MakePoint(127.0094709, 37.29953941), 4326), '{"esntl_id": "KCDCIO23N000002131", "type": "indoor", "mlsfc": "공연장"}'),
('서수원주민편익시설', '문화시설', '경기도 수원시 권선구 수인로 126', ST_SetSRID(ST_MakePoint(126.9749506, 37.27961019), 4326), '{"esntl_id": "KCDCIO23N000002342", "type": "indoor", "mlsfc": "문화지원시설"}'),
('수원시청소년문화공원', '문화시설', '경기도 수원시 팔달구 권광로 293', ST_SetSRID(ST_MakePoint(127.0401825, 37.26578007), 4326), '{"esntl_id": "KCDCIO23N000002364", "type": "indoor", "mlsfc": "문화지원시설"}'),
('수원박물관', '문화시설', '경기도 수원시 영통구 창룡대로 265', ST_SetSRID(ST_MakePoint(127.0427011, 37.29170363), 4326), '{"esntl_id": "KCDCIO23N000002826", "type": "indoor", "mlsfc": "박물관/미술관"}'),
('수원광교박물관', '문화시설', '경기도 수원시 영통구 광교로 182', ST_SetSRID(ST_MakePoint(127.0505191, 37.29792037), 4326), '{"esntl_id": "KCDCIO23N000002832", "type": "indoor", "mlsfc": "박물관/미술관"}'),
('수원시 가족여성회관', '문화시설', '경기도 수원시 팔달구 매산로 119', ST_SetSRID(ST_MakePoint(127.0051185, 37.2687593), 4326), '{"esntl_id": "KCDCIO23N000002951", "type": "indoor", "mlsfc": "지역문화복지시설"}');

-- 실외시설 PostGIS 저장 쿼리
INSERT INTO places (name, category, address, location, meta)
VALUES
('수원화성', '관광지', '경기도 수원시 팔달구 정조로 825', ST_SetSRID(ST_MakePoint(127.012423, 37.282578), 4326), '{"esntl_id": "KCDCOPO23N000001859", "type": "outdoor", "mlsfc": "역사관광지"}'),
('화성행궁', '관광지', '경기도 수원시 팔달구 정조로 825', ST_SetSRID(ST_MakePoint(127.012423, 37.282578), 4326), '{"esntl_id": "KCDCOPO23N000001860", "type": "outdoor", "mlsfc": "역사관광지"}'),
('수원궁도장(연무대)', '관광지', '경기도 수원시 팔달구 창룡대로 103', ST_SetSRID(ST_MakePoint(127.023292, 37.287232), 4326), '{"esntl_id": "KCDCOPO23N000001861", "type": "outdoor", "mlsfc": "역사관광지"}'),
('수원월드컵경기장', '관광지', '경기도 수원시 팔달구 월드컵로 310', ST_SetSRID(ST_MakePoint(127.036666, 37.286241), 4326), '{"esntl_id": "KCDCOPO23N000002014", "type": "outdoor", "mlsfc": "휴양관광지"}'),
('서수원체육공원', '관광지', '경기도 수원시 권선구 수인로 126', ST_SetSRID(ST_MakePoint(126.974945, 37.279607), 4326), '{"esntl_id": "KCDCOPO23N000002015", "type": "outdoor", "mlsfc": "휴양관광지"}'),
('광교호수공원', '관광지', '경기도 수원시 영통구 광교호수공원로 102', ST_SetSRID(ST_MakePoint(127.062024, 37.279584), 4326), '{"esntl_id": "KCDCOPO23N000002167", "type": "outdoor", "mlsfc": "자연관광지"}'),
('효원공원 월화원', '관광지', '경기도 수원시 팔달구 효원로307번길 26', ST_SetSRID(ST_MakePoint(127.037134, 37.264627), 4326), '{"esntl_id": "KCDCOPO23N000002425", "type": "outdoor", "mlsfc": "건축/조형물"}');
