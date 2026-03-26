"""
F5 실시간 위험 신고 엔진 — 백엔드 라우트
PRD v3.0 / 김성익 PL 담당

엔드포인트:
  POST /api/report  — 위험 신고 접수 (이미지 + 위치 + 유형)
  GET  /api/reports — 최근 신고 목록 조회 (최대 50건)
"""

import os
import uuid
from functools import wraps

from flask import Blueprint, request, jsonify
from supabase import create_client, Client

# ── Supabase 클라이언트 초기화 ──────────────────────────────────────────────
# 환경변수에서 Supabase 프로젝트 URL과 Service Role Key를 읽는다.
# Service Role Key는 RLS를 우회하므로 절대 클라이언트에 노출하면 안 된다.
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY: str = os.environ.get("SUPABASE_SERVICE_KEY", "")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Flask Blueprint 등록 — app.py에서 register_blueprint()로 마운트
reports_bp = Blueprint("reports", __name__)

# Supabase Storage 버킷 이름 (0005_reports.sql에서 생성)
BUCKET_NAME = "reports-images"


# ── JWT 인증 미들웨어 ──────────────────────────────────────────────────────
def require_auth(f):
    """
    Authorization 헤더의 Bearer JWT를 검증하는 데코레이터.
    Supabase Auth의 getUser() API로 토큰 유효성을 확인한다.
    인증 실패 시 401 Unauthorized 반환.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "인증 토큰이 없습니다."}), 401

        token = auth_header.split(" ", 1)[1]
        try:
            # Supabase Auth API로 토큰 검증 및 사용자 정보 조회
            user_resp = supabase.auth.get_user(token)
            request.user_id = user_resp.user.id  # 이후 핸들러에서 사용
        except Exception:
            return jsonify({"error": "유효하지 않은 토큰입니다."}), 401

        return f(*args, **kwargs)
    return decorated


# ── POST /api/report — 위험 신고 접수 ────────────────────────────────────
@reports_bp.route("/api/report", methods=["POST"])
@require_auth
def create_report():
    """
    위험 신고를 접수하는 엔드포인트.

    요청 형식: multipart/form-data
      - latitude  (float)  : GPS 위도
      - longitude (float)  : GPS 경도
      - type      (string) : 위험 유형 (stairs / construction / steep_slope / elevator_broken)
      - severity  (int)    : 위험도 1~5
      - image     (file)   : 첨부 이미지 (선택)

    처리 흐름:
      1) 이미지가 있으면 Supabase Storage에 업로드 → 공개 URL 획득
      2) reports 테이블에 INSERT
      3) Supabase Realtime이 INSERT 감지 → 모든 접속자 지도에 마커 자동 표시
    """
    # 폼 데이터 파싱
    try:
        latitude = float(request.form.get("latitude"))
        longitude = float(request.form.get("longitude"))
        report_type = request.form.get("type", "stairs")
        severity = int(request.form.get("severity", 3))
    except (TypeError, ValueError):
        return jsonify({"error": "latitude, longitude 값이 유효하지 않습니다."}), 400

    # ── 이미지 업로드 (선택) ──────────────────────────────────────────────
    image_url = None
    image_file = request.files.get("image")
    if image_file:
        # 파일명 충돌 방지를 위해 UUID로 고유 경로 생성
        ext = image_file.filename.rsplit(".", 1)[-1] if "." in image_file.filename else "jpg"
        file_path = f"{uuid.uuid4()}.{ext}"

        # Supabase Storage에 바이너리로 업로드
        file_bytes = image_file.read()
        supabase.storage.from_(BUCKET_NAME).upload(
            path=file_path,
            file=file_bytes,
            file_options={"content-type": image_file.content_type or "image/jpeg"},
        )

        # 공개 URL 조회 (버킷이 public이므로 서명 없이 접근 가능)
        url_resp = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)
        image_url = url_resp  # SDK v2는 문자열 반환

    # ── reports 테이블 INSERT ─────────────────────────────────────────────
    # PostGIS geometry는 WKT 형식으로 삽입 (POINT(lng lat) 순서 주의)
    insert_data = {
        "user_id": request.user_id,
        "location": f"POINT({longitude} {latitude})",
        "type": report_type,
        "severity": severity,
        "image_url": image_url,
    }

    result = supabase.table("reports").insert(insert_data).execute()

    # INSERT 성공 시 Supabase Realtime이 자동으로 프론트엔드에 이벤트를 전송한다.
    return jsonify({"status": "ok", "id": result.data[0]["id"]}), 201


# ── GET /api/reports — 최근 신고 목록 조회 ───────────────────────────────
@reports_bp.route("/api/reports", methods=["GET"])
def get_reports():
    """
    최근 50건의 위험 신고를 최신순으로 조회한다.
    인증 불필요 — 지도에 마커를 표시할 때 사용.
    """
    result = (
        supabase.table("reports")
        .select("id, type, severity, image_url, created_at, location")
        .order("created_at", desc=True)
        .limit(50)
        .execute()
    )
    return jsonify(result.data), 200
