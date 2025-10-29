from flask import jsonify, request
from models.models import Professional

def login():
    data = request.get_json()
    user = data.get("user")
    password = data.get("password")

    # Buscar en la base de datos
    prof = Professional.query.filter_by(
        email=user, 
        password=password,  # En producción usar hash
        is_active=True
    ).first()

    if not prof:
        return jsonify({"error": "Credenciales inválidas"}), 401

    return jsonify({
        "user": prof.email,
        "name": prof.name,
        "role": prof.role
    }), 200