from flask import jsonify, request
from models.models import Appointment, Professional
from datetime import datetime, timedelta
from sqlalchemy import func, and_
import traceback

def get_appointments():
    """Obtener estadísticas y citas del dashboard con auto-actualización de estados"""
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
        
        # Auto-actualizar estados de citas
        update_appointment_states(now)
        
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
        
        # Calcular estadísticas
        stats = {
            'period': period_label,
            'total': len(period_appointments),
            'pending': len([a for a in period_appointments if a.status == 'pending']),
            'to_confirm': len([a for a in period_appointments if a.status == 'to_confirm']),
            'confirmed': len([a for a in period_appointments if a.status == 'confirmed']),
            'completed': len([a for a in period_appointments if a.status == 'completed']),
            'cancelled': len([a for a in period_appointments if a.status == 'cancelled']),
            'missed': len([a for a in period_appointments if a.status == 'missed']),
        }
        
        # Obtener citas por confirmar (prioritarias)
        to_confirm_appointments = [
            a.to_dict() for a in period_appointments 
            if a.status == 'to_confirm'
        ]
        
        # Ordenar por fecha
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


def update_appointment_states(now):
    """
    Actualizar automáticamente los estados de las citas:
    - pending -> to_confirm (si la cita es hoy)
    - confirmed/to_confirm -> completed (si la cita ya pasó)
    """
    try:
        from models.models import db
        
        # 1. Cambiar pending a to_confirm si la cita es hoy
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        pending_today = Appointment.query.filter(
            and_(
                Appointment.status == 'pending',
                Appointment.date >= today_start,
                Appointment.date < today_end
            )
        ).all()
        
        for apt in pending_today:
            apt.status = 'to_confirm'
        
        # 2. Cambiar confirmed/to_confirm a completed si ya pasó la hora
        past_appointments = Appointment.query.filter(
            and_(
                Appointment.status.in_(['confirmed', 'to_confirm']),
                Appointment.date < now
            )
        ).all()
        
        for apt in past_appointments:
            apt.status = 'completed'
        
        db.session.commit()
        
    except Exception as e:
        print(f"Error updating appointment states: {str(e)}")
        traceback.print_exc()
        db.session.rollback()