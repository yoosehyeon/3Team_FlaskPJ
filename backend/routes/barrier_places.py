from flask import Blueprint, request, jsonify
from sqlalchemy import text
from db import SessionLocal

barrier_bp = Blueprint('barrier', __name__, url_prefix='/api/barrier')

@barrier_bp.route('/places', methods=['GET'])
def get_barrier_places():
    """
    Get barrier-free facilities within a specified radius (default 300m).
    URL params: lat, lng, radius (optional, default 300m)
    """
    lat = request.args.get('lat', type=float)
    lng = request.args.get('lng', type=float)
    radius = request.args.get('radius', default=300, type=float)

    if lat is None or lng is None:
        return jsonify({
            "status": "error",
            "message": "Latitude (lat) and Longitude (lng) are required"
        }), 400

    db = SessionLocal()
    try:
        # Use PostGIS ST_DWithin and ST_Distance for accurate proximity sorting
        # Casting to geography ensures distance is in meters
        query = text("""
            SELECT 
                esntl_id, fclty_nm, lclas_nm, mlsfc_nm, fclty_road_nm_addr, fclty_la, fclty_lo,
                ST_Distance(geom::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) as distance
            FROM barrier_places
            WHERE ST_DWithin(geom::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius)
            ORDER BY distance ASC
        """)
        
        results = db.execute(query, {"lat": lat, "lng": lng, "radius": radius}).fetchall()
        
        places = []
        for row in results:
            places.append({
                "esntl_id": row.esntl_id,
                "name": row.fclty_nm,
                "category_large": row.lclas_nm,
                "category_mid": row.mlsfc_nm,
                "address": row.fclty_road_nm_addr,
                "lat": row.fclty_la,
                "lng": row.fclty_lo,
                "distance": round(row.distance, 1)
            })
            
        return jsonify({
            "status": "success",
            "count": len(places),
            "data": places
        })
    except Exception as e:
        print(f"Error in get_barrier_places: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
    finally:
        db.close()
