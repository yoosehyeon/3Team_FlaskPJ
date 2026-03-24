# 모두의 길 (Modu-Gil) 휠체어 통합 내비게이션

본 저장소는 **모두의 길(Modu-Gil)** 프로젝트를 위한 통합 레포지토리입니다. (React 18 + Flask 3.0)

## 📌 1. 필수 개발 환경 세팅 (Day 1)

### 🚀 A. Supabase Local CLI 세팅 (로컬 DB 인프라)
모든 팀원은 로컬 DB 레이어 통일을 위해 별도의 외부 DB가 아닌 Supabase Local을 사용합니다.
1. 팀원 PC의 Node.js 설치 확인 (`node -v`) 및 Docker Desktop 실행
2. 터미널에서 `npm install -g supabase` 실행
3. 프로젝트 최상위 폴더에서 `supabase init` 실행
4. `supabase start` 실행 (로컬 컨테이너 실행됨)
5. 완료 후 터미널에 출력되는 **DATABASE_URL**, **API URL**, **anon key**를 복사합니다.

### 🚀 B. 백엔드(Flask) 환경 구성
1. 파이썬 가상환경 생성 및 활성화
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```
2. 패키지 설치
```bash
pip install -r backend/requirements.txt
```
3. 환경변수 설정
- `backend/.env.example` 파일을 복사하여 `backend/.env`를 만듭니다. (절대 커밋 금지)
- `supabase start` 결과값을 `.env` 안에 맞춰 넣습니다. (`postgresql://postgres:postgres@127.0.0.1:54322/postgres`)
4. 앱 실행
```bash
python backend/app.py
```
> 포트 5000번에서 실행되며 DB 테이블이 최초 1회 자동 생성됩니다.

### 🚀 C. 프론트엔드(React) 환경 구성
1. 패키지 모듈 설치
```bash
cd frontend
npm install
```
2. 개발 서버 실행
```bash
npm run dev
```
> 팀원 A(PM 유세현)의 프록시 설정에 의해 프론트에서 `/api/...`로 보내는 데이터는 자동으로 백엔드(5000번)로 연동됩니다.

---

### 📞 6인 협업 컨벤션 및 담당
- 유세현(PM): 인프라 아키텍처 & 공통 모듈 (DevOps)
- 이승연: 공간 데이터 알고리즘 (Map Engine)
- 권우영: 실시간 상태 추적기 (Elevator)
- 이동규: 대중교통 데이터 엔지니어 (Public Transport)
- 변호준: 배리어프리 컨텐츠 매니저 (Barrier-free Content)
- 김성익(PL): 실시간 인터랙션 엔진 (Real-time Web)

*충돌 방지를 위해 반드시 매일 `feature/역할-기능` 브랜치를 따서 작업하시기 바랍니다.*
