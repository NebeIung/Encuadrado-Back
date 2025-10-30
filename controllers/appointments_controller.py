from flask import jsonify, request
from models.models import db, Appointment, Patient, Professional, Specialty
from datetime import datetime

def get_all_appointments():
    """Obtener todas las citas con filtros"""
    try:
        user_email = request.args.get('user')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        query = Appointment.query
        
        # Filtrar por profesional si es member
        if user_email:
            professional = Professional.query.filter_by(email=user_email).first()
            if professional and professional.role != 'admin':
                query = query.filter(Appointment.professional_id == professional.id)
        
        # Filtrar por rango de fechas
        if start_date:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(Appointment.date >= start)
        
        if end_date:
            end = datetime.strptime(end_date, '%Y-%m-%d')
            # Agregar 1 día para incluir todas las horas del último día
            from datetime import timedelta
            end = end + timedelta(days=1)
            query = query.filter(Appointment.date < end)
        
        appointments = query.order_by(Appointment.date.asc()).all()
        return jsonify([apt.to_dict() for apt in appointments]), 200
    except Exception as e:
        print(f"Error getting appointments: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def create_appointment_admin():
    """Crear una cita (Admin o Member)"""
    try:
        data = request.get_json()
        
        # Validar campos requeridos
        required_fields = ['patient_id', 'professional_id', 'specialty_id', 'date']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido: {field}"}), 400
        
        # Validar que existan las entidades
        patient = Patient.query.get(data['patient_id'])
        if not patient:
            return jsonify({"error": "Paciente no encontrado"}), 404
        
        professional = Professional.query.get(data['professional_id'])
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        specialty = Specialty.query.get(data['specialty_id'])
        if not specialty:
            return jsonify({"error": "Especialidad no encontrada"}), 404
        
        # Crear la cita
        appointment = Appointment(
            patient_id=data['patient_id'],
            professional_id=data['professional_id'],
            specialty_id=data['specialty_id'],
            date=datetime.fromisoformat(data['date'].replace('Z', '')),
            status=data.get('status', 'confirmed'),
            notes=data.get('notes', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify(appointment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating appointment: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def update_appointment_admin(appointment_id):
    """Actualizar una cita (Admin o Member)"""
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Cita no encontrada"}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'date' in data:
            appointment.date = datetime.fromisoformat(data['date'].replace('Z', ''))
        if 'status' in data:
            appointment.status = data['status']
        if 'notes' in data:
            appointment.notes = data['notes']
        if 'cancellation_reason' in data:
            appointment.cancellation_reason = data['cancellation_reason']
        
        db.session.commit()
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating appointment: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def cancel_appointment(appointment_id):
    """Cancelar una cita"""
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Cita no encontrada"}), 404
        
        data = request.get_json() or {}
        appointment.status = 'cancelled'
        appointment.cancellation_reason = data.get('reason', 'Sin motivo especificado')
        
        db.session.commit()
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error cancelling appointment: {str(e)}")
        return jsonify({"error": str(e)}), 500

def reschedule_appointment(appointment_id):
    """Reagendar una cita"""
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Cita no encontrada"}), 404
        
        data = request.get_json()
        if 'date' not in data:
            return jsonify({"error": "Nueva fecha requerida"}), 400
        
        appointment.date = datetime.fromisoformat(data['date'].replace('Z', ''))
        
        db.session.commit()
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error rescheduling appointment: {str(e)}")
        return jsonify({"error": str(e)}), 500