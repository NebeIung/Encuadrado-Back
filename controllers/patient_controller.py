from flask import jsonify, request
from models.models import db, Patient
from datetime import datetime
import traceback

def get_patients():
    """Obtener todos los pacientes"""
    try:
        patients = Patient.query.all()
        return jsonify([patient.to_dict() for patient in patients]), 200
    except Exception as e:
        print(f"Error getting patients: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def get_patient(patient_id):
    """Obtener un paciente específico"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({"error": "Paciente no encontrado"}), 404
        return jsonify(patient.to_dict()), 200
    except Exception as e:
        print(f"Error getting patient: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def create_patient():
    """Crear un nuevo paciente"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'phone', 'rut', 'birth_date']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido: {field}"}), 400
        
        # Verificar si el email o RUT ya existen
        if Patient.query.filter_by(email=data['email']).first():
            return jsonify({"error": "El email ya está registrado"}), 400
        
        if Patient.query.filter_by(rut=data['rut']).first():
            return jsonify({"error": "El RUT ya está registrado"}), 400
        
        # Convertir birth_date string a datetime
        birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        
        patient = Patient(
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            rut=data['rut'],
            birth_date=birth_date
        )
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify(patient.to_dict()), 201
    except ValueError as ve:
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error creating patient: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def update_patient(patient_id):
    """Actualizar un paciente"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({"error": "Paciente no encontrado"}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            patient.name = data['name']
        if 'email' in data:
            # Verificar que el email no esté en uso por otro paciente
            existing = Patient.query.filter_by(email=data['email']).first()
            if existing and existing.id != patient_id:
                return jsonify({"error": "El email ya está registrado"}), 400
            patient.email = data['email']
        if 'phone' in data:
            patient.phone = data['phone']
        if 'rut' in data:
            # Verificar que el RUT no esté en uso por otro paciente
            existing = Patient.query.filter_by(rut=data['rut']).first()
            if existing and existing.id != patient_id:
                return jsonify({"error": "El RUT ya está registrado"}), 400
            patient.rut = data['rut']
        if 'birth_date' in data:
            patient.birth_date = datetime.strptime(data['birth_date'], '%Y-%m-%d').date()
        
        db.session.commit()
        return jsonify(patient.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error updating patient: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def delete_patient(patient_id):
    """Eliminar un paciente"""
    try:
        patient = Patient.query.get(patient_id)
        if not patient:
            return jsonify({"error": "Paciente no encontrado"}), 404
        
        # Verificar si tiene citas asociadas
        if patient.appointments:
            return jsonify({"error": "No se puede eliminar un paciente con citas asociadas"}), 400
        
        db.session.delete(patient)
        db.session.commit()
        
        return jsonify({"message": "Paciente eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting patient: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def search_patients():
    """Buscar pacientes por nombre, email o RUT"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify([]), 200
        
        patients = Patient.query.filter(
            db.or_(
                Patient.name.ilike(f'%{query}%'),
                Patient.email.ilike(f'%{query}%'),
                Patient.rut.ilike(f'%{query}%')
            )
        ).all()
        
        return jsonify([patient.to_dict() for patient in patients]), 200
    except Exception as e:
        print(f"Error searching patients: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500