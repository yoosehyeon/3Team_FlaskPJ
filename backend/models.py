from backend.database import Base

# ==========================================================
# 🚀 백엔드 팀원 (권우영, 이동규, 변호준 님) 협업 규칙
# ==========================================================
# 1. 이곳에 PRD에 명시된 본인의 도메인 SQLAlchemy 모델을 작성하세요.
# 2. `from sqlalchemy import ...` 등을 자유롭게 사용하시면 됩니다.
# 3. 모델 클래스는 반드시 `Base`를 상속받아야 app.py가 인식하여 테이블을 자동 생성합니다.
# 
# [작성 예시]
# class User(Base):
#     __tablename__ = "users"
#     id = Column(Integer, primary_key=True)
#     ...
