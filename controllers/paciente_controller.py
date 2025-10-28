from flask import jsonify

def paciente():
    return jsonify({
        "pacientes": [
            {"id": 1, "nombre": "Juan Pérez"},
            {"id": 2, "nombre": "María González"}
        ]
    })