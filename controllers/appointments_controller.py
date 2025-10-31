from flask import jsonify, request
from models.models import db, Appointment, Patient, Professional, Specialty
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import traceback

def get_dashboard_stats():
    """Obtener estadísticas y citas del dashboard - SIN auto-actualización de estados"""
    try:
        user_email = request.args.get('user')
        period = request.args.get('period', 'daily')
        
        now = datetime.now()
        
        # Determinar rango de fechas
        if period == 'daily':
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            period_label = 'hoy'
        else:
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            if now.month == 12:
                end_date = now.replace(year=now.year + 1, month=1, day=1)
            else:
                end_date = now.replace(month=now.month + 1, day=1)
            period_label = 'del mes'
        
        # Filtrar por profesional si no es admin
        query = Appointment.query
        if user_email:
            professional = Professional.query.filter_by(email=user_email).first()
            if professional and professional.role != 'admin':
                query = query.filter(Appointment.professional_id == professional.id)
        
        # Obtener todas las citas del período
        period_appointments = query.filter(
            and_(
                Appointment.date >= start_date,
                Appointment.date < end_date
            )
        ).all()
        
        # Calcular "to_confirm" en tiempo real
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        next_hour = current_hour + timedelta(hours=1)
        
        to_confirm_list = []
        for apt in period_appointments:
            if apt.status == 'pending':
                if apt.date < now or (apt.date >= current_hour and apt.date < next_hour):
                    to_confirm_list.append(apt)
        
        # Calcular estadísticas
        stats = {
            'period': period_label,
            'total': len(period_appointments),
            'pending': len([a for a in period_appointments if a.status == 'pending']),
            'to_confirm': len(to_confirm_list),
            'confirmed': len([a for a in period_appointments if a.status == 'confirmed']),
            'cancelled': len([a for a in period_appointments if a.status == 'cancelled']),
            'missed': len([a for a in period_appointments if a.status == 'missed']),
        }
        
        # Obtener citas por confirmar (ordenadas por fecha)
        to_confirm_appointments = [a.to_dict() for a in to_confirm_list]
        to_confirm_appointments.sort(key=lambda x: x['date'])
        
        return jsonify({
            'stats': stats,
            'to_confirm': to_confirm_appointments,
            'all_appointments': [a.to_dict() for a in period_appointments]
        }), 200
        
    except Exception as e:
        print(f"Error getting dashboard data: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


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
            end = end + timedelta(days=1)
            query = query.filter(Appointment.date < end)
        
        appointments = query.order_by(Appointment.date.asc()).all()
        return jsonify([apt.to_dict() for apt in appointments]), 200
    except Exception as e:
        print(f"Error getting appointments: {str(e)}")
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
            status=data.get('status', 'pending'),
            notes=data.get('notes', '')
        )
        
        db.session.add(appointment)
        db.session.commit()
        
        return jsonify(appointment.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating appointment: {str(e)}")
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
            valid_states = ['pending', 'confirmed', 'cancelled', 'missed']
            if data['status'] not in valid_states:
                return jsonify({"error": f"Estado inválido. Estados válidos: {', '.join(valid_states)}"}), 400
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
        traceback.print_exc()
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
        # Resetear a pending cuando se reagenda
        appointment.status = 'pending'
        
        db.session.commit()
        return jsonify(appointment.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error rescheduling appointment: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500