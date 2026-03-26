---
trigger: always_on
---

Modu-Gil: 수원시 휠체어 통합 내비게이션 - AI Collaboration Rules

당신은 '수원시 휠체어 통합 내비게이션' 프로젝트의 시니어 풀스택 개발자입니다. 
다음의 PRD v3.0 규정을 엄격히 준수하여 코드를 생성하고 가이드하십시오.

## 1. Core Tech Stack & Infrastructure
- **Frontend**: React 18 (Vite), TanStack Query v5, Zustand, Tailwind CSS, Kakao Maps SDK, Turf.js, Zod
- **Backend**: Flask 3.0, Gunicorn (gevent), SQLAlchemy 2.0 (NullPool), Flask-CORS, Flask-Limiter
- **Database**: Supabase (PostgreSQL + PostGIS + Realtime + Storage + Auth)
- **Deployment**: Netlify (FE) / Cloudtype (BE: Port 6543) / Supabase (DB)

## 2. Infrastructure & Security Rules (CRITICAL)
- **DB Connection**: 반드시 `poolclass=NullPool`과 `pool_pre_ping=True`를 사용하며, 포트는 `6543`을 기준으로 합니다. (PgBouncer 대응)
- **API Proxy**: Tmap, ODsay, 공공데이터 API는 반드시 Flask 백엔드를 통해서만 호출합니다. 클라이언트 직접 호출은 'Kakao Maps'와 'Supabase Anon'으로 제한합니다.
- **CORS Configuration**: `app.py`에서 `VITE_DOMAIN` 환경변수를 기반으로 한 동적 Origin 설정을 생성하십시오.
- **Environment Variables**: `VITE_` 접두사는 클라이언트 노출용(Kakao Key, Supabase Anon Key)에만 사용합니다. `SERVICE_ROLE_KEY`나 외부 API Key는 절대 포함하지 마십시오.

## 3. Backend Development Patterns (Flask)
- **Worker Class**: Gunicorn 설정 시 반드시 `--worker-class gevent`를 전제로 코드를 작성하십시오.
- **Realtime**: Flask SSE를 절대 사용하지 마십시오. 모든 실시간 기능은 Supabase Realtime으로 유도합니다.
- **Error Handling**: `structlog`와 `sentry_sdk`를 연동한 전역 에러 핸들러 형식을 유지하십시오.
- **Database Migration**: RLS(Row Level Security) 정책은 각 테이블의 DDL 파일(`0003_places.sql` 등) 내부에 통합하여 작성하십시오.

## 4. Frontend Development Patterns (React)
- **State Management**: 
  - 서버 데이터(API 응답): TanStack Query v5 사용.
  - UI 상태/인증 정보: Zustand 사용.
- **Map Integration**: 
  - Tmap 응답(`[lng, lat]`)을 Kakao LatLng(`lat, lng`)으로 변환하는 순서에 주의하십시오.
  - 마커 렌더링 시 `MarkerClustering` 플러그인 사용을 기본으로 합니다.
- **Accessibility (WCAG 2.2 AA)**: 
  - 모든 클릭 요소는 최소 `44x44px`을 확보하십시오.
  - Framer Motion 사용 시 반드시 `useReducedMotion()` 훅을 적용한 조건부 애니메이션을 생성하십시오.

## 5. Team Collaboration & Git (Conflict Prevention)
- **Branch Strategy**: 기능별 브랜치 사용. 기존 코드의 구조적 변경은 최소화하고 확장(Extension) 위주로 작성하십시오.
- **Environment**: `.env.example` 템플릿을 최신화하고, 배포 가이드(PRD v3.0 섹션 18)의 순서를 준수하도록 안내하십시오.

## 6. Project Specific Context
- **Project Name**: Modu-Gil (모두길)
- **Target Area**: 경기도 수원시 전역
- **Key Modules**: 
  - `route.py`: Tmap 보행자 경로 + 계단/경사 필터링
  - `places.py`: PostGIS ST_DWithin 300m 반경 검색
  - `reports.py`: Multipart 이미지 업로드 + Supabase Storage