from flask import jsonify, request
from models.models import Appointment, Professional
from datetime import datetime

def get_appointments():
    email = request.args.get("user")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    
    if not email:
        return jsonify({"error": "Usuario requerido"}), 400
    
    user = Professional.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    # Query base
    if user.role == "admin":
        query = Appointment.query
    else:
        query = Appointment.query.filter_by(professional_id=user.id)
    
    # Filtrar por rango de fechas si se proporcionan
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        query = query.filter(Appointment.date >= start)
    
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d')
        # Agregar un día para incluir todo el día final
        from datetime import timedelta
        end = end + timedelta(days=1)
        query = query.filter(Appointment.date < end)
    
    appointments = query.order_by(Appointment.date).all()
    
    return jsonify([a.to_dict() for a in appointments]), 200