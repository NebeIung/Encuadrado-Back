from flask import jsonify, request
from models.models import db, Professional, Specialty, Appointment, Patient
from datetime import datetime, timedelta
import traceback

def get_available_hours():
    """
    Obtener horas disponibles considerando horarios por especialidad
    """
    try:
        date = request.args.get("date")
        professional_id = request.args.get("professionalId")
        service_id = request.args.get("serviceId")

        print(f"=== GET AVAILABLE HOURS ===")
        print(f"Date: {date}, Professional: {professional_id}, Service: {service_id}")

        if not date or not service_id or not professional_id:
            return jsonify({"error": "Faltan parámetros requeridos"}), 400

        service = Specialty.query.get(int(service_id))
        if not service:
            return jsonify({"error": "Servicio no encontrado"}), 404

        prof = Professional.query.get(int(professional_id))
        if not prof:
            return jsonify({"error": "Profesional no encontrado"}), 404

        # Obtener horario específico para esta especialidad
        if not prof.schedule or service_id not in prof.schedule:
            print(f"No schedule found for specialty {service_id}")
            return jsonify([]), 200

        specialty_schedule = prof.schedule[service_id]
        
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        weekday = date_obj.weekday()
        day_keys = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
        day_key = day_keys[weekday]

        day_schedule = specialty_schedule.get(day_key, {})
        
        if not day_schedule or not day_schedule.get('enabled') or not day_schedule.get('start') or not day_schedule.get('end'):
            print(f"No work schedule for {day_key}")
            return jsonify([]), 200

        duration = service.duration
        
        work_start = datetime.strptime(f"{date} {day_schedule['start']}", "%Y-%m-%d %H:%M")
        work_end = datetime.strptime(f"{date} {day_schedule['end']}", "%Y-%m-%d %H:%M")

        lunch_start = None
        lunch_end = None
        if day_schedule.get('lunch_start') and day_schedule.get('lunch_end'):
            lunch_start = datetime.strptime(f"{date} {day_schedule['lunch_start']}", "%Y-%m-%d %H:%M")
            lunch_end = datetime.strptime(f"{date} {day_schedule['lunch_end']}", "%Y-%m-%d %H:%M")

        appointments_on_date = Appointment.query.filter(
            Appointment.professional_id == prof.id,
            db.func.date(Appointment.date) == date_obj.date(),
            Appointment.status.in_(['confirmed', 'pending'])
        ).all()

        busy_intervals = []
        for apt in appointments_on_date:
            apt_start = apt.date
            apt_duration = apt.specialty.duration
            apt_end = apt_start + timedelta(minutes=apt_duration)
            busy_intervals.append((apt_start, apt_end))

        available_hours = []
        current = work_start
        
        while current + timedelta(minutes=duration) <= work_end:
            slot_end = current + timedelta(minutes=duration)
            
            if lunch_start and lunch_end:
                if not (slot_end <= lunch_start or current >= lunch_end):
                    current += timedelta(minutes=15)
                    continue
            
            has_conflict = False
            for busy_start, busy_end in busy_intervals:
                if not (slot_end <= busy_start or current >= busy_end):
                    has_conflict = True
                    break
            
            if not has_conflict:
                available_hours.append(current.strftime("%H:%M"))
            
            current += timedelta(minutes=15)

        return jsonify(available_hours), 200

    except Exception as e:
        print(f"ERROR in get_available_hours: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


def create_appointment():
    """
    Crear una cita desde el flujo público
    """
    try:
        data = request.get_json()
        
        specialty_id = data.get('specialty_id')
        scheduled_at = data.get('scheduled_at')
        professional_id = data.get('professional_id')
        
        if not specialty_id or not scheduled_at or not professional_id:
            return jsonify({"error": "Faltan campos requeridos"}), 400

        specialty = Specialty.query.get(specialty_id)
        if not specialty:
            return jsonify({"error": "Especialidad no encontrada"}), 404

        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404

        appointment_date = datetime.fromisoformat(scheduled_at.replace('Z', '+00:00'))
        appointment_end = appointment_date + timedelta(minutes=specialty.duration)
        
        conflicts = Appointment.query.filter(
            Appointment.professional_id == professional_id,
            Appointment.status.in_(['confirmed', 'pending']),
            db.func.date(Appointment.date) == appointment_date.date()
        ).all()

        for conflict in conflicts:
            conflict_end = conflict.date + timedelta(minutes=conflict.specialty.duration)
            if not (appointment_end <= conflict.date or appointment_date >= conflict_end):
                return jsonify({"error": "Este horario ya no está disponible"}), 409

        patient_email = data.get('patient_email')
        patient_id = None

        if patient_email:
            patient = Patient.query.filter_by(email=patient_email).first()
            if not patient:
                patient = Patient(
                    name=data.get('patient_name', 'Paciente Temporal'),
                    email=patient_email,
                    phone=data.get('patient_phone', 'Sin teléfono'),
                    rut=data.get('patient_rut', '00000000-0'),
                    birth_date=datetime.now()
                )
                db.session.add(patient)
                db.session.flush()
            
            patient_id = patient.id
        else:
            patient = Patient(
                name="Paciente Web",
                email=f"temp_{datetime.now().timestamp()}@temporal.com",
                phone="Sin teléfono",
                rut="00000000-0",
                birth_date=datetime.now()
            )
            db.session.add(patient)
            db.session.flush()
            patient_id = patient.id

        appointment = Appointment(
            patient_id=patient_id,
            professional_id=professional_id,
            specialty_id=specialty_id,
            date=appointment_date,
            status='confirmed',
            notes=data.get('notes', 'Cita agendada desde web pública')
        )

        db.session.add(appointment)
        db.session.commit()

        return jsonify({
            "message": "Cita creada exitosamente",
            "appointment": appointment.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"ERROR en create_appointment: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500