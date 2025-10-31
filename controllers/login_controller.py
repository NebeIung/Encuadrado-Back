from flask import jsonify, request
from models.models import Professional
from werkzeug.security import check_password_hash

def login():
    """Login de profesionales"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email y contraseña son requeridos"}), 400
        
        prof = Professional.query.filter_by(email=email).first()
        
        if not prof:
            return jsonify({"error": "Credenciales inválidas"}), 401
        
        if not check_password_hash(prof.password_hash, password):
            return jsonify({"error": "Credenciales inválidas"}), 401
        
        return jsonify({
            "id": prof.id,
            "name": prof.name,
            "email": prof.email,
            "role": prof.role,
            "specialties": [
                {
                    "id": s.id,
                    "name": s.name,
                    "duration": s.duration,
                    "price": s.price
                } for s in prof.specialties
            ]
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Error interno del servidor"}), 500