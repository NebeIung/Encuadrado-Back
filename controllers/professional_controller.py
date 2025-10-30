from flask import jsonify, request
from models.models import db, Professional, Specialty
from werkzeug.security import generate_password_hash
import traceback

def get_professionals():
    """Obtener todos los profesionales"""
    try:
        professionals = Professional.query.all()
        return jsonify([prof.to_dict() for prof in professionals]), 200
    except Exception as e:
        print(f"Error getting professionals: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def get_professional(professional_id):
    """Obtener un profesional específico"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        return jsonify(professional.to_dict()), 200
    except Exception as e:
        print(f"Error getting professional: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def create_professional():
    """Crear un nuevo profesional"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo requerido: {field}"}), 400
        
        # Verificar si el email ya existe
        if Professional.query.filter_by(email=data['email']).first():
            return jsonify({"error": "El email ya está registrado"}), 400
        
        professional = Professional(
            name=data['name'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role=data.get('role', 'member'),
            schedule=data.get('schedule', {})
        )
        
        db.session.add(professional)
        db.session.commit()
        
        return jsonify(professional.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        print(f"Error creating professional: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def update_professional(professional_id):
    """Actualizar un profesional"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            professional.name = data['name']
        if 'email' in data:
            # Verificar que el email no esté en uso por otro profesional
            existing = Professional.query.filter_by(email=data['email']).first()
            if existing and existing.id != professional_id:
                return jsonify({"error": "El email ya está registrado"}), 400
            professional.email = data['email']
        if 'password' in data:
            professional.password_hash = generate_password_hash(data['password'])
        if 'role' in data:
            professional.role = data['role']
        if 'schedule' in data:
            professional.schedule = data['schedule']
        
        db.session.commit()
        return jsonify(professional.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating professional: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def delete_professional(professional_id):
    """Eliminar un profesional"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        # Verificar si tiene citas asociadas
        if professional.appointments:
            return jsonify({"error": "No se puede eliminar un profesional con citas asociadas"}), 400
        
        db.session.delete(professional)
        db.session.commit()
        
        return jsonify({"message": "Profesional eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting professional: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def assign_specialties(professional_id):
    """Asignar especialidades a un profesional"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        data = request.get_json()
        specialty_ids = data.get('specialty_ids', [])
        
        # Limpiar especialidades actuales
        professional.specialties = []
        
        # Asignar nuevas especialidades
        for specialty_id in specialty_ids:
            specialty = Specialty.query.get(specialty_id)
            if specialty:
                professional.specialties.append(specialty)
        
        db.session.commit()
        return jsonify(professional.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error assigning specialties: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def update_professional_schedule(professional_id):
    """Actualizar horario de un profesional"""
    try:
        professional = Professional.query.get(professional_id)
        if not professional:
            return jsonify({"error": "Profesional no encontrado"}), 404
        
        data = request.get_json()
        schedule = data.get('schedule')
        
        if not schedule:
            return jsonify({"error": "Falta el horario"}), 400
        
        professional.schedule = schedule
        db.session.commit()
        
        return jsonify(professional.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error updating schedule: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500