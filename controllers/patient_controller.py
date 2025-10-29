from flask import jsonify, request
from models.models import db, Patient
from datetime import datetime

def get_patients():
    """Obtener todos los pacientes"""
    try:
        patients = Patient.query.filter_by(is_active=True).all()
        return jsonify([p.to_dict() for p in patients]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_patient(patient_id):
    """Obtener un paciente específico"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({"error": "Paciente no encontrado"}), 404
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_patient():
    """Crear un nuevo paciente"""
    try:
        data = request.get_json()
        
        # Validaciones
        if not data.get('name') or not data.get('email') or not data.get('phone'):
            return jsonify({"error": "Nombre, email y teléfono son requeridos"}), 400
        
        # Verificar si el email ya existe
        if Patient.query.filter_by(email=data['email']).first():
            return jsonify({"error": "El email ya está registrado"}), 400
        
        # Verificar si el RUT ya existe (si viene)
        if data.get('rut') and Patient.query.filter_by(rut=data['rut']).first():
            return jsonify({"error": "El RUT ya está registrado"}), 400
        
        # Crear paciente
        patient = Patient(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            rut=data.get('rut'),
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data.get('birth_date') else None,
            address=data.get('address'),
            emergency_contact=data.get('emergency_contact'),
            emergency_phone=data.get('emergency_phone'),
            notes=data.get('notes')
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify(patient.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def update_patient(patient_id):
    """Actualizar un paciente"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({"error": "Paciente no encontrado"}), 404
        
        data = request.get_json()
        
        # Actualizar campos
        if 'name' in data:
            patient.name = data['name']
        if 'email' in data:
            existing = Patient.query.filter_by(email=data['email']).first()
            if existing and existing.id != patient_id:
                return jsonify({"error": "El email ya está en uso"}), 400
            patient.email = data['email']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'rut' in data:
            existing = Patient.query.filter_by(rut=data['rut']).first()
            if existing and existing.id != patient_id:
                return jsonify({"error": "El RUT ya está en uso"}), 400
            patient.rut = data['rut']
        if 'birth_date' in data:
            patient.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        if 'address' in data:
            patient.address = data['address']
        if 'emergency_contact' in data:
            patient.emergency_contact = data['emergency_contact']
        if 'emergency_phone' in data:
            patient.emergency_phone = data['emergency_phone']
        if 'notes' in data:
            patient.notes = data['notes']
        
        db.session.commit()
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def delete_patient(patient_id):
    """Eliminar (desactivar) un paciente"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({"error": "Paciente no encontrado"}), 404
        
        # Soft delete
        patient.is_active = False
        db.session.commit()
        
        return jsonify({"message": "Paciente eliminado"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def search_patients():
    """Buscar pacientes por nombre, email o RUT"""
    try:
        query = request.args.get('q', '')
        
        patients = Patient.query.filter(
            db.or_(
                Patient.name.ilike(f'%{query}%'),
                Patient.email.ilike(f'%{query}%'),
                Patient.rut.ilike(f'%{query}%')
            ),
            Patient.is_active == True
        ).all()
        
        return jsonify([p.to_dict() for p in patients]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500