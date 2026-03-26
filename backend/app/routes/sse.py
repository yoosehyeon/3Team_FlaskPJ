import json
import queue
import threading
from flask import Blueprint, Response, request, stream_with_context
from backend.database import SessionLocal
from backend.models import Barrier

sse_bp = Blueprint("sse", __name__)

# 연결된 클라이언트 큐 목록 (thread-safe)
_clients: list = []
_clients_lock = threading.Lock()


def broadcast(data: dict):
    """연결된 모든 클라이언트에 이벤트 전송"""
    dead = []
    with _clients_lock:
        for q in _clients:
            try:
                q.put_nowait(data)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _clients.remove(q)


@sse_bp.route("/api/sse")
def sse_stream():
    """SSE 연결 엔드포인트 — 모든 브라우저가 여기에 연결"""
    q = queue.Queue(maxsize=20)
    with _clients_lock:
        _clients.append(q)

    def generate():
        try:
            # 연결 즉시 현재 접속자 수 전송
            msg = {'type': 'connected', 'clients': len(_clients)}
            yield f"data: {json.dumps(msg)}\n\n"
            while True:
                try:
                    data = q.get(timeout=25)
                    yield f"data: {json.dumps(data)}\n\n"
                except queue.Empty:
                    # 연결 유지용 heartbeat
                    yield ": heartbeat\n\n"
        except GeneratorExit:
            with _clients_lock:
                if q in _clients:
                    _clients.remove(q)

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Cloudtype Nginx 버퍼링 방지
            "Access-Control-Allow-Origin": "*",
        },
    )


@sse_bp.route("/api/barriers", methods=["POST"])
def report_barrier():
    """위험 신고 접수 → DB 저장 → 전체 브라우저에 broadcast"""
    data = request.get_json()
    if not data:
        return {"error": "요청 데이터가 없습니다."}, 400

    db = SessionLocal()
    try:
        barrier = Barrier(
            latitude=data.get("latitude"),
            longitude=data.get("longitude"),
            type=data.get("type"),
            severity=data.get("severity", 3),
            image_url=data.get("image_url"),
            verified=False,
        )
        db.add(barrier)
        db.commit()
        db.refresh(barrier)

        # 모든 연결된 클라이언트에 실시간 전파
        broadcast({
            "type": "new_barrier",
            "payload": {
                "id": barrier.id,
                "latitude": barrier.latitude,
                "longitude": barrier.longitude,
                "barrier_type": barrier.type,
                "severity": barrier.severity,
                "image_url": barrier.image_url,
                "created_at": str(barrier.created_at),
            },
        })

        return {"status": "ok", "barrier_id": barrier.id}, 201

    except Exception as e:
        db.rollback()
        return {"error": str(e)}, 500
    finally:
        db.close()


@sse_bp.route("/api/barriers", methods=["GET"])
def get_barriers():
    """현재 활성 위험 마커 목록 조회"""
    db = SessionLocal()
    try:
        barriers = (
            db.query(Barrier)
            .order_by(Barrier.created_at.desc())
            .limit(50)
            .all()
        )
        return {
            "barriers": [
                {
                    "id": b.id,
                    "latitude": b.latitude,
                    "longitude": b.longitude,
                    "type": b.type,
                    "severity": b.severity,
                    "image_url": b.image_url,
                    "created_at": str(b.created_at),
                }
                for b in barriers
            ]
        }, 200
    finally:
        db.close()
