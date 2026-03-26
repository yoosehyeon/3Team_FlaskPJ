import os
from functools import wraps
from flask import request, jsonify
from supabase import create_client, Client

# Initialize Supabase client for auth
supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# Supabase 클라이언트 초기화 (보안 및 안정성 강화)
supabase = None
if supabase_url and supabase_key:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
    except Exception as e:
        print(f"[Auth] Supabase 초기화 실패 (네트워크/버전 충돌): {e}")
        supabase = None
else:
    print("[Auth] Supabase URL 또는 Key가 누락되었습니다.")

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
