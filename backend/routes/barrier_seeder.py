import os
from dotenv import load_dotenv
from sqlalchemy import text
from db import engine

load_dotenv()

indoor_data = """KCDCIO23N000000639,수원시립장애인주간보호시설,무장애장소,무장애장소_실내,경기도 수원시 권선구 호매실로 211,37.2641476,126.9458957
KCDCIO23N000000641,수원시장애인종합복지관,무장애장소,무장애장소_실내,경기도 수원시 영통구 창룡대로 256,37.288924,127.0435161
KCDCIO23N000002016,수원시 장안구민회관,문화시설,공연장,경기도 수원시 장안구 수성로 382,37.29953941,127.0094709
KCDCIO23N000002131,수원제2야외음악당,문화시설,공연장,경기도 수원시 장안구 수성로 382,37.29953941,127.0094709
KCDCIO23N000002342,서수원주민편익시설,문화시설,문화지원시설,경기도 수원시 권선구 수인로 126,37.27961019,126.9749506
KCDCIO23N000002364,수원시청소년문화공원,문화시설,문화지원시설,경기도 수원시 팔달구 권광로 293,37.26578007,127.0401825
KCDCIO23N000002826,수원박물관,문화시설,박물관/미술관,경기도 수원시 영통구 창룡대로 265,37.29170363,127.0427011
KCDCIO23N000002832,수원광교박물관,문화시설,박물관/미술관,경기도 수원시 영통구 광교로 182,37.29792037,127.0505191
KCDCIO23N000002951,수원시 가족여성회관,문화시설,지역문화복지시설,경기도 수원시 팔달구 매산로 119,37.2687593,127.0051185"""

outdoor_data = """KCDCOPO23N000001859,수원화성,관광지,역사관광지,경기도 수원시 팔달구 정조로 825,37.282578,127.012423
KCDCOPO23N000001860,화성행궁,관광지,역사관광지,경기도 수원시 팔달구 정조로 825,37.282578,127.012423
KCDCOPO23N000001861,수원궁도장(연무대),관광지,역사관광지,경기도 수원시 팔달구 창룡대로 103,37.287232,127.023292
KCDCOPO23N000002014,수원월드컵경기장,관광지,휴양관광지,경기도 수원시 팔달구 월드컵로 310,37.286241,127.036666
KCDCOPO23N000002015,서수원체육공원,관광지,휴양관광지,경기도 수원시 권선구 수인로 126,37.279607,126.974945
KCDCOPO23N000002167,광교호수공원,관광지,자연관광지,경기도 수원시 영통구 광교호수공원로 102,37.279584,127.062024
KCDCOPO23N000002425,효원공원 월화원,관광지,건축/조형물,경기도 수원시 팔달구 효원로307번길 26,37.264627,127.037134"""

def seed_data():
    try:
        with engine.begin() as conn:
            # 실내시설 저장
            for row in indoor_data.split('\n'):
                parts = row.split(',')
                if len(parts) >= 7:
                    esntl, name, lclas, mlsfc, addr, lat, lng = parts
                    meta_json = f'{{"esntl_id": "{esntl}", "type": "indoor", "mlsfc": "{mlsfc}"}}'
                    conn.execute(
                        text("""
                        INSERT INTO places (name, category, address, location, meta)
                        VALUES (:name, :cat, :addr, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), CAST(:meta AS jsonb))
                        """),
                        {"name": name, "cat": lclas, "addr": addr, "lng": float(lng), "lat": float(lat), "meta": meta_json}
                    )
            
            # 실외시설 저장
            for row in outdoor_data.split('\n'):
                parts = row.split(',')
                if len(parts) >= 7:
                    esntl, name, lclas, mlsfc, addr, lat, lng = parts
                    meta_json = f'{{"esntl_id": "{esntl}", "type": "outdoor", "mlsfc": "{mlsfc}"}}'
                    conn.execute(
                        text("""
                        INSERT INTO places (name, category, address, location, meta)
                        VALUES (:name, :cat, :addr, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), CAST(:meta AS jsonb))
                        """),
                        {"name": name, "cat": lclas, "addr": addr, "lng": float(lng), "lat": float(lat), "meta": meta_json}
                    )
            
            print("Successfully inserted indoor and outdoor facilities data!")

    except Exception as e:
        print(f"Error seeding data: {e}")

if __name__ == "__main__":
    seed_data()
