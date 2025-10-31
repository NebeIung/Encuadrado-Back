from flask import jsonify, request
from models.models import db, Professional, Specialty, Appointment, Patient, ProfessionalSpecialty
from datetime import datetime, timedelta
import json

def register_public_routes(app):
    @app.route('/api/public/services', methods=['GET'])
    def get_public_services():
        """Obtener servicios públicos activos con términos"""
        try:
            specialties = Specialty.query.filter_by(is_active=True).all()
            
            services_with_terms = [
                {
                    'id': s.id,
                    'name': s.name,
                    'description': s.description,
                    'duration': s.duration,
                    'price': s.price,
                    'color': s.color,
                    'has_terms': s.has_terms
                }
                for s in specialties if s.has_terms
            ]
            
            return jsonify(services_with_terms), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/public/professionals', methods=['GET'])
    def get_public_professionals_by_specialty():
        """Obtener profesionales públicos filtrados por especialidad"""
        try:
            specialty_id = request.args.get('specialty_id', type=int)
            
            if not specialty_id:
                return jsonify({'error': 'specialty_id es requerido'}), 400
            
            specialty = Specialty.query.get(specialty_id)
            if not specialty:
                return jsonify({'error': 'Especialidad no encontrada'}), 404
            
            professionals = Professional.query.filter(
                Professional.role != 'admin',
                Professional.specialties.any(id=specialty_id)
            ).all()
            
            result = []
            for prof in professionals:
                prof_specialty = None
                for s in prof.specialties:
                    if s.name == specialty.name:
                        prof_specialty = s
                        break
                
                schedule_for_specialty = None
                if prof.schedule and prof_specialty:
                    schedule_key = str(prof_specialty.id)
                    schedule_for_specialty = prof.schedule.get(schedule_key, None)
                
                result.append({
                    'id': prof.id,
                    'name': prof.name,
                    'email': prof.email,
                    'role': prof.role,
                    'specialties': [
                        {
                            'id': s.id,
                            'name': s.name,
                            'color': s.color,
                            'duration': s.duration
                        }
                        for s in prof.specialties
                    ],
                    'schedule': schedule_for_specialty or {}
                })
            
            return jsonify(result), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/available-days', methods=['GET'])
    def get_available_days():
        """Obtener días disponibles para un profesional y especialidad"""
        try:
            professional_id = request.args.get('professional_id', type=int)
            specialty_id = request.args.get('specialty_id', type=int)
            
            if not professional_id or not specialty_id:
                return jsonify({'error': 'professional_id y specialty_id son requeridos'}), 400
            
            professional = Professional.query.get(professional_id)
            if not professional:
                return jsonify({'error': 'Profesional no encontrado'}), 404
            
            specialty = Specialty.query.get(specialty_id)
            if not specialty or specialty not in professional.specialties:
                return jsonify({'error': 'El profesional no tiene esa especialidad'}), 400
            
            prof_specialty = None
            for s in professional.specialties:
                if s.name == specialty.name:
                    prof_specialty = s
                    break
            
            if not prof_specialty:
                return jsonify({'available_days': []}), 200
            
            schedule = professional.schedule or {}
            specialty_schedule = schedule.get(str(prof_specialty.id))
            
            if not specialty_schedule:
                return jsonify({'available_days': []}), 200
            
            available_days = []
            today = datetime.now().date()
            
            day_map_long = {
                0: 'monday', 1: 'tuesday', 2: 'wednesday',
                3: 'thursday', 4: 'friday', 5: 'saturday', 6: 'sunday'
            }
            
            day_map_short = {
                0: 'mon', 1: 'tue', 2: 'wed',
                3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'
            }
            
            for i in range(1, 61):
                check_date = today + timedelta(days=i)
                weekday = check_date.weekday()
                
                day_key = day_map_long.get(weekday)
                day_schedule = specialty_schedule.get(day_key, {})
                
                if not day_schedule:
                    day_key = day_map_short.get(weekday)
                    day_schedule = specialty_schedule.get(day_key, {})
                
                if day_schedule and day_schedule.get('enabled'):
                    available_days.append({
                        'date': check_date.isoformat(),
                        'day': day_key,
                        'start': day_schedule.get('start'),
                        'end': day_schedule.get('end'),
                        'lunch_start': day_schedule.get('lunch_start'),
                        'lunch_end': day_schedule.get('lunch_end')
                    })
            
            return jsonify({'available_days': available_days}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/available-slots', methods=['GET'])
    def get_available_slots():
        """Obtener horarios disponibles para un día específico"""
        try:
            professional_id = request.args.get('professional_id', type=int)
            specialty_id = request.args.get('specialty_id', type=int)
            date_str = request.args.get('date')
            
            if not all([professional_id, specialty_id, date_str]):
                return jsonify({'error': 'Faltan parámetros requeridos'}), 400
            
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            professional = Professional.query.get(professional_id)
            specialty = Specialty.query.get(specialty_id)
            
            if not professional or not specialty:
                return jsonify({'error': 'Profesional o especialidad no encontrados'}), 404
            
            prof_specialty = None
            for s in professional.specialties:
                if s.id == specialty_id:
                    prof_specialty = s
                    break
            
            if not prof_specialty:
                return jsonify({'available_slots': []}), 200
            
            schedule = professional.schedule or {}
            specialty_schedule = schedule.get(str(prof_specialty.id), {})
            
            day_map_long = {0: 'monday', 1: 'tuesday', 2: 'wednesday', 3: 'thursday', 4: 'friday', 5: 'saturday', 6: 'sunday'}
            day_map_short = {0: 'mon', 1: 'tue', 2: 'wed', 3: 'thu', 4: 'fri', 5: 'sat', 6: 'sun'}
            
            day_key = day_map_long.get(date.weekday())
            day_schedule = specialty_schedule.get(day_key, {})
            
            if not day_schedule:
                day_key = day_map_short.get(date.weekday())
                day_schedule = specialty_schedule.get(day_key, {})
            
            if not day_schedule or not day_schedule.get('enabled'):
                return jsonify({'available_slots': []}), 200
            
            start_datetime = datetime.combine(date, datetime.min.time())
            end_datetime = datetime.combine(date, datetime.max.time())
            
            existing_appointments = Appointment.query.filter(
                Appointment.professional_id == professional_id,
                Appointment.date >= start_datetime,
                Appointment.date <= end_datetime,
                Appointment.status.in_(['pending', 'confirmed'])
            ).all()
            
            occupied_times = set()
            for apt in existing_appointments:
                apt_start = apt.date
                apt_specialty = next((s for s in professional.specialties if s.id == apt.specialty_id), None)
                apt_duration = apt_specialty.duration if apt_specialty else 60
                
                current_time = apt_start
                end_time = apt_start + timedelta(minutes=apt_duration)
                
                while current_time < end_time:
                    occupied_times.add(current_time.strftime('%H:%M'))
                    current_time += timedelta(minutes=15)
            
            start_time = datetime.strptime(day_schedule['start'], '%H:%M').time()
            end_time = datetime.strptime(day_schedule['end'], '%H:%M').time()
            lunch_start = day_schedule.get('lunch_start')
            lunch_end = day_schedule.get('lunch_end')
            
            available_slots = []
            current_time = datetime.combine(date, start_time)
            end_datetime_check = datetime.combine(date, end_time)
            
            SLOT_INTERVAL = 15
            
            while current_time < end_datetime_check:
                time_str = current_time.strftime('%H:%M')
                
                in_lunch = False
                if lunch_start and lunch_end:
                    lunch_start_dt = datetime.strptime(lunch_start, '%H:%M').time()
                    lunch_end_dt = datetime.strptime(lunch_end, '%H:%M').time()
                    current_time_only = current_time.time()
                    in_lunch = lunch_start_dt <= current_time_only < lunch_end_dt
                
                enough_time = True
                if not in_lunch:
                    appointment_end = current_time + timedelta(minutes=specialty.duration)
                    
                    if appointment_end > end_datetime_check:
                        enough_time = False
                    
                    if lunch_start and lunch_end and enough_time:
                        lunch_start_dt_full = datetime.combine(date, datetime.strptime(lunch_start, '%H:%M').time())
                        lunch_end_dt_full = datetime.combine(date, datetime.strptime(lunch_end, '%H:%M').time())
                        
                        if current_time < lunch_start_dt_full < appointment_end:
                            enough_time = False
                
                if time_str not in occupied_times and not in_lunch and enough_time:
                    available_slots.append(time_str)
                
                current_time += timedelta(minutes=SLOT_INTERVAL)
            
            return jsonify({'available_slots': available_slots}), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    @app.route('/api/public/terms/<int:professional_id>/<int:specialty_id>', methods=['GET'])
    def get_terms_and_conditions(professional_id, specialty_id):
        """Obtener términos y condiciones de un profesional para una especialidad"""
        try:
            prof_specialty = ProfessionalSpecialty.query.filter_by(
                professional_id=professional_id,
                specialty_id=specialty_id
            ).first()
            
            professional = Professional.query.get(professional_id)
            specialty = Specialty.query.get(specialty_id)
            
            if not professional or not specialty:
                return jsonify({
                    'error': 'Profesional o especialidad no encontrados'
                }), 404
            
            if not prof_specialty or not prof_specialty.terms_and_conditions:
                return jsonify({
                    'content': 'No hay términos y condiciones específicos configurados para esta especialidad y profesional.',
                    'professional_name': professional.name,
                    'specialty_name': specialty.name,
                    'has_terms': False,
                    'updated_at': None
                }), 200
            
            return jsonify({
                'content': prof_specialty.terms_and_conditions or '',
                'professional_name': professional.name,
                'specialty_name': specialty.name,
                'has_terms': prof_specialty.has_terms,
                'updated_at': prof_specialty.updated_at.isoformat() if prof_specialty.updated_at else None
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/public/appointment', methods=['POST'])
    def create_public_appointment():
        """Crear una cita desde el formulario público"""
        try:
            data = request.get_json()
            
            required_fields = ['professional_id', 'specialty_id', 'date', 'time', 'patient']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Campo requerido: {field}'}), 400
            
            patient_data = data['patient']
            required_patient_fields = ['name', 'email', 'phone', 'rut', 'birth_date']
            for field in required_patient_fields:
                if field not in patient_data:
                    return jsonify({'error': f'Campo requerido del paciente: {field}'}), 400
            
            professional = Professional.query.get(data['professional_id'])
            specialty = Specialty.query.get(data['specialty_id'])
            
            if not professional or not specialty:
                return jsonify({'error': 'Profesional o especialidad no encontrados'}), 404
            
            patient = Patient.query.filter_by(rut=patient_data['rut']).first()
            
            if patient:
                if patient.name != patient_data['name']:
                    patient.name = patient_data['name']
                
                if patient.email != patient_data['email']:
                    patient.email = patient_data['email']
                
                if patient.phone != patient_data['phone']:
                    patient.phone = patient_data['phone']
                
                new_birth_date = datetime.strptime(patient_data['birth_date'], '%Y-%m-%d').date()
                if patient.birth_date != new_birth_date:
                    patient.birth_date = new_birth_date
                
                db.session.flush()
                
            else:
                patient = Patient(
                    name=patient_data['name'],
                    email=patient_data['email'],
                    phone=patient_data['phone'],
                    rut=patient_data['rut'],
                    birth_date=datetime.strptime(patient_data['birth_date'], '%Y-%m-%d').date()
                )
                db.session.add(patient)
                db.session.flush()
            
            appointment_datetime = datetime.strptime(
                f"{data['date']} {data['time']}", 
                '%Y-%m-%d %H:%M'
            )
            
            # Calcular rango de 15 días antes y después
            date_min = appointment_datetime - timedelta(days=15)
            date_max = appointment_datetime + timedelta(days=15)
            
            # Buscar citas existentes del paciente en ese rango
            existing_recent_appointment = Appointment.query.filter(
                Appointment.patient_id == patient.id,
                Appointment.professional_id == data['professional_id'],
                Appointment.specialty_id == data['specialty_id'],
                Appointment.date >= date_min,
                Appointment.date <= date_max,
                Appointment.status.in_(['pending', 'confirmed'])
            ).first()
            
            if existing_recent_appointment:
                existing_date = existing_recent_appointment.date
                days_diff = abs((existing_date.date() - appointment_datetime.date()).days)
                
                return jsonify({
                    'error': f'Ya tienes una cita {("pendiente" if existing_recent_appointment.status == "pending" else "confirmada")} '
                             f'para el {existing_date.strftime("%d/%m/%Y a las %H:%M")}. '
                             f'Debe haber al menos 15 días entre citas.',
                    'existing_appointment': {
                        'id': existing_recent_appointment.id,
                        'date': existing_date.isoformat(),
                        'status': existing_recent_appointment.status
                    }
                }), 409
            
            # Verificar que el slot sigue disponible
            existing_slot = Appointment.query.filter_by(
                professional_id=data['professional_id'],
                date=appointment_datetime
            ).filter(
                Appointment.status.in_(['pending', 'confirmed'])
            ).first()
            
            if existing_slot:
                return jsonify({'error': 'Este horario ya no está disponible'}), 409
            
            appointment = Appointment(
                patient_id=patient.id,
                professional_id=data['professional_id'],
                specialty_id=data['specialty_id'],
                date=appointment_datetime,
                status='pending',
                notes=data.get('notes', '')
            )
            
            db.session.add(appointment)
            db.session.commit()
            
            return jsonify({
                'message': 'Cita creada exitosamente',
                'appointment_id': appointment.id,
                'patient_id': patient.id,
                'patient_name': patient.name
            }), 201
            
        except ValueError as e:
            db.session.rollback()
            return jsonify({'error': f'Formato de fecha inválido: {str(e)}'}), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
        
    @app.route('/api/public/center-info', methods=['GET'])
    def get_public_center_info():
        """Obtener información pública del centro"""
        try:
            from models.models import CenterConfig
            config = CenterConfig.query.first()
            
            if not config:
                return jsonify({
                    'name': 'Centro de Salud',
                    'address': '',
                    'phone': '',
                    'email': '',
                    'description': '',
                    'vision': ''
                }), 200
            
            return jsonify({
                'name': config.name,
                'address': config.address,
                'phone': config.phone,
                'email': config.email,
                'description': config.description,
                'vision': config.vision,
                'logo_url': config.logo_url
            }), 200
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500