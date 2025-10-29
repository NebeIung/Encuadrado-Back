from flask import jsonify, request
from models.models import Appointment, Professional

def get_appointments():
    email = request.args.get("user")
    
    user = Professional.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    if user.role == "admin":
        appointments = Appointment.query.all()
    else:
        appointments = Appointment.query.filter_by(
            professional_id=user.id
        ).all()
    
    return jsonify([a.to_dict() for a in appointments]), 200