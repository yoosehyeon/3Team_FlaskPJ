# F5 — 실시간 위험 신고 엔진

> PRD v3.0 담당자: 김성익 (PL)
> 기능 분류: 실시간 위험 정보 공유 (Supabase Realtime + Storage)

---

## 담당 기능 개요

사용자가 휠체어·보행 중 마주친 위험 요소(계단, 공사, 급경사, 엘리베이터 고장)를 실시간으로 신고하면, **모든 접속자의 지도에 즉시 마커가 표시**되는 기능입니다.

- 신고 → POST /api/report → Supabase DB INSERT
- Supabase Realtime WebSocket → 전체 클라이언트 캐시 무효화
- TanStack Query re-fetch → 카카오맵 마커 즉시 렌더

---

## 담당 파일 목록

### Backend

| 파일 | 역할 |
|------|------|
| `backend/app.py` | Flask 앱 엔트리포인트, Flask-Limiter 설정, Blueprint 등록 |
| `backend/database.py` | SQLAlchemy NullPool 설정 (PgBouncer Transaction Mode 대응) |
| `backend/routes/reports.py` | 위험 신고 API 라우트 (POST /api/report, GET /api/reports) |

### Frontend

| 파일 | 역할 |
|------|------|
| `frontend/src/hooks/useReportsRealtime.js` | Supabase Realtime WebSocket 구독 훅 |
| `frontend/src/store/useMapStore.js` | dangerMarkers 전역 상태 (Zustand, 30분 자동 소멸) |
| `frontend/src/components/F-sse/ReportModal.jsx` | 위험 신고 모달 UI (유형·위험도·사진 선택 후 제출) |
| `frontend/src/components/F-sse/DangerMarker.jsx` | 카카오맵 위험 마커 오버레이 컴포넌트 |

### DB / 인프라

| 파일 | 역할 |
|------|------|
| `supabase/migrations/0005_reports.sql` | reports 테이블 DDL, RLS 정책 2개, Realtime 등록, Storage 버킷 정책 |
| `netlify.toml` | SPA fallback, `/api/*` → Flask 백엔드 프록시 |

---

## API 명세

### POST /api/report
위험 신고를 접수합니다.

**인증**: Authorization: Bearer `<Supabase JWT>`
**Content-Type**: multipart/form-data

| 필드 | 타입 | 필수 | 설명 |
|------|------|:----:|------|
| latitude | float | ✅ | GPS 위도 |
| longitude | float | ✅ | GPS 경도 |
| type | string | ✅ | `stairs` / `construction` / `steep_slope` / `elevator_broken` |
| severity | int | ✅ | 위험도 1~5 |
| image | file | ❌ | 현장 사진 (jpg, png 등) |

**응답 예시 (201)**
```json
{ "status": "ok", "id": "550e8400-e29b-41d4-a716-446655440000" }
```

### GET /api/reports
최근 50건의 위험 신고를 최신순으로 조회합니다.

**인증**: 불필요

**응답 예시 (200)**
```json
[
  {
    "id": "550e8400...",
    "type": "stairs",
    "severity": 4,
    "image_url": "https://xxx.supabase.co/storage/v1/object/public/reports-images/uuid.jpg",
    "created_at": "2025-05-01T12:00:00+00:00"
  }
]
```

---

## 데이터베이스 구조

```sql
CREATE TABLE reports (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    location    geometry(Point, 4326) NOT NULL,   -- PostGIS POINT(lng lat)
    type        TEXT NOT NULL,                     -- 위험 유형 enum
    severity    INTEGER NOT NULL DEFAULT 3,        -- 위험도 1~5
    image_url   TEXT,                              -- Supabase Storage 공개 URL
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**RLS 정책**
- `reports_insert`: 로그인한 사용자만 본인 user_id로 INSERT 가능
- `reports_select`: 누구나 SELECT 가능 (지도 마커 표시용)

**Realtime**: `supabase_realtime` 발행 테이블로 등록됨

---

## 실시간 동작 흐름

```
[사용자] 신고 제출
    │
    ▼
POST /api/report (Flask)
    │ JWT 검증 → 이미지 Storage 업로드 → reports INSERT
    ▼
Supabase Realtime (WebSocket)
    │ INSERT 이벤트 감지 → payload.new (신규 행 전체)
    ▼
useReportsRealtime.js (모든 접속자)
    ├─ invalidateQueries(['reports']) → GET /api/reports 재요청 (전체 목록 갱신)
    └─ addDangerMarker(payload.new)  → 카카오맵 마커 즉시 표시 (API 재요청 대기 없음)
```

---

## 주요 설정 사항

### Flask-Limiter (Rate Limiting)
- `/api/route`: 분당 30회 제한 (카카오맵 API 쿼터 보호, PRD 9.2)
- 전역 기본값: 하루 200회, 시간당 50회

### SQLAlchemy NullPool
Supabase는 내부적으로 PgBouncer(Transaction Mode)를 사용하기 때문에 SQLAlchemy 기본 커넥션 풀과 충돌이 발생합니다. `NullPool`은 매 요청마다 새 연결을 열고 즉시 반환하므로 이 문제를 해결합니다.

### 마커 자동 소멸 (30분)
`useMapStore.js`의 `addDangerMarker()`는 마커 추가 시 30분 이상 된 오래된 마커를 자동으로 제거합니다.

---

## 환경변수

`.env` 파일에 아래 항목을 설정해야 합니다.

```
# Backend (Flask)
SUPABASE_URL=https://<project-id>.supabase.co
SUPABASE_SERVICE_KEY=<service_role_key>
DATABASE_URL=postgresql://postgres:<password>@db.<project-id>.supabase.co:6543/postgres

# Frontend (Vite)
VITE_API_URL=http://localhost:5000
VITE_SUPABASE_URL=https://<project-id>.supabase.co
VITE_SUPABASE_ANON_KEY=<anon_key>
```

> **주의**: `SUPABASE_SERVICE_KEY`는 RLS를 우회하는 관리자 키입니다. 절대 프론트엔드에 노출하지 마세요.

---

## 주요 변경 이력

### 2026-03-26 코드 점검 및 수정

| 파일 | 변경 내용 |
|------|-----------|
| `backend/app.py` | import 경로 수정 (`backend.routes.reports` → `routes.reports`), 파일 복구 |
| `backend/Procfile` | gunicorn 실행 명령 추가 (`web: gunicorn app:app`) |
| `backend/database.py` | 파일 말미 잘림 복구 (`get_db()` 함수, `Base` 선언) |
| `backend/routes/reports.py` | 0바이트 → 전체 코드 신규 작성 (JWT 인증, POST/GET 엔드포인트) |
| `supabase/migrations/0005_reports.sql` | Storage 업로드 정책 복구, `severity`·`image_url` 컬럼 추가 |
| `frontend/src/components/F-sse/ReportModal.jsx` | 파일 말미 잘림 복구 (사진 업로드 UI, 제출 버튼) |
| `frontend/src/hooks/useReportsRealtime.js` | `addDangerMarker(payload.new)` 연결 — Realtime 수신 즉시 마커 표시 |
| `frontend/src/store/useUIStore.js` | dangerMarkers 중복 블록에 미사용 주의 코멘트 추가 (코드 유지) |

### 미결 사항 (배포 전 확인 필요)

| 항목 | 내용 | 담당 |
|------|------|------|
| CORS 설정 | `CORS(app)` 전면 개방 → Netlify 도메인만 허용으로 좁혀야 함 | F5 (배포 시점에 수정) |
| `useUIStore.js` dangerMarkers 블록 | `useMapStore`와 중복 — 추후 제거 권장 | B팀원 협의 후 |

---

## Supabase 설정 체크리스트

Supabase 대시보드에서 아래 항목을 확인하세요.

- [ ] `supabase/migrations/0005_reports.sql` SQL Editor에서 실행 완료
- [ ] `reports-images` 스토리지 버킷 생성 확인 (Storage 메뉴)
- [ ] 버킷 공개 읽기 정책 활성화 확인
- [ ] Database → Replication → `reports` 테이블 Realtime 활성화 확인
- [ ] Authentication → Policies → `reports` 테이블 RLS 2개 확인
