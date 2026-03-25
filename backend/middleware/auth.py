import os
from functools import wraps
from flask import request, jsonify
from supabase import create_client

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if supabase_url and supabase_key:
    supabase = create_client(supabase_url, supabase_key)
else:
    # 환경변수 없을 시 기본 처리 (에러 방지용)
    supabase = None

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not supabase:
             return jsonify({"error": "Supabase client not initialized"}), 500

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(" ")[1]
        try:
            user = supabase.auth.get_user(token)
            request.user = user
        except Exception:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated
