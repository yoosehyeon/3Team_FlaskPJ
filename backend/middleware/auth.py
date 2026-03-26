import os
from functools import wraps
from flask import request, jsonify
from supabase import create_client, Client

# Initialize Supabase client for auth
supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# Only create the client if the keys are actually present.
# Since this creates a global object, it might fail if SUPABASE_URL is empty in some environments.
if supabase_url and supabase_key:
    supabase: Client = create_client(supabase_url, supabase_key)
else:
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
