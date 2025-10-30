from flask import jsonify, request
from models.models import Professional
from werkzeug.security import check_password_hash
import traceback

def login():
    """Login de profesionales"""
    try:
        # Log para debug
        print("=== LOGIN ATTEMPT ===")
        print(f"Request content type: {request.content_type}")
        print(f"Request data: {request.data}")
        
        data = request.get_json()
        print(f"Parsed JSON data: {data}")
        
        if not data:
            print("ERROR: No JSON data received")
            return jsonify({"error": "No se recibieron datos"}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        print(f"Email: {email}")
        print(f"Password received: {'Yes' if password else 'No'}")
        
        if not email or not password:
            print("ERROR: Missing email or password")
            return jsonify({"error": "Email y contraseña son requeridos"}), 400
        
        # Buscar profesional por email
        prof = Professional.query.filter_by(email=email).first()
        
        if not prof:
            print(f"ERROR: Professional not found for email: {email}")
            return jsonify({"error": "Credenciales inválidas"}), 401
        
        print(f"Professional found: {prof.name}")
        
        # Verificar contraseña
        if not check_password_hash(prof.password_hash, password):
            print("ERROR: Invalid password")
            return jsonify({"error": "Credenciales inválidas"}), 401
        
        print("SUCCESS: Login successful")
        
        # Retornar datos del profesional
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
        print(f"ERROR in login: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": "Error interno del servidor"}), 500