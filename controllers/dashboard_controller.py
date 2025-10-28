from flask import jsonify, request
from data import appointments, professionals

def get_appointments():
    email = request.args.get("user")

    user = next((p for p in professionals if p["email"] == email), None)

    if not user:
        return jsonify({"error": "usuario no encontrado"}), 404

    if user["role"] == "admin":
        result = appointments
    else:
        result = [a for a in appointments if a["professionId"] == user["id"]]

    return jsonify(result)