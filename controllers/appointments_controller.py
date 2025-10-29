from flask import jsonify, request
from models.models import db, Appointment, Patient, Professional, Specialty
from datetime import datetime

def get_all_appointments():
    """Obtener todas las citas (Admin)"""
    try:
        appointments = Appointment.query.order_by(Appointment.date.desc()).all()
        return jsonify([a.to_dict() for a in appointments]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_appointment_admin():
    """Crear una cita manualmente (Admin/Member)"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not all(k in data for k in ['patient_id', 'professional_id', 'specialty_id', 'date']):
            return jsonify({"error": "Faltan campos requeridos"}), 400
        
        # Verificar que existan
        patient = Patient.query.get(data['patient_id'])
        if not patient:
            return jsonify({"error": "Paciente no encontrado"}), 404
        
        professional = Professional.query.get(data['professional_id'])
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        specialty = Specialty.query.get(data['specialty_id'])
        if not specialty:
            return jsonify({"error": "Especialidad no encontrada"}), 404
        
        # Parsear fecha
        appointment_date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M')
        
        # Verificar disponibilidad (opcional - implementar lógica)
        # ...
        
        # Crear cita
        appointment = Appointment(
            patient_id=data['patient_id'],
            professional_id=data['professional_id'],
            specialty_id=data['specialty_id'],
            date=appointment_date,
            status='confirmed',
            notes=data.get('notes', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify(appointment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def update_appointment_admin(appointment_id):
    """Actualizar una cita existente"""
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Cita no encontrada"}), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'date' in data:
            appointment.date = datetime.strptime(data['date'], '%Y-%m-%d %H:%M')
        if 'status' in data:
            appointment.status = data['status']
        if 'notes' in data:
            appointment.notes = data['notes']
        if 'patient_id' in data:
            appointment.patient_id = data['patient_id']
        if 'professional_id' in data:
            appointment.professional_id = data['professional_id']
        if 'specialty_id' in data:
            appointment.specialty_id = data['specialty_id']
        
        db.session.commit()
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
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
        return jsonify({"message": "Cita cancelada"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def reschedule_appointment(appointment_id):
    """Reagendar una cita"""
    try:
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"error": "Cita no encontrada"}), 404
        
        data = request.get_json()
        new_date = data.get("date")
        
        if not new_date:
            return jsonify({"error": "Fecha requerida"}), 400
        
        appointment.date = datetime.strptime(new_date, '%Y-%m-%d %H:%M')
        appointment.status = 'rescheduled'
        
        db.session.commit()
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def get_appointments_by_professional(professional_id):
    """Obtener citas de un profesional específico"""
    try:
        appointments = Appointment.query.filter_by(
            professional_id=professional_id
        ).order_by(Appointment.date.desc()).all()
        
        return jsonify([a.to_dict() for a in appointments]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_appointments_by_patient(patient_id):
    """Obtener citas de un paciente específico"""
    try:
        appointments = Appointment.query.filter_by(
            patient_id=patient_id
        ).order_by(Appointment.date.desc()).all()
        
        return jsonify([a.to_dict() for a in appointments]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500