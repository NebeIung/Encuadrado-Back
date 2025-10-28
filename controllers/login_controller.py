from flask import jsonify, request
from data import professionals  # Importamos usuarios desde data.py

def login():
    data = request.get_json()
    user = data.get("user")
    password = data.get("password")

    # Por ahora, validación simple: todas las cuentas usan 1234
    if password != "1234":
        return jsonify({"error": "Credenciales inválidas"}), 401

    # Buscamos el usuario en la data local
    prof = next((p for p in professionals if p["email"] == user), None)

    if not prof:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Lo que guardamos en localStorage en el frontend
    return jsonify({
        "user": prof["email"],
        "name": prof["name"],
        "role": prof["role"]
    }), 200